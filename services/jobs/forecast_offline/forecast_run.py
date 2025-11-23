from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

import pandas as pd
import psycopg

from .db import get_connection
from .model import generate_forecasts


def load_labels(conn: psycopg.Connection) -> pd.DataFrame:
    label_schema = os.getenv("LABEL_SCHEMA") or "mart"
    query = f"""
        select
            sku_id,
            year_month,
            demand_10m_rolling
        from {label_schema}.label_sku_demand_10m_roll
    """
    return pd.read_sql(query, conn)


def insert_forecasts(conn: psycopg.Connection, forecasts: pd.DataFrame, run_id: str, created_at) -> int:
    if forecasts.empty:
        return 0

    forecasts = forecasts.copy()
    forecasts["run_id"] = run_id
    forecasts["created_at"] = created_at

    records = [
        (
            row["sku_id"],
            row["year_month"].date() if hasattr(row["year_month"], "date") else row["year_month"],
            row["p10"],
            row["p50"],
            row["p90"],
            row["run_id"],
            row["created_at"],
        )
        for _, row in forecasts.iterrows()
    ]

    insert_sql = """
        insert into analytics.sku_forecasts (
            sku_id, year_month, p10, p50, p90, run_id, created_at
        )
        values (%s, %s, %s, %s, %s, %s, %s)
    """

    with conn.cursor() as cur:
        cur.executemany(insert_sql, records)

    return len(records)


def main():
    run_id = str(uuid4())
    created_at = datetime.now(timezone.utc)

    print("Starting forecast run", run_id)
    try:
        with get_connection() as conn:
            labels_df = load_labels(conn)
            forecasts_df = generate_forecasts(labels_df, horizon_months=6)

            inserted = insert_forecasts(conn, forecasts_df, run_id, created_at)
            conn.commit()

            sku_count = forecasts_df["sku_id"].nunique() if not forecasts_df.empty else 0
            months = forecasts_df["year_month"].nunique() if not forecasts_df.empty else 0

            print(f"Forecast run complete. run_id={run_id}")
            print(f"SKUs: {sku_count}, horizon months: {months}, rows inserted: {inserted}")
    except Exception as exc:  # noqa: BLE001
        print(f"Forecast run failed: {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
