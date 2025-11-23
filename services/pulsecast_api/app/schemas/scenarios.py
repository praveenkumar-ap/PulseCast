from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

class ScenarioLedgerEvent(BaseModel):
    ledger_id: UUID
    scenario_id: UUID
    version_seq: int
    action_type: str
    actor: str
    actor_role: Optional[str] = None
    assumptions: Optional[str] = None
    comments: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScenarioLedgerEventCreate(BaseModel):
    action_type: str
    actor: str
    actor_role: Optional[str] = None
    assumptions: Optional[str] = None
    comments: Optional[str] = None


class ScenarioLedgerListResponse(BaseModel):
    events: List[ScenarioLedgerEvent]


class ScenarioResultItem(BaseModel):
    sku_id: str
    year_month: str
    base_run_id: Optional[str]
    p10: float
    p50: float
    p90: float
    created_at: str


class ScenarioHeaderModel(BaseModel):
    scenario_id: UUID
    name: str
    description: Optional[str]
    status: str
    base_run_id: Optional[str]
    uplift_percent: Optional[float]
    created_by: str
    created_at: str
    updated_at: str


class ScenarioDetailResponse(BaseModel):
    header: ScenarioHeaderModel
    results: List[ScenarioResultItem]


class CreateScenarioRequest(BaseModel):
    name: str
    description: Optional[str] = None
    created_by: str
    base_run_id: Optional[str] = None
    sku_ids: Optional[List[str]] = None  # None or empty => all SKUs
    from_month: str  # "YYYY-MM"
    to_month: str  # "YYYY-MM"
    uplift_percent: float = Field(..., description="e.g. 15.0 for +15%")


class CreateScenarioResponse(BaseModel):
    scenario_id: UUID
    name: str
    status: str
    base_run_id: str
    uplift_percent: float
    from_month: str
    to_month: str
    sku_ids: List[str]
    total_rows: int


class ScenarioSummary(BaseModel):
    scenario_id: UUID
    name: str
    status: str
    base_run_id: Optional[str]
    uplift_percent: Optional[float]
    created_by: str
    created_at: str
    updated_at: str


class ScenarioListResponse(BaseModel):
    scenarios: List[ScenarioSummary]
