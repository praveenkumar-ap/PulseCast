from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class SignalEvent(BaseModel):
    event_id: str
    indicator_id: str
    event_time: datetime
    geo: Optional[str] = None
    value: float
    source_system: str
    ingested_at: datetime


class SignalsEventsResponse(BaseModel):
    events: List[SignalEvent]


class SignalNowcastSnapshot(BaseModel):
    indicator_id: str
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None
    window_value: Optional[float] = None
    baseline_value: Optional[float] = None
    delta_value: Optional[float] = None
    delta_pct: Optional[float] = None


class SignalsNowcastResponse(BaseModel):
    snapshots: List[SignalNowcastSnapshot]
