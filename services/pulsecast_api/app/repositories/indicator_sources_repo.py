from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from ..models.indicator_sources import IndicatorSeries, IndicatorSource


def list_sources(db: Session, status: Optional[str] = None) -> list[IndicatorSource]:
    query = db.query(IndicatorSource)
    if status:
        query = query.filter(IndicatorSource.status == status)
    return query.order_by(IndicatorSource.code).all()


def query_series(
    db: Session,
    source_code: Optional[str] = None,
    indicator_code: Optional[str] = None,
    geo_key: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    limit: int = 500,
) -> list[IndicatorSeries]:
    query = db.query(IndicatorSeries)
    if source_code:
        query = query.filter(IndicatorSeries.source_code == source_code)
    if indicator_code:
        query = query.filter(IndicatorSeries.indicator_code == indicator_code)
    if geo_key:
        query = query.filter(IndicatorSeries.geo_key == geo_key)
    if from_date:
        query = query.filter(IndicatorSeries.as_of_date >= from_date)
    if to_date:
        query = query.filter(IndicatorSeries.as_of_date <= to_date)
    return query.order_by(IndicatorSeries.as_of_date.desc()).limit(limit).all()
