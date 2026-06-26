from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import io
import logging

from app.core.security import require_jefe
from app.core.database import get_db
from app.models.sales_upload import SalesUpload
from app.models.product import Product
from app.services.cleansing import clean_matr780
from app.services.abc_engine import run_abc
from app.schemas.upload import UploadResponse

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

router = APIRouter(prefix="/uploads", tags=["Carga de Archivos"])


@router.post("/matr780", response_model=UploadResponse, dependencies=[Depends(require_jefe)])
async def upload_matr780(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Solo se aceptan archivos Excel (.xlsx o .xls)"
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"El archivo supera el límite de {MAX_FILE_SIZE_MB} MB"
        )

    upload = SalesUpload(
        filename=file.filename,
        file_size_bytes=len(file_bytes),
        status="processing",
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)

    try:
        df_clean, cleansing_report = clean_matr780(io.BytesIO(file_bytes))
        df_abc, summary = run_abc(df_clean)

        for _, row in df_abc.iterrows():
            product = db.query(Product).filter(Product.sku == row["sku"]).first()

            if product:
                product.abc_zone       = row["zona_abc"]
                product.abc_percentage = float(row["pct_acumulado"])
                product.updated_at     = datetime.utcnow()
            else:
                product = Product(
                    sku=row["sku"],
                    name=row["descripcion"],
                    abc_zone=row["zona_abc"],
                    abc_percentage=float(row["pct_acumulado"]),
                )
                db.add(product)

        db.commit()

        zonas = {z["zona_abc"]: z for z in summary["zonas"]}
        upload.status           = "completed"
        upload.total_skus       = summary["total_skus"]
        upload.skus_zone_a      = zonas.get("A", {}).get("skus", 0)
        upload.skus_zone_b      = zonas.get("B", {}).get("skus", 0)
        upload.skus_zone_c      = zonas.get("C", {}).get("skus", 0)
        upload.skus_with_errors = cleansing_report["filas_sin_cantidad"]
        upload.cleansing_report = cleansing_report
        upload.processed_at     = datetime.utcnow()
        db.commit()
        db.refresh(upload)

    except ValueError as e:
        upload.status = "failed"
        db.commit()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Error procesando MATR780 '%s': %s", file.filename, e, exc_info=True)
        upload.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=500,
            detail="Error interno al procesar el archivo. Verifica que el formato sea correcto."
        )

    return upload
