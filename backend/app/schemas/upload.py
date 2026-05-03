from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UploadResponse(BaseModel):
    id: int
    filename: str
    status: str
    total_skus: Optional[int]
    skus_zone_a: Optional[int]
    skus_zone_b: Optional[int]
    skus_zone_c: Optional[int]
    skus_with_errors: Optional[int]
    cleansing_report: Optional[dict]
    uploaded_at: datetime

    class Config:
        from_attributes = True