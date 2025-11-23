from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import uuid4
import re

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ..models.indicators import (
    IndicatorCatalog,
    IndicatorFreshness,
    IndicatorQuality,
    IndicatorTrustScore,
)

logger = logging.getLogger(__name__)

MAX_LIST = 500
DEFAULT_LIST = 100


def get_indicator_detail(db: Session, indicator_id: str) -> Tuple[Optional[IndicatorCatalog], Optional[IndicatorQuality], Optional[IndicatorFreshness]]:
    cat_stmt = select(IndicatorCatalog).where(IndicatorCatalog.indicator_id == indicator_id)
    qual_stmt = select(IndicatorQuality).where(IndicatorQuality.indicator_id == indicator_id)
    fresh_stmt = select(IndicatorFreshness).where(IndicatorFreshness.indicator_id == indicator_id)
    cat = db.execute(cat_stmt).scalar_one_or_none()
    qual = db.execute(qual_stmt).scalar_one_or_none()
    fresh = db.execute(fresh_stmt).scalar_one_or_none()
    return cat, qual, fresh


def list_indicators(
    db: Session,
    category: Optional[str],
    status: Optional[str],
    provider: Optional[str],
    is_byo: Optional[bool],
    is_leading_indicator: Optional[bool],
    search: Optional[str],
    limit: int,
    offset: int = 0,
) -> List[IndicatorCatalog]:
    safe_limit = min(max(limit or DEFAULT_LIST, 1), MAX_LIST)
    safe_offset = max(offset or 0, 0)
    stmt = select(IndicatorCatalog).offset(safe_offset).limit(safe_limit)
    conditions = []
    if category:
        conditions.append(IndicatorCatalog.category == category)
    if status:
        conditions.append(IndicatorCatalog.status == status)
    if provider:
        conditions.append(IndicatorCatalog.provider == provider)
    if is_byo is not None:
        conditions.append(IndicatorCatalog.is_byo == is_byo)
    if is_leading_indicator is not None:
        conditions.append(IndicatorCatalog.is_leading_indicator == is_leading_indicator)
    if search:
        like_expr = f"%{search.lower()}%"
        conditions.append(
            or_(
                IndicatorCatalog.name.ilike(like_expr),
                IndicatorCatalog.description.ilike(like_expr),
                IndicatorCatalog.tags.ilike(like_expr),
            )
        )
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.order_by(IndicatorCatalog.created_at.desc().nullslast())
    try:
        return list(db.execute(stmt).scalars())
    except SQLAlchemyError as exc:
        logger.error("Failed to list indicators", exc_info=exc)
        raise


def create_indicator(db: Session, payload) -> IndicatorCatalog:
    now = datetime.utcnow()
    cat = IndicatorCatalog(
        indicator_id=payload.indicator_id,
        name=payload.name,
        description=payload.description,
        category=payload.category,
        frequency=payload.frequency,
        provider=payload.provider,
        owner_team=payload.owner_team,
        owner_contact=payload.owner_contact,
        geo_scope=payload.geo_scope,
        unit=payload.unit,
        is_leading_indicator=payload.is_leading_indicator,
        default_lead_months=payload.default_lead_months,
        sla_freshness_hours=payload.sla_freshness_hours,
        sla_coverage_notes=payload.sla_coverage_notes,
        license_type=payload.license_type,
        cost_model=payload.cost_model,
        cost_estimate_per_month=payload.cost_estimate_per_month,
        status=payload.status,
        is_external=payload.is_external,
        is_byo=payload.is_byo,
        tags=payload.tags,
        connector_type=payload.connector_type,
        connector_config=_stringify_config(payload.connector_config),
        created_at=now,
        updated_at=now,
    )
    try:
        db.add(cat)
        db.commit()
        return cat
    except IntegrityError as exc:
        db.rollback()
        logger.warning("Indicator %s already exists", payload.indicator_id)
        raise ValueError("Indicator already exists") from exc
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to create indicator", exc_info=exc)
        raise


def update_indicator(db: Session, indicator_id: str, payload) -> IndicatorCatalog:
    cat_stmt = select(IndicatorCatalog).where(IndicatorCatalog.indicator_id == indicator_id)
    cat = db.execute(cat_stmt).scalar_one_or_none()
    if cat is None:
        raise ValueError("Indicator not found")

    for field in [
        "name",
        "description",
        "category",
        "frequency",
        "provider",
        "owner_team",
        "owner_contact",
        "geo_scope",
        "unit",
        "is_leading_indicator",
        "default_lead_months",
        "sla_freshness_hours",
        "sla_coverage_notes",
        "license_type",
        "cost_model",
        "cost_estimate_per_month",
        "status",
        "is_external",
        "is_byo",
        "tags",
        "connector_type",
    ]:
        value = getattr(payload, field, None)
        if value is not None:
            setattr(cat, field, value)
    if getattr(payload, "connector_config", None) is not None:
        cat.connector_config = _stringify_config(payload.connector_config)
    cat.updated_at = datetime.utcnow()

    try:
        db.add(cat)
        db.commit()
        return cat
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to update indicator %s", indicator_id, exc_info=exc)
        raise


def upsert_quality(db: Session, indicator_id: str, payload) -> IndicatorQuality:
    qual_stmt = select(IndicatorQuality).where(IndicatorQuality.indicator_id == indicator_id)
    qual = db.execute(qual_stmt).scalar_one_or_none()
    if qual is None:
        qual = IndicatorQuality(indicator_id=indicator_id)
        db.add(qual)
    for field in [
        "metric_date",
        "correlation_score",
        "correlation_stability_score",
        "importance_score",
        "causality_score",
        "data_completeness_pct",
        "lead_quality_score",
        "last_correlation_range",
        "last_eval_at",
        "is_recommended",
        "notes",
    ]:
        setattr(qual, field, getattr(payload, field, None))
    try:
        db.commit()
        return qual
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to upsert quality for %s", indicator_id, exc_info=exc)
        raise


def upsert_freshness(db: Session, indicator_id: str, payload) -> IndicatorFreshness:
    fresh_stmt = select(IndicatorFreshness).where(IndicatorFreshness.indicator_id == indicator_id)
    fresh = db.execute(fresh_stmt).scalar_one_or_none()
    if fresh is None:
        fresh = IndicatorFreshness(indicator_id=indicator_id)
        db.add(fresh)

    for field in [
        "snapshot_time",
        "last_data_time",
        "lag_hours",
        "is_within_sla",
        "miss_count",
        "late_count",
    ]:
        setattr(fresh, field, getattr(payload, field, None))
    fresh.updated_at = datetime.utcnow()

    try:
        db.commit()
        return fresh
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to upsert freshness for %s", indicator_id, exc_info=exc)
        raise


def get_trust_score(db: Session, indicator_id: str) -> Optional[IndicatorTrustScore]:
    stmt = select(IndicatorTrustScore).where(IndicatorTrustScore.indicator_id == indicator_id)
    return db.execute(stmt).scalar_one_or_none()


def list_trust_scores(
    db: Session,
    min_trust_score: Optional[float],
    min_lead_quality_score: Optional[float],
    limit: int,
    offset: int = 0,
) -> List[IndicatorTrustScore]:
    safe_limit = min(max(limit or DEFAULT_LIST, 1), MAX_LIST)
    safe_offset = max(offset or 0, 0)
    stmt = select(IndicatorTrustScore).offset(safe_offset).limit(safe_limit)
    conditions = []
    if min_trust_score is not None:
        conditions.append(IndicatorTrustScore.trust_score >= min_trust_score)
    if min_lead_quality_score is not None:
        conditions.append(IndicatorTrustScore.lead_quality_score >= min_lead_quality_score)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.order_by(IndicatorTrustScore.trust_score.desc().nullslast())
    try:
        return list(db.execute(stmt).scalars())
    except SQLAlchemyError as exc:
        logger.error("Failed to list trust scores", exc_info=exc)
        raise


def register_byo_indicator(db: Session, payload) -> IndicatorCatalog:
    """Register BYOS indicator metadata only."""
    indicator_id = _generate_byo_indicator_id(payload.name)
    now = datetime.utcnow()
    cat = IndicatorCatalog(
        indicator_id=indicator_id,
        name=payload.name,
        description=payload.description,
        category=payload.category,
        frequency=payload.frequency,
        provider=payload.provider or "CUSTOM",
        owner_team=payload.owner_team,
        owner_contact=payload.owner_contact,
        geo_scope=payload.geo_scope,
        unit=payload.unit,
        is_leading_indicator=payload.is_leading_indicator,
        default_lead_months=payload.default_lead_months,
        sla_freshness_hours=payload.sla_freshness_hours,
        sla_coverage_notes=payload.sla_coverage_notes,
        license_type=payload.license_type,
        cost_model=payload.cost_model,
        cost_estimate_per_month=payload.cost_estimate_per_month,
        status=payload.status or "PENDING",
        is_external=True,
        is_byo=True,
        tags=payload.tags,
        connector_type=payload.connector_type,
        connector_config=_stringify_config(payload.connector_config),
        created_at=now,
        updated_at=now,
    )
    try:
        db.add(cat)
        db.commit()
        return cat
    except IntegrityError as exc:
        db.rollback()
        logger.warning("BYOS indicator conflict for name=%s", payload.name, exc_info=exc)
        raise ValueError("Indicator already exists") from exc
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to register BYOS indicator", exc_info=exc)
        raise


def _generate_byo_indicator_id(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return f"byos_{slug}_{uuid4().hex[:8]}"


def _stringify_config(config: Optional[Dict]) -> Optional[str]:
    if config is None:
        return None
    try:
        import json
        return json.dumps(config)
    except Exception:
        return str(config)
