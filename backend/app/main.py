from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.core.security import require_jefe
from app.routers import uploads, products, inventory, auth
import app.models  # noqa: F401

app = FastAPI(
    title="ReOrdena-ABC API",
    description="Motor de clasificación ABC para optimización logística de bodega",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(uploads.router)
app.include_router(products.router)
app.include_router(inventory.router)


@app.get("/health", tags=["Sistema"])
def health_check(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status, "service": "ReOrdena-ABC", "version": "0.1.0"}


@app.post("/admin/seed-positions", tags=["Admin"], dependencies=[Depends(require_jefe)])
def seed_positions(db: Session = Depends(get_db)):
    from app.services.seed_positions import seed_warehouse_positions
    return seed_warehouse_positions(db)


@app.post("/admin/reset-positions", tags=["Admin"], dependencies=[Depends(require_jefe)])
def reset_positions(db: Session = Depends(get_db)):
    from app.models.warehouse_position import WarehousePosition
    from sqlalchemy import text
    db.execute(text("UPDATE warehouse_positions SET product_id = NULL, is_occupied = FALSE"))
    db.commit()
    return {"mensaje": "Todas las posiciones liberadas"}