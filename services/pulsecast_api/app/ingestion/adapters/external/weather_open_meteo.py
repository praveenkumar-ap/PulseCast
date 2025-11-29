from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping
from uuid import uuid4

import requests
from sqlalchemy.orm import Session

from ...core.config import settings
from ...core.logging import get_logger
from ...ingestion.base import BaseBatchAdapter, IngestionContext, IngestionResult
from ...ingestion.registry import register_adapter
from ...ingestion.utils import persist_external_signals

logger = get_logger(__name__)


@register_adapter
class WeatherOpenMeteoAdapter(BaseBatchAdapter):
    """Ingest daily weather signals from Open-Meteo archive API."""

    name = "weather_open_meteo"

    def ingest(
        self,
        *,
        db: Session,
        ctx: IngestionContext,
        config: Mapping[str, Any],
    ) -> IngestionResult:
        base_url = config.get("base_url") or settings.open_meteo_base_url
        locations = config.get("locations") or settings.open_meteo_locations
        start_date = config.get("start_date") or settings.weather_start_date
        end_date = config.get("end_date") or settings.weather_end_date

        if not locations or not start_date or not end_date:
            logger.warning("Weather config incomplete; skipping ingestion.")
            return IngestionResult(
                records_ingested=0,
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=datetime.utcnow(),
                notes="Missing locations or date range",
            )

        total_ingested = 0
        total_failed = 0
        for loc in locations:
            lat = loc.get("lat")
            lon = loc.get("lon")
            label = loc.get("label")
            if lat is None or lon is None or not label:
                logger.warning("Skipping invalid location config: %s", loc)
                total_failed += 1
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
                logger.exception("Weather fetch failed for %s", label)
                total_failed += 1
                continue

            times = data.get("daily", {}).get("time", [])
            temps = data.get("daily", {}).get("temperature_2m_mean", [])
            indicator_id = f"weather_temp_avg_{label.lower()}"
            records = []
            for t, temp in zip(times, temps):
                try:
                    event_time = datetime.fromisoformat(t)
                except ValueError:
                    total_failed += 1
                    continue
                records.append(
                    {
                        "event_id": uuid4(),
                        "indicator_id": indicator_id,
                        "event_time": event_time,
                        "geo": label,
                        "value": float(temp),
                        "source_system": "OPEN_METEO",
                        "payload": {"time": t, "temperature_2m_mean": temp, "label": label},
                    }
                )

            ingested, failed = persist_external_signals(
                db=db, rows=records, source_name=self.name
            )
            total_ingested += ingested
            total_failed += failed

        return IngestionResult(
            records_ingested=total_ingested,
            records_failed=total_failed,
            source_name=self.name,
            started_at=ctx.started_at,
            finished_at=datetime.utcnow(),
            notes=None if total_failed == 0 else f"{total_failed} rows failed validation",
        )
