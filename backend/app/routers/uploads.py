from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import io

from app.core.database import get_db
from app.models.sales_upload import SalesUpload
from app.models.product import Product
from app.services.cleansing import clean_matr780
from app.services.abc_engine import run_abc
from app.schemas.upload import UploadResponse

router = APIRouter(prefix="/uploads", tags=["Carga de Archivos"])


@router.post("/matr780", response_model=UploadResponse)
async def upload_matr780(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Validar extensión
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Solo se aceptan archivos Excel (.xlsx o .xls)"
        )

    # Leer bytes
    file_bytes = await file.read()

    # Registrar el upload en DB
    upload = SalesUpload(
        filename=file.filename,
        file_size_bytes=len(file_bytes),
        status="processing",
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)

    try:
        # 1. Limpieza
        df_clean, cleansing_report = clean_matr780(io.BytesIO(file_bytes))

        # 2. Algoritmo ABC
        df_abc, summary = run_abc(df_clean)

        # 3. Actualizar/crear productos en DB
        for _, row in df_abc.iterrows():
            product = db.query(Product).filter(
                Product.sku == row["sku"]
            ).first()

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

        # 4. Actualizar el registro del upload
        zonas = {z["zona_abc"]: z for z in summary["zonas"]}
        upload.status            = "completed"
        upload.total_skus        = summary["total_skus"]
        upload.skus_zone_a       = zonas.get("A", {}).get("skus", 0)
        upload.skus_zone_b       = zonas.get("B", {}).get("skus", 0)
        upload.skus_zone_c       = zonas.get("C", {}).get("skus", 0)
        upload.skus_with_errors  = cleansing_report["filas_sin_cantidad"]
        upload.cleansing_report  = cleansing_report
        upload.processed_at      = datetime.utcnow()
        db.commit()
        db.refresh(upload)

    except Exception as e:
        upload.status        = "failed"
        upload.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

    return upload