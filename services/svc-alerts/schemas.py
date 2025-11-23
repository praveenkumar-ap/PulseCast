from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AlertSchema(BaseModel):
    alert_id: UUID
    indicator_id: Optional[str] = None
    sku_id: Optional[str] = None
    geo_id: Optional[str] = None
    alert_type: str
    severity: str
    status: str
    message: Optional[str] = None
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    alerts: List[AlertSchema]


class AckRequest(BaseModel):
    actor: str = Field(..., description="Identifier of person/system acknowledging the alert.")
    note: Optional[str] = Field(default=None, description="Optional acknowledgment note.")
