import logging
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.rbac import require_roles
from ..repositories import value_repo
from ..schemas.value import (
    BenchmarksResponse,
    BenchmarkMetric,
    RunValueSummary,
    RunValueSummaryListResponse,
    RunValueSummaryResponse,
    ScenarioValueSummary,
    ScenarioValueSummaryListResponse,
    ScenarioValueSummaryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/value",
    tags=["value"],
    dependencies=[Depends(require_roles("PLANNER", "SOP_APPROVER", "DATA_SCIENTIST", "ADMIN"))],
)


def _run_to_dict(row: RunValueSummary) -> dict:
    data = {
        "run_id": row.run_id,
        "run_type": row.run_type,
        "family_id": row.family_id,
        "family_name": row.family_name,
        "period_start": row.period_start,
        "period_end": row.period_end,
        "forecast_accuracy_uplift_pct": row.forecast_accuracy_uplift_pct,
        "revenue_uplift_estimate": row.revenue_uplift_estimate,
        "scrap_avoidance_estimate": row.scrap_avoidance_estimate,
        "working_capital_savings_estimate": row.working_capital_savings_estimate,
        "planner_productivity_hours_saved": row.planner_productivity_hours_saved,
        "total_value_estimate": row.total_value_estimate,
        "case_label": row.case_label,
        "computed_at": row.computed_at,
    }
    # If total_value_estimate is missing, derive a conservative sum of available components.
    if data["total_value_estimate"] is None:
        parts = [
            data["revenue_uplift_estimate"],
            data["scrap_avoidance_estimate"],
            data["working_capital_savings_estimate"],
        ]
        total = sum(float(p) for p in parts if p is not None)
        data["total_value_estimate"] = total if parts else None
    return data


def _scenario_to_dict(row: ScenarioValueSummary) -> dict:
    data = {
        "scenario_id": row.scenario_id,
        "scenario_name": row.scenario_name,
        "base_run_id": row.base_run_id,
        "status": row.status,
        "family_id": row.family_id,
        "family_name": row.family_name,
        "expected_revenue_uplift_estimate": row.expected_revenue_uplift_estimate,
        "expected_scrap_avoidance_estimate": row.expected_scrap_avoidance_estimate,
        "expected_working_capital_effect": row.expected_working_capital_effect,
        "expected_service_level_change": row.expected_service_level_change,
        "total_expected_value_estimate": row.total_expected_value_estimate,
        "case_label": row.case_label,
        "rec_count": row.rec_count,
        "created_at": row.created_at,
    }
    if data["total_expected_value_estimate"] is None:
        parts = [
            data["expected_revenue_uplift_estimate"],
            data["expected_scrap_avoidance_estimate"],
            data["expected_working_capital_effect"],
        ]
        total = sum(float(p) for p in parts if p is not None)
        data["total_expected_value_estimate"] = total if parts else None
    return data


@router.get("/runs/{run_id}", response_model=RunValueSummaryResponse)
def get_run_value(run_id: str, db: Session = Depends(get_db)) -> RunValueSummaryResponse:
    try:
        row = value_repo.get_run_value_summary(db, run_id)
    except SQLAlchemyError as exc:
        logger.error("DB error fetching run value %s", run_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    if row is None:
        raise HTTPException(status_code=404, detail="Run value summary not found")
    return RunValueSummaryResponse(run=RunValueSummary.model_validate(_run_to_dict(row)))


@router.get("/runs", response_model=RunValueSummaryListResponse)
def list_run_values(
    family_id: Optional[str] = Query(default=None),
    case_label: Optional[str] = Query(default=None),
    run_type: Optional[str] = Query(default=None),
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
    limit: int = Query(default=100),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
) -> RunValueSummaryListResponse:
    try:
        rows = value_repo.list_run_value_summaries(db, family_id, case_label, run_type, from_date, to_date, limit, offset)
    except SQLAlchemyError as exc:
        logger.error("DB error listing run values", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    return RunValueSummaryListResponse(runs=[RunValueSummary.model_validate(_run_to_dict(r)) for r in rows])


@router.get("/scenarios/{scenario_id}", response_model=ScenarioValueSummaryResponse)
def get_scenario_value(scenario_id: str, db: Session = Depends(get_db)) -> ScenarioValueSummaryResponse:
    try:
        row = value_repo.get_scenario_value_summary(db, scenario_id)
    except SQLAlchemyError as exc:
        logger.error("DB error fetching scenario value %s", scenario_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    if row is None:
        raise HTTPException(status_code=404, detail="Scenario value summary not found")
    return ScenarioValueSummaryResponse(scenario=ScenarioValueSummary.model_validate(_scenario_to_dict(row)))


@router.get("/scenarios", response_model=ScenarioValueSummaryListResponse)
def list_scenario_values(
    family_id: Optional[str] = Query(default=None),
    case_label: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    from_date: Optional[datetime] = Query(default=None),
    to_date: Optional[datetime] = Query(default=None),
    limit: int = Query(default=100),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
) -> ScenarioValueSummaryListResponse:
    try:
        rows = value_repo.list_scenario_value_summaries(db, family_id, case_label, status, from_date, to_date, limit, offset)
    except SQLAlchemyError as exc:
        logger.error("DB error listing scenario values", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    return ScenarioValueSummaryListResponse(
        scenarios=[ScenarioValueSummary.model_validate(_scenario_to_dict(r)) for r in rows]
    )


@router.get("/benchmarks", response_model=BenchmarksResponse)
def get_benchmarks(
    scope: Optional[str] = Query(default=None),
    scope_key: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
) -> BenchmarksResponse:
    try:
        rows = value_repo.list_benchmarks(db, scope, scope_key)
    except SQLAlchemyError as exc:
        logger.error("DB error listing benchmarks", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    return BenchmarksResponse(benchmarks=[BenchmarkMetric.model_validate(r) for r in rows])
