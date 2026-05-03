from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class SalesUpload(Base):
    __tablename__ = "sales_uploads"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)

    # pending → processing → completed → failed
    status = Column(String(20), default="pending", nullable=False, index=True)
    error_message = Column(Text, nullable=True)

    total_skus = Column(Integer, nullable=True)
    skus_zone_a = Column(Integer, nullable=True)
    skus_zone_b = Column(Integer, nullable=True)
    skus_zone_c = Column(Integer, nullable=True)
    skus_with_errors = Column(Integer, nullable=True)

    cleansing_report = Column(JSON, nullable=True)
    relocation_suggestions = Column(JSON, nullable=True)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<SalesUpload id={self.id} file={self.filename} status={self.status}>"