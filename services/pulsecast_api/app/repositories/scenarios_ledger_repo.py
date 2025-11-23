from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models.scenarios import ScenarioHeader
from ..models.scenarios_ledger import ScenarioLedger

logger = logging.getLogger(__name__)
MAX_EVENTS = 500

ALLOWED_ACTIONS = {"CREATE", "EDIT", "APPROVE", "REJECT", "ARCHIVE", "COMMENT", "RUN_OPTIMIZER"}


def _ensure_scenario_exists(db: Session, scenario_id: UUID) -> None:
    stmt = select(ScenarioHeader.scenario_id).where(ScenarioHeader.scenario_id == scenario_id).limit(1)
    found = db.execute(stmt).scalar_one_or_none()
    if found is None:
        raise ValueError("Scenario not found")


def append_event(
    db: Session,
    scenario_id: UUID,
    action_type: str,
    actor: str,
    actor_role: Optional[str],
    assumptions: Optional[str],
    comments: Optional[str],
    now: datetime,
) -> ScenarioLedger:
    if action_type not in ALLOWED_ACTIONS:
        raise ValueError("Invalid action_type")
    if not actor or not actor.strip():
        raise ValueError("actor is required")

    _ensure_scenario_exists(db, scenario_id)

    seq_stmt = select(func.coalesce(func.max(ScenarioLedger.version_seq), 0)).where(
        ScenarioLedger.scenario_id == scenario_id
    )
    current_max = db.execute(seq_stmt).scalar_one()
    next_seq = current_max + 1

    entry = ScenarioLedger(
        ledger_id=uuid4(),
        scenario_id=scenario_id,
        version_seq=next_seq,
        action_type=action_type,
        actor=actor,
        actor_role=actor_role,
        assumptions=assumptions,
        comments=comments,
        created_at=now,
    )
    try:
        db.add(entry)
        db.commit()
        logger.info("Appended ledger event scenario=%s seq=%s action=%s actor=%s", scenario_id, next_seq, action_type, actor)
        return entry
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to append ledger event for scenario %s", scenario_id, exc_info=exc)
        raise


def list_events(db: Session, scenario_id: UUID, limit: int = 50) -> List[ScenarioLedger]:
    _ensure_scenario_exists(db, scenario_id)
    safe_limit = min(max(limit, 1), MAX_EVENTS)
    stmt = (
        select(ScenarioLedger)
        .where(ScenarioLedger.scenario_id == scenario_id)
        .order_by(ScenarioLedger.version_seq.asc())
        .limit(safe_limit)
    )
    try:
        return list(db.execute(stmt).scalars())
    except SQLAlchemyError as exc:
        logger.error("Failed to list ledger events for scenario %s", scenario_id, exc_info=exc)
        raise
