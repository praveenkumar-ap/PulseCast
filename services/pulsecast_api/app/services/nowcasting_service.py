from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.signals import SignalNowcastWindow

logger = logging.getLogger(__name__)


@dataclass
class DetectedSpike:
    indicator_id: str
    window_value: float
    baseline_value: float
    delta_pct: float
    delta_value: float


def evaluate_spikes(db: Session) -> List[DetectedSpike]:
    """Evaluate spikes based on nowcast window view."""
    threshold = settings.stream_spike_delta_pct_threshold
    stmt = select(SignalNowcastWindow)
    rows = list(db.execute(stmt).scalars())
    spikes: List[DetectedSpike] = []
    for r in rows:
        if r.delta_pct is None:
            continue
        try:
            delta_pct = float(r.delta_pct)
        except (TypeError, ValueError):
            continue
        if delta_pct >= threshold:
            spikes.append(
                DetectedSpike(
                    indicator_id=r.indicator_id,
                    window_value=float(r.window_value or 0),
                    baseline_value=float(r.baseline_value or 0),
                    delta_pct=delta_pct,
                    delta_value=float(r.delta_value or 0),
                )
            )
    logger.info("Evaluated spikes; found %s candidates", len(spikes))
    return spikes
