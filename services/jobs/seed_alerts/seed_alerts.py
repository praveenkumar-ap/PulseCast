from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import List
from uuid import uuid4

import psycopg

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_conn() -> psycopg.Connection:
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "5432"))
    dbname = os.getenv("DB_NAME", "pulsecast")
    user = os.getenv("DB_USER", "pulsecast")
    password = os.getenv("DB_PASSWORD", "pulsecast")
    return psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )


def build_fake_alerts() -> List[tuple]:
    now = datetime.now(timezone.utc)
    rows = [
        (
            uuid4(),
            "indicator-demand-spike",
            "sku-100",
            "US",
            "DEMAND_SPIKE",
            "HIGH",
            "OPEN",
            "Demand spike detected for sku-100 in US",
            now - timedelta(hours=2),
            None,
            now - timedelta(hours=2),
            now - timedelta(hours=2),
        ),
        (
            uuid4(),
            "indicator-demand-drop",
            "sku-200",
            "EU",
            "DEMAND_DROP",
            "MEDIUM",
            "ACKNOWLEDGED",
            "Demand drop observed for sku-200 in EU",
            now - timedelta(days=1),
            now - timedelta(hours=12),
            now - timedelta(days=1),
            now - timedelta(hours=12),
        ),
        (
            uuid4(),
            "feed-staleness",
            None,
            None,
            "FEED_STALENESS",
            "CRITICAL",
            "OPEN",
            "Inbound data feed stale beyond SLA",
            now - timedelta(hours=4),
            None,
            now - timedelta(hours=4),
            now - timedelta(hours=4),
        ),
    ]
    return rows


def insert_alerts(conn: psycopg.Connection, rows: List[tuple]) -> int:
    sql = """
        insert into alerts.alerts (
            alert_id, indicator_id, sku_id, geo_id, alert_type, severity, status,
            message, triggered_at, acknowledged_at, created_at, updated_at
        ) values (
            %(alert_id)s, %(indicator_id)s, %(sku_id)s, %(geo_id)s, %(alert_type)s,
            %(severity)s, %(status)s, %(message)s, %(triggered_at)s,
            %(acknowledged_at)s, %(created_at)s, %(updated_at)s
        )
    """
    dict_rows = []
    for row in rows:
        dict_rows.append(
            {
                "alert_id": row[0],
                "indicator_id": row[1],
                "sku_id": row[2],
                "geo_id": row[3],
                "alert_type": row[4],
                "severity": row[5],
                "status": row[6],
                "message": row[7],
                "triggered_at": row[8],
                "acknowledged_at": row[9],
                "created_at": row[10],
                "updated_at": row[11],
            }
        )

    with conn.cursor() as cur:
        cur.executemany(sql, dict_rows)
    return len(dict_rows)


def main() -> None:
    try:
        with get_conn() as conn:
            rows = build_fake_alerts()
            inserted = insert_alerts(conn, rows)
            conn.commit()
            logger.info("Inserted %s alerts", inserted)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to seed alerts", exc_info=exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
