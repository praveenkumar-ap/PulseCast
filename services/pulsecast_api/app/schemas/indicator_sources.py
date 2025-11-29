from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class IndicatorSourceSchema(BaseModel):
    id: UUID
    code: str
    name: str
    provider_type: str
    status: str
    config: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IndicatorSeriesRowSchema(BaseModel):
    id: UUID
    source_id: UUID
    source_code: str
    indicator_code: str
    geo_key: str
    as_of_date: date
    value: float
    extra_meta: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IndicatorSourcesResponse(BaseModel):
    sources: list[IndicatorSourceSchema]


class IndicatorSeriesResponse(BaseModel):
    series: list[IndicatorSeriesRowSchema]
