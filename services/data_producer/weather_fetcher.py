from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

import requests

from services.pulsecast_api.app.core.config import settings

logger = logging.getLogger(__name__)


def fetch_weather() -> List[Dict[str, Any]]:
    """Fetch Open-Meteo daily temperature for configured locations/date range."""
    base_url = settings.open_meteo_base_url
    locations = settings.open_meteo_locations
    start_date = settings.weather_start_date
    end_date = settings.weather_end_date
    if not locations or not start_date or not end_date:
        logger.warning("Weather config incomplete; skipping fetch.")
        return []

    out: List[Dict[str, Any]] = []
    for loc in locations:
        lat = loc.get("lat")
        lon = loc.get("lon")
        label = loc.get("label")
        if lat is None or lon is None or not label:
            continue
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_mean",
            "timezone": "UTC",
        }
        try:
            resp = requests.get(base_url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.error("Weather fetch failed for %s", label, exc_info=exc)
            continue

        times = data.get("daily", {}).get("time", [])
        temps = data.get("daily", {}).get("temperature_2m_mean", [])
        indicator_id = f"weather_temp_avg_{label.lower()}"
        for t, temp in zip(times, temps):
            try:
                event_time = datetime.fromisoformat(t)
            except ValueError:
                continue
            out.append(
                {
                    "indicator_id": indicator_id,
                    "event_time": event_time.isoformat(),
                    "geo": label,
                    "value": float(temp),
                    "source_system": "OPEN_METEO",
                    "payload": {"time": t, "temperature_2m_mean": temp, "label": label},
                }
            )
    logger.info("Weather fetched %s records", len(out))
    return out
