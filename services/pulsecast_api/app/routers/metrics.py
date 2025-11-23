import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.rbac import require_roles
from ..repositories.metrics_repo import (
    get_accuracy_for_run,
    get_run_summary,
    get_value_impact_for_run,
    get_value_impact_for_runs,
    list_forecast_runs,
)
from ..schemas.metrics import (
    ForecastAccuracyItem,
    ForecastAccuracyListResponse,
    ForecastRunDetailResponse,
    ForecastRunsListResponse,
    ForecastRunSummary,
    ValueImpactListResponse,
    ValueImpactSummary,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
    dependencies=[Depends(require_roles("PLANNER", "SOP_APPROVER", "DATA_SCIENTIST", "ADMIN"))],
)


def _parse_dt(value: Optional[str], field_name: str) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}, expected ISO datetime") from exc


@router.get("/runs", response_model=ForecastRunsListResponse)
def list_runs(
    run_type: Optional[str] = Query(default=None),
    computed_from: Optional[str] = Query(default=None),
    computed_to: Optional[str] = Query(default=None),
    limit: int = Query(default=100),
    db: Session = Depends(get_db),
) -> ForecastRunsListResponse:
    try:
        runs = list_forecast_runs(
            db,
            run_type=run_type,
            computed_from=_parse_dt(computed_from, "computed_from"),
            computed_to=_parse_dt(computed_to, "computed_to"),
            limit=limit,
        )
    except SQLAlchemyError as exc:
        logger.error("DB error listing forecast runs", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    response_runs = []
    for r in runs:
        response_runs.append(
            ForecastRunSummary(
                run_id=r.run_id,
                run_type=r.run_type,
                horizon_start_month=r.horizon_start_month,
                horizon_end_month=r.horizon_end_month,
                skus_covered=r.skus_covered,
                mape=float(r.mape) if r.mape is not None else None,
                wape=float(r.wape) if r.wape is not None else None,
                bias=float(r.bias) if r.bias is not None else None,
                mae=float(r.mae) if r.mae is not None else None,
                mape_vs_baseline_delta=float(r.mape_vs_baseline_delta) if r.mape_vs_baseline_delta is not None else None,
                wape_vs_baseline_delta=float(r.wape_vs_baseline_delta) if r.wape_vs_baseline_delta is not None else None,
                computed_at=r.computed_at,
            )
        )
    return ForecastRunsListResponse(runs=response_runs)


@router.get("/runs/{run_id}", response_model=ForecastRunDetailResponse)
def run_detail(run_id: str, db: Session = Depends(get_db)) -> ForecastRunDetailResponse:
    try:
        run = get_run_summary(db, run_id)
    except SQLAlchemyError as exc:
        logger.error("DB error fetching run %s", run_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    try:
        value = get_value_impact_for_run(db, run_id)
    except SQLAlchemyError as exc:
        logger.error("DB error fetching value impact for run %s", run_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    run_schema = ForecastRunSummary(
        run_id=run.run_id,
        run_type=run.run_type,
        horizon_start_month=run.horizon_start_month,
        horizon_end_month=run.horizon_end_month,
        skus_covered=run.skus_covered,
        mape=float(run.mape) if run.mape is not None else None,
        wape=float(run.wape) if run.wape is not None else None,
        bias=float(run.bias) if run.bias is not None else None,
        mae=float(run.mae) if run.mae is not None else None,
        mape_vs_baseline_delta=float(run.mape_vs_baseline_delta) if run.mape_vs_baseline_delta is not None else None,
        wape_vs_baseline_delta=float(run.wape_vs_baseline_delta) if run.wape_vs_baseline_delta is not None else None,
        computed_at=run.computed_at,
    )

    value_schema = (
        ValueImpactSummary(
            run_id=value.run_id,
            rev_uplift_estimate=float(value.rev_uplift_estimate) if value.rev_uplift_estimate is not None else None,
            scrap_avoidance_estimate=float(value.scrap_avoidance_estimate) if value.scrap_avoidance_estimate is not None else None,
            wc_savings_estimate=float(value.wc_savings_estimate) if value.wc_savings_estimate is not None else None,
            productivity_savings_estimate=float(value.productivity_savings_estimate) if value.productivity_savings_estimate is not None else None,
            assumptions_json=value.assumptions_json,
            computed_at=value.computed_at,
        )
        if value
        else None
    )

    return ForecastRunDetailResponse(run=run_schema, value_impact=value_schema)


@router.get("/runs/{run_id}/accuracy", response_model=ForecastAccuracyListResponse)
def run_accuracy(
    run_id: str,
    sku_id: Optional[str] = Query(default=None),
    from_month: Optional[str] = Query(default=None),
    to_month: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
) -> ForecastAccuracyListResponse:
    def _parse_month(val: Optional[str], name: str) -> Optional[datetime]:
        if val is None:
            return None
        try:
            return datetime.strptime(val, "%Y-%m")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid {name}, expected YYYY-MM") from exc

    try:
        rows = get_accuracy_for_run(
            db,
            run_id=run_id,
            sku_id=sku_id,
            family=None,
            from_month=_parse_month(from_month, "from_month"),
            to_month=_parse_month(to_month, "to_month"),
        )
    except SQLAlchemyError as exc:
        logger.error("DB error fetching accuracy for run %s", run_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    items = [
        ForecastAccuracyItem(
            run_id=r.run_id,
            sku_id=r.sku_id,
            year_month=r.year_month.strftime("%Y-%m"),
            actual_units=float(r.actual_units) if r.actual_units is not None else None,
            forecast_p50_units=float(r.forecast_p50_units) if r.forecast_p50_units is not None else None,
            abs_error=float(r.abs_error) if r.abs_error is not None else None,
            ape=float(r.ape) if r.ape is not None else None,
        )
        for r in rows
    ]
    return ForecastAccuracyListResponse(items=items)


@router.get("/value_impact", response_model=ValueImpactListResponse)
def value_impact(
    run_id: Optional[List[str]] = Query(default=None),
    computed_from: Optional[str] = Query(default=None),
    computed_to: Optional[str] = Query(default=None),
    limit: int = Query(default=100),
    db: Session = Depends(get_db),
) -> ValueImpactListResponse:
    try:
        rows = get_value_impact_for_runs(
            db,
            run_ids=run_id,
            computed_from=_parse_dt(computed_from, "computed_from"),
            computed_to=_parse_dt(computed_to, "computed_to"),
            limit=limit,
        )
    except SQLAlchemyError as exc:
        logger.error("DB error listing value impact", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    items = [ValueImpactSummary.model_validate(r) for r in rows]
    return ValueImpactListResponse(items=items)
