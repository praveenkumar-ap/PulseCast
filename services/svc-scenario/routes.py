import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import get_session
from models import (
    ALLOWED_STATUSES,
    STATUS_ACTIVE,
    ScenarioHeader,
    ScenarioResult,
)
from schemas import (
    ScenarioCreateRequest,
    ScenarioCreateResponse,
    ScenarioDetailResponse,
    ScenarioHeaderSchema,
    ScenarioListResponse,
    ScenarioResultSchema,
)

logger = logging.getLogger(__name__)
router = APIRouter()

DEFAULT_LIST_LIMIT = 20
MAX_LIST_LIMIT = 100
UPLIFT_MIN = -100.0
UPLIFT_MAX = 300.0


@router.get("/health")
def health() -> dict:
    """Health check endpoint."""
    try:
        return {"status": "ok", "service": "svc-scenario"}
    except Exception as exc:  # noqa: BLE001
        logger.error("Health check failed", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


def _parse_month(value: str, field_name: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m")
    except ValueError as exc:
        logger.warning("Invalid %s format: %s", field_name, value)
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}, expected YYYY-MM") from exc


def _validate_uplift(uplift: float) -> None:
    if uplift < UPLIFT_MIN or uplift > UPLIFT_MAX:
        logger.warning("Invalid uplift_percent: %s", uplift)
        raise HTTPException(
            status_code=400,
            detail=f"uplift_percent must be between {UPLIFT_MIN} and {UPLIFT_MAX}",
        )


def _resolve_base_run_id(db: Session, provided: Optional[str]) -> Optional[str]:
    if provided:
        return provided
    stmt = text(
        """
        select run_id
        from analytics.sku_forecasts
        order by created_at desc
        limit 1
        """
    )
    result = db.execute(stmt).scalar_one_or_none()
    return result


def _fetch_base_forecasts(
    db: Session,
    base_run_id: Optional[str],
    sku_ids: Optional[List[str]],
    from_dt: datetime,
    to_dt: datetime,
) -> List[dict]:
    conditions = ["year_month >= :from_dt", "year_month <= :to_dt"]
    params = {"from_dt": from_dt.date(), "to_dt": to_dt.date()}
    if base_run_id:
        conditions.append("run_id = :run_id")
        params["run_id"] = base_run_id
    if sku_ids:
        conditions.append("sku_id = any(:sku_ids)")
        params["sku_ids"] = sku_ids

    where_clause = " AND ".join(conditions)
    query = text(
        f"""
        select sku_id, year_month, p10, p50, p90, run_id
        from analytics.sku_forecasts
        where {where_clause}
        """
    )
    rows = db.execute(query, params).mappings().all()
    return [dict(r) for r in rows]


def _apply_uplift(row: dict, uplift_percent: float) -> dict:
    factor = 1.0 + uplift_percent / 100.0
    def _adj(value):
        return max(0.0, float(value) * factor)
    return {
        "sku_id": row["sku_id"],
        "year_month": row["year_month"],
        "base_run_id": row.get("run_id"),
        "p10": _adj(row["p10"]),
        "p50": _adj(row["p50"]),
        "p90": _adj(row["p90"]),
    }


@router.post("/scenarios", response_model=ScenarioCreateResponse)
def create_scenario(
    payload: ScenarioCreateRequest,
    db: Session = Depends(get_session),
) -> ScenarioCreateResponse:
    """Create a scenario by applying uplift to base forecasts."""
    logger.info(
        "Creating scenario name=%s base_run_id=%s uplift=%s sku_ids=%s range=%s-%s",
        payload.name,
        payload.base_run_id,
        payload.uplift_percent,
        payload.sku_ids,
        payload.from_month,
        payload.to_month,
    )

    _validate_uplift(payload.uplift_percent)
    from_dt = _parse_month(payload.from_month, "from_month")
    to_dt = _parse_month(payload.to_month, "to_month")
    if from_dt > to_dt:
        logger.warning("from_month after to_month")
        raise HTTPException(status_code=400, detail="from_month cannot be after to_month")

    if payload.sku_ids is not None and len(payload.sku_ids) == 0:
        payload.sku_ids = None

    scenario_id = uuid4()
    now = datetime.now(timezone.utc)

    try:
        base_run_id = _resolve_base_run_id(db, payload.base_run_id)
        forecasts = _fetch_base_forecasts(db, base_run_id, payload.sku_ids, from_dt, to_dt)
        if not forecasts:
            logger.warning("No base forecasts found for scenario creation")
            raise HTTPException(status_code=400, detail="No base forecasts found for given criteria")

        adjusted = [_apply_uplift(row, payload.uplift_percent) for row in forecasts]

        header = ScenarioHeader(
            scenario_id=scenario_id,
            name=payload.name,
            description=payload.description,
            status=STATUS_ACTIVE,
            base_run_id=base_run_id,
            uplift_percent=payload.uplift_percent,
            created_by=payload.created_by,
            created_at=now,
            updated_at=now,
        )

        db.add(header)

        result_rows = []
        for row in adjusted:
            result_rows.append(
                ScenarioResult(
                    scenario_id=scenario_id,
                    sku_id=row["sku_id"],
                    year_month=row["year_month"],
                    base_run_id=row["base_run_id"],
                    p10=row["p10"],
                    p50=row["p50"],
                    p90=row["p90"],
                    created_at=now,
                )
            )
        db.add_all(result_rows)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to create scenario", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        logger.error("Unexpected error creating scenario", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    logger.info("Scenario %s created with %s rows", scenario_id, len(adjusted))
    return ScenarioCreateResponse(
        scenario_id=scenario_id,
        name=payload.name,
        status=STATUS_ACTIVE,
        base_run_id=base_run_id,
        uplift_percent=payload.uplift_percent,
        total_rows=len(adjusted),
        from_month=payload.from_month,
        to_month=payload.to_month,
        sku_ids=payload.sku_ids,
    )


@router.get("/scenarios", response_model=ScenarioListResponse)
def list_scenarios(
    status: Optional[str] = Query(default=None, description="Filter by status"),
    limit: int = Query(default=DEFAULT_LIST_LIMIT, description="Max rows to return"),
    db: Session = Depends(get_session),
) -> ScenarioListResponse:
    """List scenarios with optional status filter."""
    if status and status not in ALLOWED_STATUSES:
        logger.warning("Invalid status filter: %s", status)
        raise HTTPException(status_code=400, detail="Invalid status filter")

    safe_limit = min(limit, MAX_LIST_LIMIT)
    stmt = select(ScenarioHeader).order_by(ScenarioHeader.created_at.desc()).limit(safe_limit)
    if status:
        stmt = stmt.where(ScenarioHeader.status == status)

    try:
        rows: List[ScenarioHeader] = list(db.execute(stmt).scalars())
    except SQLAlchemyError as exc:
        logger.error("Failed to list scenarios", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    return ScenarioListResponse(
        scenarios=[ScenarioHeaderSchema.model_validate(r) for r in rows]
    )


@router.get("/scenarios/{scenario_id}", response_model=ScenarioDetailResponse)
def get_scenario(
    scenario_id: str,
    db: Session = Depends(get_session),
) -> ScenarioDetailResponse:
    """Fetch scenario header and results."""
    try:
        scenario_uuid = UUID(scenario_id)
    except ValueError as exc:
        logger.warning("Invalid scenario_id: %s", scenario_id)
        raise HTTPException(status_code=400, detail="Invalid scenario_id") from exc

    header_stmt = select(ScenarioHeader).where(ScenarioHeader.scenario_id == scenario_uuid)
    results_stmt = (
        select(ScenarioResult)
        .where(ScenarioResult.scenario_id == scenario_uuid)
        .order_by(ScenarioResult.sku_id.asc(), ScenarioResult.year_month.asc())
    )

    try:
        header = db.execute(header_stmt).scalar_one_or_none()
        if header is None:
            raise HTTPException(status_code=404, detail="Scenario not found")
        results: List[ScenarioResult] = list(db.execute(results_stmt).scalars())
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error("Failed to fetch scenario %s", scenario_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    return ScenarioDetailResponse(
        header=ScenarioHeaderSchema.model_validate(header),
        results=[ScenarioResultSchema.model_validate(r) for r in results],
    )
