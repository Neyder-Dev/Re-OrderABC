from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    supplier = Column(String(150), nullable=True)

    width_cm = Column(Numeric(8, 2), nullable=True)
    height_cm = Column(Numeric(8, 2), nullable=True)
    depth_cm = Column(Numeric(8, 2), nullable=True)
    weight_kg = Column(Numeric(8, 3), nullable=True)

    abc_zone = Column(String(1), nullable=True)        # 'A', 'B' o 'C'
    abc_percentage = Column(Numeric(10, 4), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    positions = relationship("WarehousePosition", back_populates="product")

    def __repr__(self):
        return f"<Product sku={self.sku} zone={self.abc_zone}>"