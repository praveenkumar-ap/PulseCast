from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RunOptimizerRequest(BaseModel):
    source_type: str  # BASE_RUN or SCENARIO
    source_id: Optional[str] = None
    sku_ids: Optional[List[str]] = None
    from_month: str
    to_month: str
    service_level_target: Optional[float] = Field(
        default=None, description="Override service level; otherwise use params/default."
    )


class RecommendationItem(BaseModel):
    policy_id: UUID
    sku_id: str
    location_id: Optional[str]
    year_month: str
    source_type: str
    source_id: Optional[str]
    service_level_target: Optional[float]
    safety_stock_units: Optional[float]
    cycle_stock_units: Optional[float]
    target_stock_units: Optional[float]
    created_at: str


class RunOptimizerResponse(BaseModel):
    source_type: str
    source_id: str
    from_month: str
    to_month: str
    total_policies: int
    recommendations: List[RecommendationItem]


class ListRecommendationsResponse(BaseModel):
    recommendations: List[RecommendationItem]
