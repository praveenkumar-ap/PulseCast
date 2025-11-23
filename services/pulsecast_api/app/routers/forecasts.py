import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.rbac import require_roles
from ..models.forecasts import Forecast
from ..repositories.forecasts_repo import get_forecasts_for_sku
from ..schemas.forecasts import ForecastItem, ForecastResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/forecasts",
    tags=["forecasts"],
    dependencies=[Depends(require_roles("PLANNER", "SOP_APPROVER", "DATA_SCIENTIST", "ADMIN"))],
)


def _validate_month(value: Optional[str], field_name: str) -> Optional[str]:
    if value is None:
        return None
    try:
        datetime.strptime(value, "%Y-%m")
        return value
    except ValueError as exc:
        logger.warning("Invalid %s format: %s", field_name, value)
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}, expected YYYY-MM") from exc


@router.get("/{sku_id}", response_model=ForecastResponse)
def get_forecasts(
    sku_id: str,
    from_month: Optional[str] = Query(default=None, description="Filter from YYYY-MM"),
    to_month: Optional[str] = Query(default=None, description="Filter to YYYY-MM"),
    db: Session = Depends(get_db),
) -> ForecastResponse:
    """Fetch forecasts for a SKU with optional month range."""
    from_month = _validate_month(from_month, "from_month")
    to_month = _validate_month(to_month, "to_month")

    if from_month and to_month and from_month > to_month:
        raise HTTPException(status_code=400, detail="from_month cannot be after to_month")

    try:
        forecasts: list[Forecast] = get_forecasts_for_sku(db, sku_id, from_month, to_month)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error("DB error fetching forecasts for sku_id=%s", sku_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error fetching forecasts for sku_id=%s", sku_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    items = [
        ForecastItem(
            year_month=f.year_month.strftime("%Y-%m"),
            p10=float(f.p10) if f.p10 is not None else None,
            p50=float(f.p50) if f.p50 is not None else None,
            p90=float(f.p90) if f.p90 is not None else None,
            run_id=f.run_id,
        )
        for f in forecasts
    ]

    return ForecastResponse(sku_id=sku_id, forecasts=items)
