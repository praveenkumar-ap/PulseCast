from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ForecastRunSummary(BaseModel):
    run_id: str
    run_type: Optional[str] = None
    horizon_start_month: Optional[datetime] = None
    horizon_end_month: Optional[datetime] = None
    skus_covered: Optional[int] = None
    mape: Optional[float] = None
    wape: Optional[float] = None
    bias: Optional[float] = None
    mae: Optional[float] = None
    mape_vs_baseline_delta: Optional[float] = None
    wape_vs_baseline_delta: Optional[float] = None
    computed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ForecastAccuracyItem(BaseModel):
    run_id: str
    sku_id: str
    year_month: str
    actual_units: Optional[float] = None
    forecast_p50_units: Optional[float] = None
    abs_error: Optional[float] = None
    ape: Optional[float] = None

    class Config:
        from_attributes = True


class ValueImpactSummary(BaseModel):
    run_id: str
    rev_uplift_estimate: Optional[float] = None
    scrap_avoidance_estimate: Optional[float] = None
    wc_savings_estimate: Optional[float] = None
    productivity_savings_estimate: Optional[float] = None
    assumptions_json: Optional[str] = None
    computed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ForecastRunsListResponse(BaseModel):
    runs: List[ForecastRunSummary]


class ForecastRunDetailResponse(BaseModel):
    run: ForecastRunSummary
    value_impact: Optional[ValueImpactSummary] = None


class ForecastAccuracyListResponse(BaseModel):
    items: List[ForecastAccuracyItem]


class ValueImpactListResponse(BaseModel):
    items: List[ValueImpactSummary]
