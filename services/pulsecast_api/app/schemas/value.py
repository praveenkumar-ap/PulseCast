from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class RunValueSummary(BaseModel):
    run_id: str
    run_type: Optional[str] = None
    family_id: Optional[str] = None
    family_name: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    forecast_accuracy_uplift_pct: Optional[float] = None
    revenue_uplift_estimate: Optional[float] = None
    scrap_avoidance_estimate: Optional[float] = None
    working_capital_savings_estimate: Optional[float] = None
    planner_productivity_hours_saved: Optional[float] = None
    total_value_estimate: Optional[float] = None
    case_label: Optional[str] = None
    computed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScenarioValueSummary(BaseModel):
    # DB returns UUID for scenario_id; keep UUID here to avoid validation errors.
    scenario_id: UUID
    scenario_name: Optional[str] = None
    base_run_id: Optional[str] = None
    status: Optional[str] = None
    family_id: Optional[str] = None
    family_name: Optional[str] = None
    expected_revenue_uplift_estimate: Optional[float] = None
    expected_scrap_avoidance_estimate: Optional[float] = None
    expected_working_capital_effect: Optional[float] = None
    expected_service_level_change: Optional[float] = None
    total_expected_value_estimate: Optional[float] = None
    case_label: Optional[str] = None
    rec_count: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BenchmarkMetric(BaseModel):
    metric_name: str
    scope: str
    scope_key: Optional[str] = None
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    as_of_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class RunValueSummaryResponse(BaseModel):
    run: RunValueSummary


class RunValueSummaryListResponse(BaseModel):
    runs: List[RunValueSummary]


class ScenarioValueSummaryResponse(BaseModel):
    scenario: ScenarioValueSummary


class ScenarioValueSummaryListResponse(BaseModel):
    scenarios: List[ScenarioValueSummary]


class BenchmarksResponse(BaseModel):
    benchmarks: List[BenchmarkMetric]
