from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class WarehousePosition(Base):
    __tablename__ = "warehouse_positions"

    id = Column(Integer, primary_key=True, index=True)

    rack = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
    column = Column(Integer, nullable=False)
    position_code = Column(String(20), unique=True, nullable=False, index=True)

    max_width_cm = Column(Numeric(8, 2), nullable=True)
    max_height_cm = Column(Numeric(8, 2), nullable=True)
    max_depth_cm = Column(Numeric(8, 2), nullable=True)
    max_weight_kg = Column(Numeric(8, 3), nullable=True)

    suggested_abc_zone = Column(String(1), nullable=True)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    is_occupied = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", back_populates="positions")

    def __repr__(self):
        return f"<WarehousePosition code={self.position_code} occupied={self.is_occupied}>"