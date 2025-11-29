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


def _epiweek_to_date(epiweek: int) -> datetime:
    year = epiweek // 100
    week = epiweek % 100
    return datetime.fromisocalendar(year, week, 1)


@register_adapter
class CDCFluViewAdapter(BaseBatchAdapter):
    """
    Ingest ILI/FluView data (CDC) via Delphi proxy endpoint.

    This adapter mirrors DelphiEpidataAdapter but is kept separate to allow
    source-specific configuration and future CDC direct calls.
    """

    name = "cdc_fluview"

    def ingest(
        self,
        *,
        db: Session,
        ctx: IngestionContext,
        config: Mapping[str, Any],
    ) -> IngestionResult:
        base_url = config.get("base_url") or settings.fluview_base_url
        regions = config.get("regions") or settings.fluview_regions
        start_week = config.get("start_epiweek") or settings.fluview_epiweek_start
        end_week = config.get("end_epiweek") or settings.fluview_epiweek_end
        if not regions or not start_week or not end_week:
            logger.warning("CDC FluView config incomplete; skipping ingestion.")
            return IngestionResult(
                records_ingested=0,
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=datetime.utcnow(),
                notes="Missing regions or epiweek window",
            )

        params = {
            "regions": ",".join(regions),
            "epiweeks": f"{start_week}-{end_week}",
        }

        try:
            resp = requests.get(base_url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.exception("CDC FluView fetch failed")
            return IngestionResult(
                records_ingested=0,
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=datetime.utcnow(),
                notes=str(exc),
            )

        if data.get("result") != 1:
            return IngestionResult(
                records_ingested=0,
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=datetime.utcnow(),
                notes=f"API returned result={data.get('result')}",
            )

        records = []
        for rec in data.get("epidata", []):
            epiweek = rec.get("epiweek")
            region = rec.get("region")
            value = rec.get("wili") or rec.get("unweighted_ili") or rec.get("ili")
            if epiweek is None or region is None or value is None:
                continue
            event_time = _epiweek_to_date(int(epiweek))
            indicator_id = f"cdc_flu_ili_{region.lower()}"
            records.append(
                {
                    "event_id": uuid4(),
                    "indicator_id": indicator_id,
                    "event_time": event_time,
                    "geo": region.upper(),
                    "value": float(value),
                    "source_system": "CDC_FLUVIEW",
                    "payload": rec,
                }
            )

        ingested, failed = persist_external_signals(
            db=db, rows=records, source_name=self.name
        )
        return IngestionResult(
            records_ingested=ingested,
            records_failed=failed,
            source_name=self.name,
            started_at=ctx.started_at,
            finished_at=datetime.utcnow(),
            notes=None if failed == 0 else f"{failed} rows failed validation",
        )
