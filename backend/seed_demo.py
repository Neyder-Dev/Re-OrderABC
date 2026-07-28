"""
Script de datos demo para entorno de prueba universitario.
Genera productos ficticios para demostración del sistema ReOrdena-ABC.
No contiene datos reales de ninguna empresa.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.warehouse_position import WarehousePosition
from app.models.sales_upload import SalesUpload
from app.core.security import hash_password
from app.services.seed_positions import seed_warehouse_positions
from app.services.position_assigner import assign_positions
from sqlalchemy import text


def run_seed():
    db = SessionLocal()

    try:
        print("🔄 Iniciando seed de datos demo...")

        # Limpiar datos existentes
        db.execute(text("DELETE FROM warehouse_positions"))
        db.execute(text("DELETE FROM products"))
        db.execute(text("DELETE FROM sales_uploads"))
        db.execute(text("DELETE FROM users"))
        db.commit()
        print("✅ Base de datos limpia")

        # Crear usuarios demo
        usuarios = [
            User(
                nombre="Administrador",
                email="admin@demo.com",
                hashed_password=hash_password("Demo2024"),
                rol="jefe",
            ),
            User(
                nombre="Operario Bodega",
                email="operario@demo.com",
                hashed_password=hash_password("Demo2024"),
                rol="operario",
            ),
        ]
        for u in usuarios:
            db.add(u)
        db.commit()
        print("✅ Usuarios demo creados")

        # Productos ficticios con clasificación ABC
        productos_demo = [
            # Zona A
            ("PROD-001", "Proteína Concentrada Premium BS 25",     "A", 72.25),
            ("PROD-002", "Caseína Micelar Instantánea BS 20",      "A", 78.20),
            ("PROD-003", "Dextrosa Monohidratada Industrial BS 25", "A", 79.95),
            # Zona B
            ("PROD-004", "Proteína Suero Concentrado 80% BS 20",   "B", 81.48),
            ("PROD-005", "Emulsificante Industrial IST 1000",       "B", 82.57),
            ("PROD-006", "Colágeno Hidrolizado BT 15",             "B", 83.64),
            ("PROD-007", "Dextrosa Importada BS 25",               "B", 84.67),
            ("PROD-008", "Péptidos Colágeno Aglomerado BS 25",     "B", 85.66),
            ("PROD-009", "Agente Fluidizante IBC 850",             "B", 86.50),
            ("PROD-010", "Agente Fluidizante Especial IBC 850",    "B", 87.30),
            ("PROD-011", "Gelatina 280 Bloom BT 25",               "B", 87.97),
            ("PROD-012", "Lubricante Industrial BS 25",            "B", 88.57),
            ("PROD-013", "Creatina Monohidratada CJ 25",           "B", 89.17),
            ("PROD-014", "Almidón Modificado BT 25",               "B", 89.76),
            ("PROD-015", "Proteína Concentrado Suero BS 20",       "B", 90.35),
            ("PROD-016", "Gelatina 250 Malla 7 BT 20",            "B", 90.90),
            ("PROD-017", "Plastificante Drum 180kg",               "B", 91.44),
            ("PROD-018", "Goma Agrirapid BS 25",                   "B", 91.98),
            ("PROD-019", "Lubricante Especial Drum 200kg",         "B", 92.51),
            ("PROD-020", "Lecitina Premium IBC 1000",              "B", 93.03),
            ("PROD-021", "Plastificante Avanzado 205kg",           "B", 93.47),
            ("PROD-022", "Almidón de Papa Refinado BT 25",         "B", 93.90),
            ("PROD-023", "Goma Arábiga Premium BT 25",             "B", 94.33),
            ("PROD-024", "Copos de Papa Deshidratada BS 20",       "B", 94.71),
            # Zona C
            ("PROD-025", "Fosfato Cálcico BS 25",                  "C", 95.03),
            ("PROD-026", "Emulsificante Especial IST 1000",        "C", 95.35),
            ("PROD-027", "Lubricante Avanzado BT 25",              "C", 95.63),
            ("PROD-028", "Agente Proceso IBC 900",                 "C", 95.91),
            ("PROD-029", "Proteína Arveja CJ 9",                   "C", 96.17),
            ("PROD-030", "Suplemento Premium CJ 10",               "C", 96.43),
            ("PROD-031", "Pigmento Industrial BS 1",               "C", 96.65),
            ("PROD-032", "Proteína Texturizada BT 4",              "C", 96.87),
            ("PROD-033", "Lubricante Premium Drum 180kg",          "C", 97.08),
            ("PROD-034", "Dextrosa Monohidratada BS 25",           "C", 97.30),
            ("PROD-035", "Fibra Soluble Premium BS 25",            "C", 97.51),
            ("PROD-036", "Lecitina Industrial TB 200",             "C", 97.70),
            ("PROD-037", "Agente Deslizante BT 25",                "C", 97.86),
            ("PROD-038", "Emulsificante Base BT 25",               "C", 98.02),
            ("PROD-039", "Vitamina K2 Microencapsulada BS 1",      "C", 98.14),
            ("PROD-040", "Inmunomodulador CJ 10",                  "C", 98.25),
        ]

        for sku, name, zona, pct in productos_demo:
            p = Product(
                sku=sku,
                name=name,
                abc_zone=zona,
                abc_percentage=pct,
                is_active=True,
            )
            db.add(p)

        db.commit()
        print(f"✅ {len(productos_demo)} productos demo creados")

        # Generar las 384 posiciones de bodega
        resultado_pos = seed_warehouse_positions(db)
        print(f"✅ {resultado_pos.get('total', 384)} posiciones generadas")

        # Asignar posiciones según zona ABC
        resultado_asig = assign_positions(db)
        print(f"✅ {resultado_asig['asignados']} posiciones asignadas")

        print()
        print("─" * 45)
        print("  CREDENCIALES DEMO")
        print("─" * 45)
        print("  Jefe:     admin@demo.com    / Demo2024")
        print("  Operario: operario@demo.com / Demo2024")
        print("─" * 45)

    except Exception as e:
        print(f"❌ Error en seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()