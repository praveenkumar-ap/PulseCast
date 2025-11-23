from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class ScenarioCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    created_by: str
    base_run_id: Optional[str] = None
    sku_ids: Optional[List[str]] = None
    from_month: str
    to_month: str
    uplift_percent: float

    @validator("name")
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v

    @validator("created_by")
    def validate_created_by(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("created_by must not be empty")
        return v


class ScenarioHeaderSchema(BaseModel):
    scenario_id: UUID
    name: str
    description: Optional[str] = None
    status: str
    base_run_id: Optional[str] = None
    uplift_percent: Optional[float] = None
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScenarioResultSchema(BaseModel):
    scenario_id: UUID
    sku_id: str
    year_month: datetime
    base_run_id: Optional[str] = None
    p10: float
    p50: float
    p90: float
    created_at: datetime

    class Config:
        from_attributes = True


class ScenarioCreateResponse(BaseModel):
    scenario_id: UUID
    name: str
    status: str
    base_run_id: Optional[str] = None
    uplift_percent: float
    total_rows: int
    from_month: str
    to_month: str
    sku_ids: Optional[List[str]] = None


class ScenarioListResponse(BaseModel):
    scenarios: List[ScenarioHeaderSchema]


class ScenarioDetailResponse(BaseModel):
    header: ScenarioHeaderSchema
    results: List[ScenarioResultSchema]
