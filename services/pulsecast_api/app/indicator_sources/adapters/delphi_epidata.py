from __future__ import annotations

from datetime import date
from typing import Iterable, Mapping, Optional

import requests

from ...core.config import settings
from ...core.logging import get_logger
from ..base import IndicatorRow, IndicatorSourceAdapter
from ..registry import register_adapter

logger = get_logger(__name__)


def _epiweek_to_date(epiweek: int) -> date:
    year = epiweek // 100
    week = epiweek % 100
    return date.fromisocalendar(year, week, 1)


@register_adapter("delphi_epidata")
class DelphiEpidataAdapter(IndicatorSourceAdapter):
    source_code = "delphi_epidata"

    def fetch(
        self, *, since: Optional[date], until: Optional[date], config: Mapping[str, object]
    ) -> Iterable[IndicatorRow]:
        base_url = (config.get("base_url") or settings.fluview_base_url) if config else settings.fluview_base_url
        regions = (config.get("regions") or settings.fluview_regions) if config else settings.fluview_regions
        start_week = (config.get("start_epiweek") or settings.fluview_epiweek_start) if config else settings.fluview_epiweek_start
        end_week = (config.get("end_epiweek") or settings.fluview_epiweek_end) if config else settings.fluview_epiweek_end
        if not regions or not start_week or not end_week:
            logger.warning("DelphiEpidataAdapter missing regions or epiweek window; returning empty.")
            return []

        params = {"regions": ",".join(regions), "epiweeks": f"{start_week}-{end_week}"}
        try:
            resp = requests.get(base_url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Delphi Epidata fetch failed")
            return []

        if data.get("result") != 1:
            logger.warning("Delphi Epidata returned result=%s", data.get("result"))
            return []

        out: list[IndicatorRow] = []
        for rec in data.get("epidata", []):
            epiweek = rec.get("epiweek")
            region = rec.get("region")
            value = rec.get("wili") or rec.get("unweighted_ili") or rec.get("ili")
            if epiweek is None or region is None or value is None:
                continue
            as_of = _epiweek_to_date(int(epiweek))
            if since and as_of < since:
                continue
            if until and as_of > until:
                continue
            out.append(
                IndicatorRow(
                    source_code=self.source_code,
                    indicator_code="ILI_RATE",
                    geo_key=region.upper(),
                    as_of_date=as_of,
                    value=float(value),
                    extra_meta={"raw": rec},
                )
            )
        return out
