from __future__ import annotations

import logging
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from ..models.value import RunValueSummary, ScenarioValueSummary, ValueBenchmark

logger = logging.getLogger(__name__)

DEFAULT_LIMIT = 100
MAX_LIMIT = 500


def _safe_limit(limit: Optional[int]) -> int:
    return min(max(limit or DEFAULT_LIMIT, 1), MAX_LIMIT)


def get_run_value_summary(db: Session, run_id: str) -> Optional[RunValueSummary]:
    stmt = select(RunValueSummary).where(RunValueSummary.run_id == run_id)
    return db.execute(stmt).scalar_one_or_none()


def list_run_value_summaries(
    db: Session,
    family_id: Optional[str],
    case_label: Optional[str],
    run_type: Optional[str],
    from_date: Optional[date],
    to_date: Optional[date],
    limit: Optional[int],
    offset: Optional[int],
) -> List[RunValueSummary]:
    stmt = select(RunValueSummary)
    conditions = []
    if family_id:
        conditions.append(RunValueSummary.family_id == family_id)
    if case_label:
        conditions.append(RunValueSummary.case_label == case_label)
    if run_type:
        conditions.append(RunValueSummary.run_type == run_type)
    if from_date:
        conditions.append(RunValueSummary.period_start >= from_date)
    if to_date:
        conditions.append(RunValueSummary.period_end <= to_date)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.order_by(RunValueSummary.period_end.desc().nullslast()).offset(offset or 0).limit(_safe_limit(limit))
    return list(db.execute(stmt).scalars())


def get_scenario_value_summary(db: Session, scenario_id: str) -> Optional[ScenarioValueSummary]:
    stmt = select(ScenarioValueSummary).where(ScenarioValueSummary.scenario_id == scenario_id)
    return db.execute(stmt).scalar_one_or_none()


def list_scenario_value_summaries(
    db: Session,
    family_id: Optional[str],
    case_label: Optional[str],
    status: Optional[str],
    from_date: Optional[datetime],
    to_date: Optional[datetime],
    limit: Optional[int],
    offset: Optional[int],
) -> List[ScenarioValueSummary]:
    stmt = select(ScenarioValueSummary)
    conditions = []
    if family_id:
        conditions.append(ScenarioValueSummary.family_id == family_id)
    if case_label:
        conditions.append(ScenarioValueSummary.case_label == case_label)
    if status:
        conditions.append(ScenarioValueSummary.status == status)
    if from_date:
        conditions.append(ScenarioValueSummary.created_at >= from_date)
    if to_date:
        conditions.append(ScenarioValueSummary.created_at <= to_date)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.order_by(ScenarioValueSummary.created_at.desc().nullslast()).offset(offset or 0).limit(_safe_limit(limit))
    return list(db.execute(stmt).scalars())


def list_benchmarks(db: Session, scope: Optional[str], scope_key: Optional[str]) -> List[ValueBenchmark]:
    stmt = select(ValueBenchmark)
    conditions = []
    if scope:
        conditions.append(ValueBenchmark.scope == scope)
    if scope_key:
        conditions.append(ValueBenchmark.scope_key == scope_key)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.order_by(ValueBenchmark.metric_name.asc())
    return list(db.execute(stmt).scalars())
