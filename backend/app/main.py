from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
import app.models  # noqa: F401
from app.routers import uploads  # ← agregar

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

app.include_router(uploads.router)  # ← agregar antes del @app.get("/health")

@app.get("/health", tags=["Sistema"])
def health_check():
    return {
        "status": "ok",
        "service": "ReOrdena-ABC",
        "version": "0.1.0",
    }