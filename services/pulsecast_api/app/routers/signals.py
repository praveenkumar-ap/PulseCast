import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.rbac import require_roles
from ..repositories.signals_repo import list_events, list_nowcast
from ..schemas.signals import SignalEvent, SignalNowcastSnapshot, SignalsEventsResponse, SignalsNowcastResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/signals",
    tags=["signals"],
    dependencies=[Depends(require_roles("PLANNER", "SOP_APPROVER", "DATA_SCIENTIST", "ADMIN", "SUPPORT_OPERATOR"))],
)


def _parse_dt(val: Optional[str], name: str) -> Optional[datetime]:
    if val is None:
        return None
    try:
        return datetime.fromisoformat(val)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid {name}, expected ISO datetime") from exc


@router.get("/events", response_model=SignalsEventsResponse)
def get_events(
    indicator_id: str = Query(..., description="Indicator ID"),
    from_time: Optional[str] = Query(default=None),
    to_time: Optional[str] = Query(default=None),
    limit: int = Query(default=100),
    db: Session = Depends(get_db),
) -> SignalsEventsResponse:
    try:
        rows = list_events(
            db,
            indicator_id=indicator_id,
            from_time=_parse_dt(from_time, "from_time"),
            to_time=_parse_dt(to_time, "to_time"),
            limit=limit,
        )
    except SQLAlchemyError as exc:
        logger.error("DB error listing signal events", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    events = [
        SignalEvent(
            event_id=str(r.event_id),
            indicator_id=r.indicator_id,
            event_time=r.event_time,
            geo=r.geo,
            value=float(r.value),
            source_system=r.source_system,
            ingested_at=r.ingested_at,
        )
        for r in rows
    ]
    return SignalsEventsResponse(events=events)


@router.get("/nowcast", response_model=SignalsNowcastResponse)
def get_nowcast(
    indicator_id: Optional[str] = Query(default=None),
    limit: int = Query(default=100),
    db: Session = Depends(get_db),
) -> SignalsNowcastResponse:
    try:
        rows = list_nowcast(db, indicator_id, limit)
    except SQLAlchemyError as exc:
        logger.error("DB error listing nowcast", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    snapshots = [
        SignalNowcastSnapshot(
            indicator_id=r.indicator_id,
            window_start=r.window_start,
            window_end=r.window_end,
            window_value=float(r.window_value) if r.window_value is not None else None,
            baseline_value=float(r.baseline_value) if r.baseline_value is not None else None,
            delta_value=float(r.delta_value) if r.delta_value is not None else None,
            delta_pct=float(r.delta_pct) if r.delta_pct is not None else None,
        )
        for r in rows
    ]
    return SignalsNowcastResponse(snapshots=snapshots)
