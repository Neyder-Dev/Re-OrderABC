from sqlalchemy.orm import Session
from app.models.warehouse_position import WarehousePosition


def seed_warehouse_positions(db: Session) -> dict:
    """
    Genera las 384 posiciones de la bodega con sus coordenadas.
    Solo crea las posiciones si la tabla está vacía.
    """

    # Si ya hay posiciones no hacer nada
    existing = db.query(WarehousePosition).count()
    if existing > 0:
        return {"mensaje": f"Ya existen {existing} posiciones en la bodega"}

    posiciones = []

    # ─── RACKS ───────────────────────────────────────────────
    # 3 racks × 3 niveles
    # Nivel 3 = Piso  → Zona A (27 posiciones)
    # Nivel 2 = Medio → Zona B (27 posiciones)
    # Nivel 1 = Techo → Zona C (26 posiciones)

    nivel_config = {
        3: {"label": "Piso",  "zona": "A", "columnas": 27},
        2: {"label": "Medio", "zona": "B", "columnas": 27},
        1: {"label": "Techo", "zona": "C", "columnas": 26},
    }

    for rack in range(1, 4):  # Rack 1, 2, 3
        for nivel, config in nivel_config.items():
            for columna in range(1, config["columnas"] + 1):
                code = f"R{rack}-N{nivel}-C{columna}"
                posiciones.append(
                    WarehousePosition(
                        rack=rack,
                        level=nivel,
                        column=columna,
                        position_code=code,
                        suggested_abc_zone=config["zona"],
                        # Dimensiones del rack (iguales en todos los niveles)
                        max_width_cm=120,
                        max_height_cm=150,
                        max_depth_cm=140,
                        max_weight_kg=1500,
                        is_occupied=False,
                        is_active=True,
                    )
                )

    # ─── ISLAS ───────────────────────────────────────────────
    # 9 islas × 16 posiciones = 144 posiciones
    # Todas en zona A (piso, sin restricción de altura)

    for isla in range(1, 10):  # Isla 1 → 9
        for pos in range(1, 17):  # Posición 1 → 16
            code = f"I{isla}-P{pos}"
            posiciones.append(
                WarehousePosition(
                    rack=0,        # 0 = isla (no es rack)
                    level=0,       # 0 = piso sin nivel
                    column=pos,
                    position_code=code,
                    suggested_abc_zone="A",
                    # Islas sin restricción de altura
                    max_width_cm=120,
                    max_height_cm=None,
                    max_depth_cm=140,
                    max_weight_kg=None,
                    is_occupied=False,
                    is_active=True,
                )
            )

    # Insertar todo en la DB
    db.bulk_save_objects(posiciones)
    db.commit()

    total = len(posiciones)
    rack_count = total - 144
    return {
        "mensaje": f"{total} posiciones creadas exitosamente",
        "racks": rack_count,
        "islas": 144,
        "total": total,
    }