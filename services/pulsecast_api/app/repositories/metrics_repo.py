from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models.metrics import ForecastAccuracyBySkuMonth, ForecastRunSummary, ValueImpactSummary

logger = logging.getLogger(__name__)

MAX_LIMIT = 500


def list_forecast_runs(
    db: Session,
    run_type: Optional[str],
    computed_from: Optional[datetime],
    computed_to: Optional[datetime],
    limit: int,
) -> List[ForecastRunSummary]:
    safe_limit = min(max(limit, 1), MAX_LIMIT)
    stmt = select(ForecastRunSummary).order_by(ForecastRunSummary.computed_at.desc()).limit(safe_limit)
    conditions = []
    if run_type:
        conditions.append(ForecastRunSummary.run_type == run_type)
    if computed_from:
        conditions.append(ForecastRunSummary.computed_at >= computed_from)
    if computed_to:
        conditions.append(ForecastRunSummary.computed_at <= computed_to)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    try:
        rows = list(db.execute(stmt).scalars())
        logger.info("Listed %s forecast runs", len(rows))
        return rows
    except SQLAlchemyError as exc:
        logger.error("DB error listing forecast runs", exc_info=exc)
        raise


def get_run_summary(db: Session, run_id: str) -> Optional[ForecastRunSummary]:
    stmt = select(ForecastRunSummary).where(ForecastRunSummary.run_id == run_id).limit(1)
    try:
        return db.execute(stmt).scalar_one_or_none()
    except SQLAlchemyError as exc:
        logger.error("DB error fetching run summary %s", run_id, exc_info=exc)
        raise


def get_accuracy_for_run(
    db: Session,
    run_id: str,
    sku_id: Optional[str],
    family: Optional[str],
    from_month: Optional[datetime],
    to_month: Optional[datetime],
) -> List[ForecastAccuracyBySkuMonth]:
    stmt = select(ForecastAccuracyBySkuMonth).where(ForecastAccuracyBySkuMonth.run_id == run_id)
    if sku_id:
        stmt = stmt.where(ForecastAccuracyBySkuMonth.sku_id == sku_id)
    if from_month:
        stmt = stmt.where(ForecastAccuracyBySkuMonth.year_month >= from_month)
    if to_month:
        stmt = stmt.where(ForecastAccuracyBySkuMonth.year_month <= to_month)
    stmt = stmt.order_by(ForecastAccuracyBySkuMonth.sku_id.asc(), ForecastAccuracyBySkuMonth.year_month.asc())
    try:
        return list(db.execute(stmt).scalars())
    except SQLAlchemyError as exc:
        logger.error("DB error fetching accuracy for run %s", run_id, exc_info=exc)
        raise


def get_value_impact_for_run(db: Session, run_id: str) -> Optional[ValueImpactSummary]:
    stmt = select(ValueImpactSummary).where(ValueImpactSummary.run_id == run_id).limit(1)
    try:
        return db.execute(stmt).scalar_one_or_none()
    except SQLAlchemyError as exc:
        logger.error("DB error fetching value impact for run %s", run_id, exc_info=exc)
        raise


def get_value_impact_for_runs(
    db: Session,
    run_ids: Optional[List[str]],
    computed_from: Optional[datetime],
    computed_to: Optional[datetime],
    limit: int,
) -> List[ValueImpactSummary]:
    safe_limit = min(max(limit, 1), MAX_LIMIT)
    stmt = select(ValueImpactSummary).limit(safe_limit)
    conditions = []
    if run_ids:
        conditions.append(ValueImpactSummary.run_id.in_(run_ids))
    if computed_from:
        conditions.append(ValueImpactSummary.computed_at >= computed_from)
    if computed_to:
        conditions.append(ValueImpactSummary.computed_at <= computed_to)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.order_by(ValueImpactSummary.computed_at.desc().nullslast())
    try:
        return list(db.execute(stmt).scalars())
    except SQLAlchemyError as exc:
        logger.error("DB error listing value impact", exc_info=exc)
        raise
