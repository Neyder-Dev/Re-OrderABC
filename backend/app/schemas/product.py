from pydantic import BaseModel
from typing import Optional


class ProductoEnMapa(BaseModel):
    id: int
    sku: str
    name: str
    abc_zone: Optional[str]
    abc_percentage: Optional[float]
    position_code: Optional[str]
    rack: Optional[int]
    level: Optional[int]
    column: Optional[int]

    class Config:
        from_attributes = True


class MapaResponse(BaseModel):
    total_productos: int
    asignados: int
    productos: list[ProductoEnMapa]