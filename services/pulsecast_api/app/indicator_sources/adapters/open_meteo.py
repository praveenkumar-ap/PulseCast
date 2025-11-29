from __future__ import annotations

from datetime import date, datetime
from typing import Iterable, Mapping, Optional

import requests

from ...core.config import settings
from ...core.logging import get_logger
from ..base import IndicatorRow, IndicatorSourceAdapter
from ..registry import register_adapter

logger = get_logger(__name__)


@register_adapter("open_meteo")
class OpenMeteoAdapter(IndicatorSourceAdapter):
    source_code = "open_meteo"

    def fetch(
        self, *, since: Optional[date], until: Optional[date], config: Mapping[str, object]
    ) -> Iterable[IndicatorRow]:
        base_url = (config.get("base_url") or settings.open_meteo_base_url) if config else settings.open_meteo_base_url
        locations = (config.get("locations") or settings.open_meteo_locations) if config else settings.open_meteo_locations
        start_date = (config.get("start_date") or settings.weather_start_date) if config else settings.weather_start_date
        end_date = (config.get("end_date") or settings.weather_end_date) if config else settings.weather_end_date

        if not locations or not start_date or not end_date:
            logger.warning("OpenMeteoAdapter missing locations or date range; returning empty.")
            return []

        out: list[IndicatorRow] = []
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
                resp = requests.get(base_url, params=params, timeout=15)
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:  # noqa: BLE001
                logger.exception("Open-Meteo fetch failed for %s", label)
                continue

            times = data.get("daily", {}).get("time", [])
            temps = data.get("daily", {}).get("temperature_2m_mean", [])
            for t, temp in zip(times, temps):
                try:
                    as_of = datetime.fromisoformat(t).date()
                except ValueError:
                    continue
                if since and as_of < since:
                    continue
                if until and as_of > until:
                    continue
                out.append(
                    IndicatorRow(
                        source_code=self.source_code,
                        indicator_code="TEMP_AVG",
                        geo_key=label,
                        as_of_date=as_of,
                        value=float(temp),
                        extra_meta={"label": label},
                    )
                )
        return out
