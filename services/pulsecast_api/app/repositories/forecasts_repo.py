import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models.forecasts import Forecast

logger = logging.getLogger(__name__)


def _parse_month(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.strptime(value, "%Y-%m")
    except ValueError as exc:
        logger.warning("Invalid month format: %s", value)
        raise


def get_forecasts_for_sku(
    db: Session,
    sku_id: str,
    from_month: Optional[str],
    to_month: Optional[str],
) -> List[Forecast]:
    """Fetch forecasts for a SKU with optional month range."""
    from_dt = _parse_month(from_month)
    to_dt = _parse_month(to_month)

    conditions = [Forecast.sku_id == sku_id]
    if from_dt:
        conditions.append(Forecast.year_month >= from_dt.date())
    if to_dt:
        conditions.append(Forecast.year_month <= to_dt.date())

    stmt = (
        select(Forecast)
        .where(and_(*conditions))
        .order_by(Forecast.year_month.asc())
    )

    try:
        return list(db.execute(stmt).scalars())
    except SQLAlchemyError as exc:
        logger.error("Failed to fetch forecasts for sku_id=%s", sku_id, exc_info=exc)
        raise
