from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import io

from app.core.database import get_db
from app.models.product import Product
from app.models.warehouse_position import WarehousePosition
from app.services.inventory_cleansing import clean_matr425
from app.services.position_assigner import assign_positions

router = APIRouter(prefix="/inventory", tags=["Inventario"])


@router.post("/upload-stock", response_model=dict)
async def upload_stock(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Recibe el MATR425 (saldos por lote) y asigna posiciones
    solo a los productos que tienen stock en bodega hoy.
    """
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Solo se aceptan archivos Excel (.xlsx o .xls)"
        )

    file_bytes = await file.read()

    try:
        # 1. Limpiar el MATR425
        inventario, cleansing_report = clean_matr425(io.BytesIO(file_bytes))

        # 2. Marcar qué productos tienen stock hoy
        skus_en_bodega = set(inventario['sku'].tolist())

        # Desactivar todos primero
        db.execute(text("UPDATE products SET is_active = FALSE"))
        db.commit()

        # Activar solo los que tienen stock
        activados = 0
        for sku in skus_en_bodega:
            producto = db.query(Product).filter(
                Product.sku == sku
            ).first()
            if producto:
                producto.is_active = True
                activados += 1

        db.commit()

        # 3. Liberar posiciones y reasignar
        db.execute(text(
            "UPDATE warehouse_positions SET product_id = NULL, is_occupied = FALSE"
        ))
        db.commit()

        resultado = assign_positions(db)

        return {
            "cleansing_report": cleansing_report,
            "skus_en_bodega": cleansing_report["skus_en_bodega"],
            "skus_activados_en_sistema": activados,
            "skus_sin_clasificacion_abc": len(skus_en_bodega) - activados,
            "posiciones_asignadas": resultado["asignados"],
            "posiciones_sin_espacio": resultado["sin_espacio"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))