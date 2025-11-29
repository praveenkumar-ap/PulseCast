from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Iterable, Tuple
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from ..core.logging import get_logger
from ..models.signals import ExternalSignalStaging

logger = get_logger(__name__)


def persist_external_signals(
    *,
    db: Session,
    rows: Iterable[dict[str, Any]],
    source_name: str,
) -> Tuple[int, int]:
    """
    Persist rows into signals.external_staging.

    Returns a tuple (ingested, failed).
    """
    ingested = 0
    failed = 0
    objects: list[ExternalSignalStaging] = []

    for row in rows:
        try:
            event_id = row.get("event_id")
            indicator_id = row["indicator_id"]
            event_time = row["event_time"]
            geo = row.get("geo")
            value = row["value"]
            payload = row.get("payload")
            objects.append(
                ExternalSignalStaging(
                    event_id=event_id if isinstance(event_id, UUID) else uuid4(),
                    indicator_id=indicator_id,
                    event_time=_coerce_datetime(event_time),
                    geo=geo,
                    value=value,
                    source_system=row.get("source_system") or source_name,
                    payload_json=json.dumps(payload) if payload is not None else None,
                )
            )
            ingested += 1
        except Exception:  # noqa: BLE001
            failed += 1
            logger.exception("Skipping malformed row for source=%s", source_name)

    if not objects:
        return ingested, failed

    try:
        db.add_all(objects)
        db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()
        logger.exception("Failed to persist external signals for source=%s", source_name)
        raise

    return ingested, failed


def _coerce_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    raise ValueError(f"Unsupported datetime value: {value!r}")
