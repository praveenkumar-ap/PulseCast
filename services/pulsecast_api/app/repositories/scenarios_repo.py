from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models.forecasts import Forecast
from ..models.scenarios import (
    ALLOWED_STATUSES,
    STATUS_ACTIVE,
    ScenarioHeader,
    ScenarioResult,
)
from ..schemas.scenarios import CreateScenarioRequest

logger = logging.getLogger(__name__)

UPLIFT_MIN = -100.0
UPLIFT_MAX = 300.0


def _parse_month(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m")
    except ValueError as exc:
        raise ValueError(f"Invalid month format: {value}") from exc


def resolve_base_run_id(db: Session, explicit_run_id: Optional[str]) -> str:
    """
    If explicit_run_id provided, verify it exists. Otherwise select latest run_id by created_at.
    """
    if explicit_run_id:
        stmt = select(Forecast.run_id).where(Forecast.run_id == explicit_run_id).limit(1)
        run = db.execute(stmt).scalar_one_or_none()
        if run is None:
            raise ValueError(f"base_run_id {explicit_run_id} not found in forecasts")
        logger.info("Using provided base_run_id=%s", explicit_run_id)
        return explicit_run_id

    stmt = (
        select(Forecast.run_id)
        .order_by(Forecast.created_at.desc())
        .limit(1)
    )
    run = db.execute(stmt).scalar_one_or_none()
    if run is None:
        raise ValueError("No forecasts available to derive base_run_id")
    logger.info("Resolved base_run_id=%s (latest by created_at)", run)
    return run


def fetch_base_forecasts(
    db: Session,
    run_id: str,
    sku_ids: Optional[List[str]],
    from_month: str,
    to_month: str,
) -> List[Forecast]:
    """Fetch base forecasts filtered by run_id, SKUs, and month range."""
    from_dt = _parse_month(from_month).date()
    to_dt = _parse_month(to_month).date()

    conditions = [Forecast.run_id == run_id, Forecast.year_month >= from_dt, Forecast.year_month <= to_dt]
    if sku_ids:
        conditions.append(Forecast.sku_id.in_(sku_ids))

    stmt = select(Forecast).where(and_(*conditions)).order_by(Forecast.year_month.asc())
    rows = list(db.execute(stmt).scalars())
    logger.info("Fetched %s base forecasts for run_id=%s", len(rows), run_id)
    return rows


def create_uplift_scenario(
    db: Session,
    req: CreateScenarioRequest,
) -> tuple[ScenarioHeader, List[ScenarioResult]]:
    """Create an uplift scenario and persist header/results."""
    if req.uplift_percent < UPLIFT_MIN or req.uplift_percent > UPLIFT_MAX:
        raise ValueError(f"uplift_percent must be between {UPLIFT_MIN} and {UPLIFT_MAX}")

    if req.sku_ids is not None and len(req.sku_ids) == 0:
        req.sku_ids = None

    scenario_id = uuid4()
    now = datetime.utcnow()

    try:
        base_run_id = resolve_base_run_id(db, req.base_run_id)
        base_forecasts = fetch_base_forecasts(db, base_run_id, req.sku_ids, req.from_month, req.to_month)
        if not base_forecasts:
            raise ValueError("No base forecasts found for given criteria")

        factor = 1.0 + req.uplift_percent / 100.0

        header = ScenarioHeader(
            scenario_id=scenario_id,
            name=req.name,
            description=req.description,
            status=STATUS_ACTIVE,
            base_run_id=base_run_id,
            uplift_percent=req.uplift_percent,
            created_by=req.created_by,
            created_at=now,
            updated_at=now,
        )
        db.add(header)

        results: List[ScenarioResult] = []
        for bf in base_forecasts:
            p10 = max(0.0, float(bf.p10) * factor) if bf.p10 is not None else 0.0
            p50 = max(0.0, float(bf.p50) * factor) if bf.p50 is not None else 0.0
            p90 = max(0.0, float(bf.p90) * factor) if bf.p90 is not None else 0.0
            res = ScenarioResult(
                scenario_id=scenario_id,
                sku_id=bf.sku_id,
                year_month=bf.year_month,
                base_run_id=bf.run_id,
                p10=p10,
                p50=p50,
                p90=p90,
                created_at=now,
            )
            results.append(res)
        db.add_all(results)
        db.commit()
        logger.info("Created scenario %s with %s rows", scenario_id, len(results))
        return header, results
    except ValueError:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("DB error creating scenario", exc_info=exc)
        raise
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        logger.error("Unexpected error creating scenario", exc_info=exc)
        raise


def list_scenarios(db: Session, status: Optional[str], limit: int) -> List[ScenarioHeader]:
    """List scenarios ordered by created_at desc with optional status filter."""
    requested_limit = max(1, min(limit, 100))
    stmt = select(ScenarioHeader).order_by(ScenarioHeader.created_at.desc()).limit(requested_limit)
    if status:
        if status not in ALLOWED_STATUSES:
            raise ValueError("Invalid status filter")
        stmt = stmt.where(ScenarioHeader.status == status)
    try:
        return list(db.execute(stmt).scalars())
    except SQLAlchemyError as exc:
        logger.error("DB error listing scenarios", exc_info=exc)
        raise


def get_scenario_with_results(
    db: Session,
    scenario_id: UUID,
) -> tuple[Optional[ScenarioHeader], List[ScenarioResult]]:
    """Return header and results for a scenario."""
    header_stmt = select(ScenarioHeader).where(ScenarioHeader.scenario_id == scenario_id)
    results_stmt = (
        select(ScenarioResult)
        .where(ScenarioResult.scenario_id == scenario_id)
        .order_by(ScenarioResult.sku_id.asc(), ScenarioResult.year_month.asc())
    )
    try:
        header = db.execute(header_stmt).scalar_one_or_none()
        results = list(db.execute(results_stmt).scalars())
        return header, results
    except SQLAlchemyError as exc:
        logger.error("DB error fetching scenario %s", scenario_id, exc_info=exc)
        raise
