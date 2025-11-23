import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.rbac import require_roles
from ..repositories.optimizer_repo import (
    ALLOWED_SOURCE_TYPES,
    list_recommendations,
    run_optimizer,
)
from ..schemas.optimizer import (
    ListRecommendationsResponse,
    RecommendationItem,
    RunOptimizerRequest,
    RunOptimizerResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/optimizer",
    tags=["optimizer"],
    dependencies=[Depends(require_roles("PLANNER", "DATA_SCIENTIST", "ADMIN"))],
)


def _validate_month_order(from_month: str, to_month: str) -> None:
    if from_month > to_month:
        raise HTTPException(status_code=400, detail="from_month cannot be after to_month")


@router.post("/run", response_model=RunOptimizerResponse)
def run_optimizer_endpoint(
    payload: RunOptimizerRequest,
    db: Session = Depends(get_db),
) -> RunOptimizerResponse:
    if payload.source_type not in ALLOWED_SOURCE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid source_type")
    _validate_month_order(payload.from_month, payload.to_month)

    try:
        resolved_source, recs = run_optimizer(db, payload)
    except ValueError as exc:
        logger.warning("Optimizer validation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        logger.error("DB error during optimizer run", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error during optimizer run", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    items = [
        RecommendationItem(
            policy_id=r.policy_id,
            sku_id=r.sku_id,
            location_id=r.location_id,
            year_month=r.year_month.strftime("%Y-%m"),
            source_type=r.source_type,
            source_id=r.source_id,
            service_level_target=float(r.service_level_target) if r.service_level_target is not None else None,
            safety_stock_units=float(r.safety_stock_units) if r.safety_stock_units is not None else None,
            cycle_stock_units=float(r.cycle_stock_units) if r.cycle_stock_units is not None else None,
            target_stock_units=float(r.target_stock_units) if r.target_stock_units is not None else None,
            created_at=r.created_at.isoformat(),
        )
        for r in recs
    ]

    return RunOptimizerResponse(
        source_type=payload.source_type,
        source_id=resolved_source,
        from_month=payload.from_month,
        to_month=payload.to_month,
        total_policies=len(items),
        recommendations=items,
    )


@router.get("/recommendations", response_model=ListRecommendationsResponse)
def list_recommendations_endpoint(
    sku_id: Optional[str] = Query(default=None),
    source_type: Optional[str] = Query(default=None),
    source_id: Optional[str] = Query(default=None),
    from_month: Optional[str] = Query(default=None),
    to_month: Optional[str] = Query(default=None),
    limit: int = Query(default=100),
    db: Session = Depends(get_db),
) -> ListRecommendationsResponse:
    try:
        recs = list_recommendations(db, sku_id, source_type, source_id, from_month, to_month, limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        logger.error("DB error listing recommendations", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error listing recommendations", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    items = [
        RecommendationItem(
            policy_id=r.policy_id,
            sku_id=r.sku_id,
            location_id=r.location_id,
            year_month=r.year_month.strftime("%Y-%m"),
            source_type=r.source_type,
            source_id=r.source_id,
            service_level_target=float(r.service_level_target) if r.service_level_target is not None else None,
            safety_stock_units=float(r.safety_stock_units) if r.safety_stock_units is not None else None,
            cycle_stock_units=float(r.cycle_stock_units) if r.cycle_stock_units is not None else None,
            target_stock_units=float(r.target_stock_units) if r.target_stock_units is not None else None,
            created_at=r.created_at.isoformat(),
        )
        for r in recs
    ]
    return ListRecommendationsResponse(recommendations=items)
