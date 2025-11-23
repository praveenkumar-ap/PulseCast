from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from sqlalchemy.orm import Session

# Ensure project root is on sys.path when running as a script
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.pulsecast_api.app.core.config import settings
from services.pulsecast_api.app.core.db import SessionLocal
from services.pulsecast_api.app.core.logging import configure_logging, get_logger
from services.pulsecast_api.app.models.signals import ExternalSignalStaging
from services.data_producer.fluview_fetcher import fetch_fluview
from services.data_producer.weather_fetcher import fetch_weather
from services.data_producer.kafka_producer import SignalsProducer

logger = get_logger(__name__)


def persist_staging(db: Session, records: List[Dict[str, Any]]) -> int:
    if not records:
        return 0
    rows = []
    for rec in records:
        try:
            event_time = rec["event_time"]
            if isinstance(event_time, str):
                from datetime import datetime

                event_time = datetime.fromisoformat(event_time)
            rows.append(
                ExternalSignalStaging(
                    event_id=uuid4(),
                    indicator_id=rec["indicator_id"],
                    event_time=event_time,
                    geo=rec.get("geo"),
                    value=rec.get("value"),
                    source_system=rec.get("source_system", "UNKNOWN"),
                    payload_json=str(rec.get("payload")),
                )
            )
        except KeyError:
            logger.warning("Skipping invalid record (missing keys): %s", rec)
            continue
    if not rows:
        return 0
    try:
        db.add_all(rows)
        db.commit()
        logger.info("Persisted %s records to staging", len(rows))
        return len(rows)
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        logger.error("Failed to persist staging records", exc_info=exc)
        raise


def batch_fetch() -> None:
    with SessionLocal() as db:
        total = 0
        for fetcher in (fetch_fluview, fetch_weather):
            try:
                records = fetcher()
                total += persist_staging(db, records)
            except Exception as exc:  # noqa: BLE001
                logger.error("Fetcher %s failed", fetcher.__name__, exc_info=exc)
        logger.info("Batch fetch complete; total records persisted=%s", total)


def replay() -> None:
    producer = SignalsProducer()
    sleep_seconds = settings.replay_sleep_seconds
    speed_factor = settings.replay_speed_factor
    try:
        with SessionLocal() as db:
            stmt = (
                db.query(ExternalSignalStaging)
                .order_by(ExternalSignalStaging.event_time.asc())
            )
            total = 0
            for row in stmt:
                event = {
                    "indicator_id": row.indicator_id,
                    "event_time": row.event_time.isoformat(),
                    "geo": row.geo,
                    "value": float(row.value) if row.value is not None else None,
                    "source_system": row.source_system,
                    "payload": row.payload_json,
                }
                producer.send(event)
                total += 1
                time.sleep(sleep_seconds / max(speed_factor, 1e-6))
            producer.flush()
            logger.info("Replay complete; sent %s events", total)
    finally:
        producer.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PulseCast data producer")
    parser.add_argument("--mode", choices=["batch_fetch", "replay"], required=True)
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    if args.mode == "batch_fetch":
        batch_fetch()
    elif args.mode == "replay":
        replay()


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001
        logger.exception("Data producer failed")
        sys.exit(1)
