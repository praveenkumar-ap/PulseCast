from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models.signals import SignalNowcastWindow, SignalStreamRaw

logger = logging.getLogger(__name__)
MAX_LIMIT = 500


def list_events(
    db: Session,
    indicator_id: str,
    from_time: Optional[datetime],
    to_time: Optional[datetime],
    limit: int,
) -> List[SignalStreamRaw]:
    safe_limit = min(max(limit, 1), MAX_LIMIT)
    stmt = select(SignalStreamRaw).where(SignalStreamRaw.indicator_id == indicator_id)
    if from_time:
        stmt = stmt.where(SignalStreamRaw.event_time >= from_time)
    if to_time:
        stmt = stmt.where(SignalStreamRaw.event_time <= to_time)
    stmt = stmt.order_by(SignalStreamRaw.event_time.desc()).limit(safe_limit)
    try:
        return list(db.execute(stmt).scalars())
    except SQLAlchemyError as exc:
        logger.error("Failed to list signal events", exc_info=exc)
        raise


def list_nowcast(
    db: Session,
    indicator_id: Optional[str],
    limit: int,
) -> List[SignalNowcastWindow]:
    safe_limit = min(max(limit, 1), MAX_LIMIT)
    stmt = select(SignalNowcastWindow)
    if indicator_id:
        stmt = stmt.where(SignalNowcastWindow.indicator_id == indicator_id)
    stmt = stmt.order_by(SignalNowcastWindow.indicator_id.asc()).limit(safe_limit)
    try:
        return list(db.execute(stmt).scalars())
    except SQLAlchemyError as exc:
        logger.error("Failed to list nowcast snapshots", exc_info=exc)
        raise
