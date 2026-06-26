from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import io
import logging

from app.core.database import get_db
from app.models.product import Product
from app.models.warehouse_position import WarehousePosition
from app.services.inventory_cleansing import clean_matr425
from app.services.position_assigner import assign_positions
from app.core.security import require_jefe

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

router = APIRouter(prefix="/inventory", tags=["Inventario"])


@router.post("/upload-stock", response_model=dict, dependencies=[Depends(require_jefe)])
async def upload_stock(
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

    try:
        inventario, cleansing_report = clean_matr425(io.BytesIO(file_bytes))

        skus_en_bodega = set(inventario['sku'].tolist())

        db.execute(text("UPDATE products SET is_active = FALSE"))
        db.commit()

        activados = 0
        for sku in skus_en_bodega:
            producto = db.query(Product).filter(Product.sku == sku).first()
            if producto:
                producto.is_active = True
                activados += 1

        db.commit()

        db.execute(text(
            "UPDATE warehouse_positions SET product_id = NULL, is_occupied = FALSE"
        ))
        db.commit()

        resultado = assign_positions(db, inventario_df=inventario)

        return {
            "cleansing_report": cleansing_report,
            "skus_en_bodega": cleansing_report["skus_en_bodega"],
            "skus_activados_en_sistema": activados,
            "skus_sin_clasificacion_abc": len(skus_en_bodega) - activados,
            "posiciones_asignadas": resultado["asignados"],
            "posiciones_sin_espacio": resultado["sin_espacio"],
        }

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Error procesando MATR425 '%s': %s", file.filename, e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al procesar el archivo. Verifica que el formato sea correcto."
        )
