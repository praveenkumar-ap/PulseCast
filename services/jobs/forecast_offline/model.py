from __future__ import annotations

from datetime import datetime
from itertools import product
from typing import Iterable

import pandas as pd


def _normalize_year_month(labels: pd.DataFrame) -> pd.DataFrame:
    """Ensure year_month is a datetime first-of-month."""
    labels = labels.copy()
    labels["year_month"] = pd.to_datetime(labels["year_month"]).dt.to_period("M").dt.to_timestamp()
    return labels


def generate_forecasts(labels: pd.DataFrame, horizon_months: int = 6) -> pd.DataFrame:
    """Compute naive per-SKU forecasts for the next horizon_months."""
    if labels.empty:
        return pd.DataFrame(columns=["sku_id", "year_month", "p10", "p50", "p90"])

    labels = _normalize_year_month(labels)

    latest_month = labels["year_month"].max().to_period("M").to_timestamp()
    future_months = [latest_month + pd.DateOffset(months=i) for i in range(1, horizon_months + 1)]

    avg_by_sku = (
        labels.groupby("sku_id")["demand_10m_rolling"]
        .mean()
        .reset_index()
        .rename(columns={"demand_10m_rolling": "p50"})
    )
    avg_by_sku["p10"] = (avg_by_sku["p50"] * 0.9).clip(lower=0)
    avg_by_sku["p90"] = (avg_by_sku["p50"] * 1.1).clip(lower=0)

    rows = []
    for sku_id, month in product(avg_by_sku["sku_id"], future_months):
        values = avg_by_sku.loc[avg_by_sku["sku_id"] == sku_id].iloc[0]
        rows.append(
            {
                "sku_id": sku_id,
                "year_month": month,
                "p10": float(values["p10"]),
                "p50": float(values["p50"]),
                "p90": float(values["p90"]),
            }
        )

    return pd.DataFrame(rows)
