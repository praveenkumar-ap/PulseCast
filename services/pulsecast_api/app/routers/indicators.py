import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.rbac import require_roles
from ..repositories.indicators_repo import (
    create_indicator,
    get_indicator_detail,
    get_trust_score,
    list_indicators,
    list_trust_scores,
    register_byo_indicator,
    update_indicator,
    upsert_freshness,
    upsert_quality,
)
from ..repositories.indicator_sources_repo import list_sources, query_series
from ..schemas.indicators import (
    ByosRegisterRequest,
    CreateIndicatorRequest,
    IndicatorCatalogSchema,
    IndicatorDetail,
    IndicatorDetailResponse,
    IndicatorFreshnessSchema,
    IndicatorListResponse,
    IndicatorSummary,
    IndicatorTrustScore,
    IndicatorTrustScoreResponse,
    IndicatorTrustScoresResponse,
    IndicatorQualitySchema,
    UpdateIndicatorRequest,
    UpdateFreshnessRequest,
    UpdateQualityRequest,
)
from ..schemas.indicator_sources import (
    IndicatorSeriesResponse,
    IndicatorSourcesResponse,
    IndicatorSourceSchema,
    IndicatorSeriesRowSchema,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/indicators",
    tags=["indicators"],
    dependencies=[Depends(require_roles("PLANNER", "SOP_APPROVER", "DATA_SCIENTIST", "ADMIN"))],
)


def _map_detail(cat, qual, fresh) -> IndicatorDetail:
    return IndicatorDetail(
        catalog=IndicatorCatalogSchema.model_validate(cat),
        quality=IndicatorQualitySchema.model_validate(qual) if qual else None,
        freshness=IndicatorFreshnessSchema.model_validate(fresh) if fresh else None,
    )


@router.get("", response_model=IndicatorListResponse)
def get_indicators(
    category: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    provider: Optional[str] = Query(default=None),
    is_byo: Optional[bool] = Query(default=None),
    is_leading_indicator: Optional[bool] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=100),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
) -> IndicatorListResponse:
    try:
        cats = list_indicators(
            db=db,
            category=category,
            status=status,
            provider=provider,
            is_byo=is_byo,
            is_leading_indicator=is_leading_indicator,
            search=search,
            limit=limit,
            offset=offset,
        )
    except SQLAlchemyError as exc:
        logger.error("DB error listing indicators", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    summaries = [
        IndicatorSummary(
            indicator_id=c.indicator_id,
            name=c.name,
            category=c.category,
            provider=c.provider,
            status=c.status,
            is_byo=c.is_byo,
            tags=c.tags,
        )
        for c in cats
    ]
    return IndicatorListResponse(indicators=summaries)


@router.get("/trust", response_model=IndicatorTrustScoresResponse)
def list_trust_endpoint(
    min_trust_score: Optional[float] = Query(default=None),
    min_lead_quality_score: Optional[float] = Query(default=None),
    limit: int = Query(default=100),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
) -> IndicatorTrustScoresResponse:
    try:
        scores = list_trust_scores(db, min_trust_score, min_lead_quality_score, limit, offset)
    except SQLAlchemyError as exc:
        logger.error("DB error listing trust scores", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    return IndicatorTrustScoresResponse(scores=[IndicatorTrustScore.model_validate(s) for s in scores])


@router.get("/{indicator_id}", response_model=IndicatorDetailResponse)
def get_indicator(indicator_id: str, db: Session = Depends(get_db)) -> IndicatorDetailResponse:
    try:
        cat, qual, fresh = get_indicator_detail(db, indicator_id)
    except SQLAlchemyError as exc:
        logger.error("DB error fetching indicator %s", indicator_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    if cat is None:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return IndicatorDetailResponse(indicator=_map_detail(cat, qual, fresh))


@router.post("", response_model=IndicatorCatalogSchema, status_code=201)
def create_indicator_endpoint(payload: CreateIndicatorRequest, db: Session = Depends(get_db)) -> IndicatorCatalogSchema:
    try:
        cat = create_indicator(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        logger.error("DB error creating indicator", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    return IndicatorCatalogSchema.model_validate(cat)


@router.put("/{indicator_id}", response_model=IndicatorCatalogSchema)
def update_indicator_endpoint(
    indicator_id: str,
    payload: UpdateIndicatorRequest,
    db: Session = Depends(get_db),
) -> IndicatorCatalogSchema:
    try:
        cat = update_indicator(db, indicator_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        logger.error("DB error updating indicator %s", indicator_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    return IndicatorCatalogSchema.model_validate(cat)


@router.put("/{indicator_id}/quality", response_model=IndicatorQualitySchema)
def update_quality_endpoint(
    indicator_id: str,
    payload: UpdateQualityRequest,
    db: Session = Depends(get_db),
) -> IndicatorQualitySchema:
    try:
        qual = upsert_quality(db, indicator_id, payload)
    except SQLAlchemyError as exc:
        logger.error("DB error updating quality for %s", indicator_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    return IndicatorQualitySchema.model_validate(qual)


@router.put("/{indicator_id}/freshness", response_model=IndicatorFreshnessSchema)
def update_freshness_endpoint(
    indicator_id: str,
    payload: UpdateFreshnessRequest,
    db: Session = Depends(get_db),
) -> IndicatorFreshnessSchema:
    try:
        fresh = upsert_freshness(db, indicator_id, payload)
    except SQLAlchemyError as exc:
        logger.error("DB error updating freshness for %s", indicator_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    return IndicatorFreshnessSchema.model_validate(fresh)


@router.get("/{indicator_id}/trust", response_model=IndicatorTrustScoreResponse)
def get_trust_endpoint(indicator_id: str, db: Session = Depends(get_db)) -> IndicatorTrustScoreResponse:
    try:
        score = get_trust_score(db, indicator_id)
    except SQLAlchemyError as exc:
        logger.error("DB error fetching trust score for %s", indicator_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    if score is None:
        raise HTTPException(status_code=404, detail="Trust score not found")
    return IndicatorTrustScoreResponse(score=IndicatorTrustScore.model_validate(score))


@router.post(
    "/byos/register",
    response_model=IndicatorCatalogSchema,
    status_code=201,
    dependencies=[Depends(require_roles("DATA_SCIENTIST", "ADMIN"))],
)
def register_byo_endpoint(payload: ByosRegisterRequest, db: Session = Depends(get_db)) -> IndicatorCatalogSchema:
    try:
        cat = register_byo_indicator(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        logger.error("DB error registering BYOS indicator", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    return IndicatorCatalogSchema.model_validate(cat)


@router.get("/sources", response_model=IndicatorSourcesResponse)
def list_indicator_sources(
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
) -> IndicatorSourcesResponse:
    try:
        rows = list_sources(db, status)
    except SQLAlchemyError as exc:
        logger.error("DB error listing indicator sources", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    return IndicatorSourcesResponse(sources=[IndicatorSourceSchema.model_validate(r) for r in rows])


@router.get("/series", response_model=IndicatorSeriesResponse)
def list_indicator_series(
    source_code: Optional[str] = Query(default=None),
    indicator_code: Optional[str] = Query(default=None),
    geo_key: Optional[str] = Query(default=None),
    from_date: Optional[str] = Query(default=None),
    to_date: Optional[str] = Query(default=None),
    limit: int = Query(default=500, le=5000),
    db: Session = Depends(get_db),
) -> IndicatorSeriesResponse:
    try:
        rows = query_series(
            db=db,
            source_code=source_code,
            indicator_code=indicator_code,
            geo_key=geo_key,
            from_date=_parse_date(from_date) if from_date else None,
            to_date=_parse_date(to_date) if to_date else None,
            limit=limit,
        )
    except SQLAlchemyError as exc:
        logger.error("DB error listing indicator series", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    return IndicatorSeriesResponse(series=[IndicatorSeriesRowSchema.model_validate(r) for r in rows])


def _parse_date(val: str):
    from datetime import date

    return date.fromisoformat(val)
