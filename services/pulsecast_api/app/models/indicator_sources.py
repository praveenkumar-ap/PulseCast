from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID

from ..models import Base


class IndicatorSource(Base):
    """Generic catalog of indicator sources."""

    __tablename__ = "indicator_sources"
    __table_args__ = {"schema": "indicators"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    provider_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="ACTIVE")
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class IndicatorSeries(Base):
    """Generic time-series storage for indicator values."""

    __tablename__ = "indicator_series"
    __table_args__ = {"schema": "indicators"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("indicators.indicator_sources.id"), nullable=False)
    source_code = Column(String, nullable=False)
    indicator_code = Column(String, nullable=False)
    geo_key = Column(String, nullable=False)
    as_of_date = Column(Date, nullable=False)
    value = Column(Numeric, nullable=False)
    extra_meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
