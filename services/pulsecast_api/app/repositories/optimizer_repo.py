from __future__ import annotations

import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models.forecasts import Forecast
from ..models.inventory import InventoryParameter, InventoryRecommendation
from ..models.scenarios import ScenarioHeader, ScenarioResult
from ..schemas.optimizer import RunOptimizerRequest, RecommendationItem

logger = logging.getLogger(__name__)

SOURCE_BASE = "BASE_RUN"
SOURCE_SCENARIO = "SCENARIO"
ALLOWED_SOURCE_TYPES = {SOURCE_BASE, SOURCE_SCENARIO}

DEFAULT_SERVICE_LEVEL = 0.97
DEFAULT_LEAD_TIME_DAYS = 14
DEFAULT_REVIEW_PERIOD_DAYS = 30
MAX_FETCH = 5000
MAX_LIST = 1000


def _parse_month(value: str, field_name: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m").date()
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name}, expected YYYY-MM") from exc


def resolve_source_id(db: Session, source_type: str, source_id: Optional[str]) -> str:
    if source_type == SOURCE_BASE:
        if source_id:
            stmt = select(Forecast.run_id).where(Forecast.run_id == source_id).limit(1)
            found = db.execute(stmt).scalar_one_or_none()
            if not found:
                raise ValueError(f"base_run_id {source_id} not found")
            return source_id
        stmt = select(Forecast.run_id).order_by(Forecast.created_at.desc()).limit(1)
        run = db.execute(stmt).scalar_one_or_none()
        if not run:
            raise ValueError("No forecast runs available")
        return run
    if source_type == SOURCE_SCENARIO:
        if not source_id:
            raise ValueError("scenario_id must be provided for SCENARIO source")
        stmt = select(ScenarioHeader.scenario_id).where(ScenarioHeader.scenario_id == UUID(source_id)).limit(1)
        found = db.execute(stmt).scalar_one_or_none()
        if not found:
            raise ValueError(f"scenario_id {source_id} not found")
        return source_id
    raise ValueError("Invalid source_type")


def fetch_base_timeseries(
    db: Session,
    source_type: str,
    source_id: str,
    sku_ids: Optional[List[str]],
    from_month: date,
    to_month: date,
) -> List[Tuple[str, date, float, float, float]]:
    """Return list of (sku_id, year_month, p10, p50, p90) for base data."""
    if source_type == SOURCE_BASE:
        conditions = [
            Forecast.run_id == source_id,
            Forecast.year_month >= from_month,
            Forecast.year_month <= to_month,
        ]
        if sku_ids:
            conditions.append(Forecast.sku_id.in_(sku_ids))
        stmt = (
            select(Forecast.sku_id, Forecast.year_month, Forecast.p10, Forecast.p50, Forecast.p90)
            .where(and_(*conditions))
            .limit(MAX_FETCH)
        )
    else:
        conditions = [
            ScenarioResult.scenario_id == UUID(source_id),
            ScenarioResult.year_month >= from_month,
            ScenarioResult.year_month <= to_month,
        ]
        if sku_ids:
            conditions.append(ScenarioResult.sku_id.in_(sku_ids))
        stmt = (
            select(
                ScenarioResult.sku_id,
                ScenarioResult.year_month,
                ScenarioResult.p10,
                ScenarioResult.p50,
                ScenarioResult.p90,
            )
            .where(and_(*conditions))
            .limit(MAX_FETCH)
        )
    rows = list(db.execute(stmt))
    logger.info("Loaded %s base rows for source_type=%s source_id=%s", len(rows), source_type, source_id)
    return [(r[0], r[1], float(r[2] or 0), float(r[3] or 0), float(r[4] or 0)) for r in rows]


def fetch_parameters(db: Session, sku_id: str, location_id: Optional[str]) -> Tuple[float, int, int]:
    stmt = select(InventoryParameter).where(InventoryParameter.sku_id == sku_id)
    if location_id:
        stmt = stmt.where(
            (InventoryParameter.location_id == location_id) | (InventoryParameter.location_id.is_(None))
        )
    row = db.execute(stmt).scalar_one_or_none()
    service = float(row.service_level_target) if row and row.service_level_target is not None else DEFAULT_SERVICE_LEVEL
    lead_time = row.lead_time_days if row and row.lead_time_days is not None else DEFAULT_LEAD_TIME_DAYS
    review = row.review_period_days if row and row.review_period_days is not None else DEFAULT_REVIEW_PERIOD_DAYS
    return service, lead_time, review


def _compute_cycle_stock(p50: float, review_period_days: int) -> float:
    horizon_months = max(review_period_days / 30.0, 0)
    return max(0.0, p50 * horizon_months)


def _compute_safety_stock(p10: float, p90: float, service_level: float, lead_time_days: int) -> float:
    spread = max(0.0, p90 - p10)
    service_factor = max(service_level, 0.0)
    lt_factor = max(lead_time_days / 30.0, 0.0) ** 0.5
    return max(0.0, spread * service_factor * lt_factor)


def compute_recommendations(
    base_rows: List[Tuple[str, date, float, float, float]],
    req: RunOptimizerRequest,
    resolved_source_id: str,
    db: Session,
) -> List[InventoryRecommendation]:
    recs: List[InventoryRecommendation] = []
    now = datetime.utcnow()
    for sku_id, ym, p10, p50, p90 in base_rows:
        service, lead_time, review_period = fetch_parameters(db, sku_id, None)
        if req.service_level_target is not None:
            service = req.service_level_target
        cycle_stock = _compute_cycle_stock(p50, review_period)
        safety_stock = _compute_safety_stock(p10, p90, service, lead_time)
        total = cycle_stock + safety_stock
        recs.append(
            InventoryRecommendation(
                policy_id=uuid4(),
                sku_id=sku_id,
                location_id=None,
                year_month=ym,
                source_type=req.source_type,
                source_id=resolved_source_id,
                service_level_target=service,
                safety_stock_units=safety_stock,
                cycle_stock_units=cycle_stock,
                target_stock_units=total,
                created_at=now,
            )
        )
    return recs


def persist_recommendations(db: Session, recs: List[InventoryRecommendation]) -> int:
    if not recs:
        return 0
    try:
        db.add_all(recs)
        db.commit()
        return len(recs)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to persist recommendations", exc_info=exc)
        raise


def run_optimizer(db: Session, req: RunOptimizerRequest) -> Tuple[str, List[InventoryRecommendation]]:
    if req.source_type not in ALLOWED_SOURCE_TYPES:
        raise ValueError("Invalid source_type")
    if req.sku_ids is not None and len(req.sku_ids) == 0:
        req.sku_ids = None

    from_dt = _parse_month(req.from_month, "from_month")
    to_dt = _parse_month(req.to_month, "to_month")
    if from_dt > to_dt:
        raise ValueError("from_month cannot be after to_month")

    resolved_source = resolve_source_id(db, req.source_type, req.source_id)
    base_rows = fetch_base_timeseries(db, req.source_type, resolved_source, req.sku_ids, from_dt, to_dt)
    if not base_rows:
        raise ValueError("No base data found for given criteria")

    recs = compute_recommendations(base_rows, req, resolved_source, db)
    created = persist_recommendations(db, recs)
    logger.info("Optimizer created %s recommendations for source %s", created, resolved_source)
    return resolved_source, recs


def list_recommendations(
    db: Session,
    sku_id: Optional[str],
    source_type: Optional[str],
    source_id: Optional[str],
    from_month: Optional[str],
    to_month: Optional[str],
    limit: int,
) -> List[InventoryRecommendation]:
    safe_limit = min(max(limit, 1), MAX_LIST)
    stmt = select(InventoryRecommendation).limit(safe_limit)
    conditions = []
    if sku_id:
        conditions.append(InventoryRecommendation.sku_id == sku_id)
    if source_type:
        conditions.append(InventoryRecommendation.source_type == source_type)
    if source_id:
        conditions.append(InventoryRecommendation.source_id == source_id)
    if from_month:
        conditions.append(InventoryRecommendation.year_month >= _parse_month(from_month, "from_month"))
    if to_month:
        conditions.append(InventoryRecommendation.year_month <= _parse_month(to_month, "to_month"))
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.order_by(InventoryRecommendation.created_at.desc())
    try:
        return list(db.execute(stmt).scalars())
    except SQLAlchemyError as exc:
        logger.error("Failed to list recommendations", exc_info=exc)
        raise
