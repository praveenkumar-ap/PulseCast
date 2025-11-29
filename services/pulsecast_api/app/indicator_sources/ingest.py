from __future__ import annotations

from datetime import date, datetime
from typing import Iterable, Optional

from sqlalchemy.orm import Session

from ..core.logging import get_logger
from ..models.indicator_sources import IndicatorSeries, IndicatorSource
from .base import IndicatorRow, SourceIngestionResult
from .registry import registry

logger = get_logger(__name__)


def ingest_active_sources(
    *,
    db: Session,
    since: Optional[date] = None,
    until: Optional[date] = None,
) -> list[SourceIngestionResult]:
    """Ingest all ACTIVE indicator sources."""
    sources = db.query(IndicatorSource).filter(IndicatorSource.status == "ACTIVE").all()
    results: list[SourceIngestionResult] = []
    for src in sources:
        try:
            adapter = registry.get(src.code)
        except KeyError:
            logger.warning("No adapter registered for source_code=%s", src.code)
            continue

        rows = adapter.fetch(since=since, until=until, config=src.config or {})
        res = _upsert_series(db=db, src=src, rows=rows)
        results.append(res)
    return results


def _upsert_series(
    *,
    db: Session,
    src: IndicatorSource,
    rows: Iterable[IndicatorRow],
) -> SourceIngestionResult:
    started = datetime.utcnow()
    upserted = 0
    fetched = 0
    for row in rows:
        fetched += 1
        try:
            db.merge(
                IndicatorSeries(
                    source_id=src.id,
                    source_code=src.code,
                    indicator_code=row.indicator_code,
                    geo_key=row.geo_key,
                    as_of_date=row.as_of_date,
                    value=row.value,
                    extra_meta=row.extra_meta,
                )
            )
            upserted += 1
        except Exception:  # noqa: BLE001
            logger.exception("Failed to upsert indicator row for %s", src.code)
    try:
        db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()
        logger.exception("Commit failed for source_code=%s", src.code)
    finished = datetime.utcnow()
    return SourceIngestionResult(
        source_code=src.code,
        rows_fetched=fetched,
        rows_upserted=upserted,
        started_at=started,
        finished_at=finished,
    )
