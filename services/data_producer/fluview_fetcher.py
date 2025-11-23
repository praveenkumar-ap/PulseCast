from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

import requests

from services.pulsecast_api.app.core.config import settings

logger = logging.getLogger(__name__)


def _epiweek_to_date(epiweek: int) -> datetime:
    year = epiweek // 100
    week = epiweek % 100
    return datetime.fromisocalendar(year, week, 1)


def fetch_fluview() -> List[Dict[str, Any]]:
    """Fetch FluView ILI data for configured regions and epiweek range."""
    base_url = settings.fluview_base_url
    regions = settings.fluview_regions
    start_week = settings.fluview_epiweek_start
    end_week = settings.fluview_epiweek_end
    if not regions or not start_week or not end_week:
        logger.warning("FluView config incomplete; skipping fetch.")
        return []

    params = {
        "regions": ",".join(regions),
        "epiweeks": f"{start_week}-{end_week}",
    }
    try:
        resp = requests.get(base_url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.error("FluView fetch failed", exc_info=exc)
        raise

    results = data.get("result")
    if results != 1:
        logger.warning("FluView response result=%s", results)
        return []
    records = data.get("epidata", [])
    out: List[Dict[str, Any]] = []
    for rec in records:
        epiweek = rec.get("epiweek")
        region = rec.get("region")
        if epiweek is None or region is None:
            continue
        indicator_id = f"flu_ili_{region.lower()}"
        event_time = _epiweek_to_date(int(epiweek))
        value = rec.get("wili") or rec.get("unweighted_ili") or rec.get("ili")
        if value is None:
            continue
        out.append(
            {
                "indicator_id": indicator_id,
                "event_time": event_time.isoformat(),
                "geo": region.upper(),
                "value": float(value),
                "source_system": "DELPHI_FLUVIEW",
                "payload": rec,
            }
        )
    logger.info("FluView fetched %s records", len(out))
    return out
