from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product
from app.models.warehouse_position import WarehousePosition
from app.services.position_assigner import assign_positions
from app.schemas.product import MapaResponse, ProductoEnMapa

router = APIRouter(prefix="/products", tags=["Productos"])


@router.post("/assign-positions", response_model=dict)
def asignar_posiciones(db: Session = Depends(get_db)):
    """
    Asigna automáticamente cada producto a una posición según su zona ABC.
    """
    return assign_positions(db)


@router.get("/mapa", response_model=MapaResponse)
def get_mapa(db: Session = Depends(get_db)):
    """
    Retorna todos los productos con su posición asignada.
    """
    # Traer posiciones ocupadas con su producto
    posiciones = (
        db.query(WarehousePosition, Product)
        .join(Product, WarehousePosition.product_id == Product.id)
        .filter(WarehousePosition.is_occupied == True)
        .all()
    )

    # Traer productos sin posición
    productos_con_posicion_ids = [p.id for _, p in posiciones]
    sin_posicion = (
        db.query(Product)
        .filter(
            Product.abc_zone.isnot(None),
            Product.id.notin_(productos_con_posicion_ids)
        )
        .all()
    )

    productos = []

    # Productos con posición
    for position, product in posiciones:
        productos.append(
            ProductoEnMapa(
                id=product.id,
                sku=product.sku,
                name=product.name,
                abc_zone=product.abc_zone,
                abc_percentage=float(product.abc_percentage or 0),
                position_code=position.position_code,
                rack=position.rack,
                level=position.level,
                column=position.column,
            )
        )

    # Productos sin posición
    for product in sin_posicion:
        productos.append(
            ProductoEnMapa(
                id=product.id,
                sku=product.sku,
                name=product.name,
                abc_zone=product.abc_zone,
                abc_percentage=float(product.abc_percentage or 0),
                position_code=None,
                rack=None,
                level=None,
                column=None,
            )
        )

    asignados = len(posiciones)

    return MapaResponse(
        total_productos=len(productos),
        asignados=asignados,
        productos=productos,
    )


@router.put("/reasignar/{producto_id}/{position_code}", response_model=dict)
def reasignar_producto(
    producto_id: int,
    position_code: str,
    db: Session = Depends(get_db),
):
    """
    Permite al operario mover un producto a una posición diferente.
    """
    # Buscar posición destino
    nueva_pos = (
        db.query(WarehousePosition)
        .filter(WarehousePosition.position_code == position_code)
        .first()
    )
    if not nueva_pos:
        return {"error": f"Posición {position_code} no existe"}

    if nueva_pos.is_occupied and nueva_pos.product_id != producto_id:
        return {"error": f"Posición {position_code} ya está ocupada"}

    # Liberar posición actual del producto
    pos_actual = (
        db.query(WarehousePosition)
        .filter(WarehousePosition.product_id == producto_id)
        .first()
    )
    if pos_actual:
        pos_actual.product_id = None
        pos_actual.is_occupied = False

    # Asignar nueva posición
    nueva_pos.product_id = producto_id
    nueva_pos.is_occupied = True
    db.commit()

    return {
        "mensaje": f"Producto movido a {position_code}",
        "position_code": position_code,
    }