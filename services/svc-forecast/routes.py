import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import get_session
from models import SkuForecast
from schemas import ForecastItem, ForecastResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
def health() -> dict:
    """Health check endpoint."""
    try:
        return {"status": "ok", "service": "svc-forecast"}
    except Exception as exc:  # noqa: BLE001
        logger.error("Health check failed", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


def _parse_month(value: Optional[str], field_name: str) -> Optional[datetime]:
    """Validate a YYYY-MM month string."""
    if value is None:
        return None
    try:
        return datetime.strptime(value, "%Y-%m")
    except ValueError as exc:
        logger.warning("Invalid %s format: %s", field_name, value)
        raise HTTPException(status_code=400, detail=f"Invalid {field_name} format, expected YYYY-MM") from exc


def _map_forecast(row: SkuForecast) -> ForecastItem:
    """Convert ORM row to response item."""
    return ForecastItem(
        year_month=row.year_month.strftime("%Y-%m"),
        p10=float(row.p10) if row.p10 is not None else None,
        p50=float(row.p50) if row.p50 is not None else None,
        p90=float(row.p90) if row.p90 is not None else None,
        run_id=row.run_id,
    )


@router.get("/forecasts/{sku_id}", response_model=ForecastResponse)
def get_forecasts(
    sku_id: str,
    from_month: Optional[str] = Query(default=None, description="Filter from YYYY-MM"),
    to_month: Optional[str] = Query(default=None, description="Filter to YYYY-MM"),
    db: Session = Depends(get_session),
) -> ForecastResponse:
    """Fetch forecasts for a SKU with optional month range filtering."""
    logger.info("Fetching forecasts for sku_id=%s, from_month=%s, to_month=%s", sku_id, from_month, to_month)
    from_dt = _parse_month(from_month, "from_month")
    to_dt = _parse_month(to_month, "to_month")

    if from_dt and to_dt and from_dt > to_dt:
        logger.warning("from_month after to_month for sku_id=%s", sku_id)
        raise HTTPException(status_code=400, detail="from_month cannot be after to_month")

    conditions = [SkuForecast.sku_id == sku_id]
    if from_dt:
        conditions.append(SkuForecast.year_month >= from_dt.date())
    if to_dt:
        conditions.append(SkuForecast.year_month <= to_dt.date())

    stmt = (
        select(SkuForecast)
        .where(and_(*conditions))
        .order_by(SkuForecast.year_month.asc())
    )

    try:
        results: List[SkuForecast] = list(db.execute(stmt).scalars())
    except SQLAlchemyError as exc:
        logger.error("Database query failed for sku_id=%s", sku_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    forecasts = [_map_forecast(row) for row in results]
    return ForecastResponse(sku_id=sku_id, forecasts=forecasts)
