from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
import app.models  # noqa: F401
from app.routers import uploads, products, inventory
from app.services.seed_positions import seed_warehouse_positions
from sqlalchemy.orm import Session
from app.core.database import get_db

app = FastAPI(
    title="ReOrdena-ABC API",
    description="Motor de clasificación ABC para optimización logística de bodega",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(uploads.router) 
app.include_router(products.router)
app.include_router(inventory.router)

@app.get("/health", tags=["Sistema"])
def health_check():
    return {
        "status": "ok",
        "service": "ReOrdena-ABC",
        "version": "0.1.0",
    }
    
@app.post("/admin/seed-positions", tags=["Admin"])
def seed_positions(db: Session = Depends(get_db)):
    return seed_warehouse_positions(db)

@app.post("/admin/reset-positions", tags=["Admin"])
def reset_positions(db: Session = Depends(get_db)):
    from app.models.warehouse_position import WarehousePosition
    db.query(WarehousePosition).update({
        "product_id": None,
        "is_occupied": False,
    })
    db.commit()
    return {"mensaje": "Todas las posiciones liberadas"}