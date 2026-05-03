from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.product import Product
from app.models.warehouse_position import WarehousePosition


def assign_positions(db: Session) -> dict:
    # 1. Liberar todas las posiciones con SQL directo
    db.execute(text("UPDATE warehouse_positions SET product_id = NULL, is_occupied = FALSE"))
    db.commit()

    # 2. Verificar cuántas posiciones libres hay por zona
    zonas = ['A', 'B', 'C']
    for z in zonas:
        count = db.query(WarehousePosition).filter(
            WarehousePosition.suggested_abc_zone == z,
            WarehousePosition.is_active == True,
        ).count()
        print(f"Posiciones zona {z}: {count}")

    # 3. Obtener productos ordenados por zona y porcentaje
    productos = (
        db.query(Product)
        .filter(Product.abc_zone.isnot(None), Product.is_active == True)
        .order_by(Product.abc_zone.asc(), Product.abc_percentage.asc())
        .all()
    )

    asignados = 0
    sin_espacio = []

    for producto in productos:
        zona = producto.abc_zone

        # Buscar posición libre de la zona correcta
        posicion = (
            db.query(WarehousePosition)
            .filter(
                WarehousePosition.suggested_abc_zone == zona,
                WarehousePosition.is_occupied == False,
                WarehousePosition.is_active == True,
            )
            .first()
        )

        # Si no hay posición en su zona, buscar cualquier posición libre
        if not posicion:
            posicion = (
                db.query(WarehousePosition)
                .filter(
                    WarehousePosition.is_occupied == False,
                    WarehousePosition.is_active == True,
                )
                .first()
            )

        if posicion:
            posicion.product_id = producto.id
            posicion.is_occupied = True
            db.flush()
            asignados += 1
        else:
            sin_espacio.append(producto.sku)

    db.commit()

    return {
        "asignados": asignados,
        "sin_espacio": sin_espacio,
        "total_productos": len(productos),
    }