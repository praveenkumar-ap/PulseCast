from __future__ import annotations

import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from sqlalchemy.orm import Session

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parents[1] / ".."
ROOT = ROOT.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.pulsecast_api.app.core.config import settings
from services.pulsecast_api.app.core.db import SessionLocal
from services.pulsecast_api.app.core.logging import configure_logging, get_logger
from services.pulsecast_api.app.models.signals import SignalStreamRaw
from services.pulsecast_api.app.streaming.factory import StreamingDisabled, get_streaming_consumer
from services.pulsecast_api.app.services.nowcasting_service import evaluate_spikes
from services.pulsecast_api.app.repositories.alerts_repo import create_indicator_spike_alert

logger = get_logger(__name__)


def _validate_event(evt: Dict[str, Any]) -> bool:
    required = ["indicator_id", "event_time", "value"]
    return all(key in evt and evt[key] is not None for key in required)


def process_batch(db: Session, events: List[Dict[str, Any]]) -> None:
    if not events:
        return
    rows = []
    from datetime import datetime, timezone

    for evt in events:
        if not _validate_event(evt):
            logger.warning("Skipping invalid event: %s", evt)
            continue
        rows.append(
            SignalStreamRaw(
                event_id=uuid4(),
                indicator_id=str(evt["indicator_id"]),
                event_time=datetime.fromisoformat(evt["event_time"])
                if isinstance(evt["event_time"], str)
                else evt["event_time"],
                geo=evt.get("geo"),
                value=evt.get("value"),
                source_system=evt.get("source_system", "UNKNOWN"),
                ingested_at=datetime.now(timezone.utc),
                payload_json=str(evt),
            )
        )
    if not rows:
        return
    try:
        db.add_all(rows)
        db.commit()
        logger.info("Inserted %s signal events", len(rows))
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        logger.error("Failed to insert signal events", exc_info=exc)
        raise


def main() -> None:
    configure_logging()
    try:
        consumer = get_streaming_consumer()
    except StreamingDisabled:
        logger.warning("Streaming provider disabled; exiting consumer.")
        return
    except RuntimeError as exc:
        logger.error("Failed to initialize streaming consumer: %s", exc)
        return

    consumer.subscribe()
    try:
        while True:
            with SessionLocal() as db:
                try:
                    events = consumer.poll(batch_size=100)
                    process_batch(db, events)
                    consumer.ack()
                    # Evaluate spikes after insertion
                    spikes = evaluate_spikes(db)
                    for s in spikes:
                        severity = "HIGH" if s.delta_pct >= 1.0 else "MEDIUM"
                        create_indicator_spike_alert(
                            db,
                            indicator_id=s.indicator_id,
                            severity=severity,
                            payload={
                                "window_value": s.window_value,
                                "baseline_value": s.baseline_value,
                                "delta_pct": s.delta_pct,
                                "delta_value": s.delta_value,
                            },
                        )
                except Exception as exc:  # noqa: BLE001
                    logger.error("Error in consumer loop", exc_info=exc)
            time.sleep(settings.stream_poll_interval_ms / 1000.0)
    finally:
        consumer.close()


if __name__ == "__main__":
    try:
        from services.pulsecast_api.app.core.config import settings  # noqa: F401
    except Exception:  # noqa: BLE001
        logger.exception("Failed to load settings")
        sys.exit(1)
    main()
