from __future__ import annotations

from datetime import date, datetime
from typing import Iterable, Mapping, Optional

from pydantic import BaseModel, Field


class IndicatorRow(BaseModel):
    """Normalized indicator row used by all adapters."""

    source_code: str
    indicator_code: str
    geo_key: str
    as_of_date: date
    value: float
    extra_meta: Mapping[str, object] | None = None


class IndicatorSourceAdapter:
    """Protocol-like base class for indicator source adapters."""

    source_code: str

    def fetch(
        self, *, since: Optional[date], until: Optional[date], config: Mapping[str, object]
    ) -> Iterable[IndicatorRow]:
        raise NotImplementedError


class SourceIngestionResult(BaseModel):
    source_code: str
    rows_fetched: int
    rows_upserted: int
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
