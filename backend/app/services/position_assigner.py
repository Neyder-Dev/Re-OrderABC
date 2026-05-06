from sqlalchemy.orm import Session
from sqlalchemy import text
from math import ceil
from app.models.product import Product
from app.models.warehouse_position import WarehousePosition


# Peso máximo por estiba según nivel
PESO_MAX_POR_NIVEL = {
    3: 1000,  # Piso
    2: 750,   # Medio
    1: 500,   # Techo
    0: 1000,  # Islas (mismo que piso)
}


def calcular_estibas(saldo_kg: float, nivel: int) -> int:
    """
    Calcula cuántas posiciones necesita un producto
    según su saldo en kg y el nivel donde se ubicará.
    """
    peso_max = PESO_MAX_POR_NIVEL.get(nivel, 1000)
    return max(1, ceil(saldo_kg / peso_max))


def assign_positions(db: Session, inventario_df=None) -> dict:
    """
    Asigna automáticamente productos a posiciones según su zona ABC.
    Si se provee inventario_df, calcula cuántas posiciones necesita
    cada producto según su saldo real en bodega.
    Zona A → piso en racks e islas (N3, nivel 0)
    Zona B → nivel medio en racks (N2)
    Zona C → techo en racks (N1)
    """

    # 1. Liberar todas las posiciones
    db.execute(text(
        "UPDATE warehouse_positions SET product_id = NULL, is_occupied = FALSE"
    ))
    db.commit()

    # 2. Construir mapa de saldos si se provee inventario
    saldo_por_sku = {}
    if inventario_df is not None:
        for _, row in inventario_df.iterrows():
            saldo_por_sku[row['sku']] = float(row['saldo_total'])

    # 3. Obtener productos activos con zona asignada
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
        saldo = saldo_por_sku.get(producto.sku, 0)

        # Determinar cuántas posiciones necesita
        # Usar nivel según zona para calcular estibas
        nivel_referencia = {'A': 3, 'B': 2, 'C': 1}.get(zona, 1)

        if saldo > 0:
            num_posiciones = calcular_estibas(saldo, nivel_referencia)
        else:
            num_posiciones = 1  # mínimo 1 posición

        # Asignar tantas posiciones como estibas necesite
        posiciones_asignadas = 0
        for _ in range(num_posiciones):
            posicion = (
                db.query(WarehousePosition)
                .filter(
                    WarehousePosition.suggested_abc_zone == zona,
                    WarehousePosition.is_occupied == False,
                    WarehousePosition.is_active == True,
                )
                .first()
            )

            # Si no hay en su zona, buscar cualquier posición libre
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
                posiciones_asignadas += 1
                asignados += 1
            else:
                sin_espacio.append(f"{producto.sku} (faltan {num_posiciones - posiciones_asignadas} pos.)")
                break

    db.commit()

    return {
        "asignados": asignados,
        "sin_espacio": sin_espacio,
        "total_productos": len(productos),
    }