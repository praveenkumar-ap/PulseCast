from sqlalchemy import Boolean, Column, Integer, Numeric, Text, TIMESTAMP

from ..models import Base


class IndicatorCatalog(Base):
    """ORM model for indicators.catalog."""

    __tablename__ = "catalog"
    __table_args__ = {"schema": "indicators"}

    indicator_id: str = Column(Text, primary_key=True)
    name: str | None = Column(Text, nullable=True)
    description: str | None = Column(Text, nullable=True)
    category: str | None = Column(Text, nullable=True)
    frequency: str | None = Column(Text, nullable=True)
    provider: str | None = Column(Text, nullable=True)
    owner_team: str | None = Column(Text, nullable=True)
    owner_contact: str | None = Column(Text, nullable=True)
    geo_scope: str | None = Column(Text, nullable=True)
    unit: str | None = Column(Text, nullable=True)
    is_leading_indicator: bool | None = Column(Boolean, nullable=True)
    default_lead_months: Numeric | None = Column(Numeric, nullable=True)
    sla_freshness_hours: int | None = Column(Integer, nullable=True)
    sla_coverage_notes: str | None = Column(Text, nullable=True)
    license_type: str | None = Column(Text, nullable=True)
    cost_model: str | None = Column(Text, nullable=True)
    cost_estimate_per_month: Numeric | None = Column(Numeric, nullable=True)
    status: str | None = Column(Text, nullable=True)
    is_external: bool | None = Column(Boolean, nullable=True)
    is_byo: bool | None = Column(Boolean, nullable=True)
    tags: str | None = Column(Text, nullable=True)
    connector_type: str | None = Column(Text, nullable=True)
    connector_config: str | None = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)


class IndicatorQuality(Base):
    """ORM model for indicators.quality."""

    __tablename__ = "quality"
    __table_args__ = {"schema": "indicators"}

    indicator_id: str = Column(Text, primary_key=True)
    metric_date = Column(TIMESTAMP, nullable=True)
    correlation_score = Column(Numeric, nullable=True)
    correlation_stability_score = Column(Numeric, nullable=True)
    importance_score = Column(Numeric, nullable=True)
    causality_score = Column(Numeric, nullable=True)
    data_completeness_pct = Column(Numeric, nullable=True)
    lead_quality_score = Column(Numeric, nullable=True)
    last_correlation_range = Column(Text, nullable=True)
    last_eval_at = Column(TIMESTAMP, nullable=True)
    is_recommended = Column(Boolean, nullable=True)
    notes = Column(Text, nullable=True)


class IndicatorFreshness(Base):
    """ORM model for indicators.freshness."""

    __tablename__ = "freshness"
    __table_args__ = {"schema": "indicators"}

    indicator_id: str = Column(Text, primary_key=True)
    snapshot_time = Column(TIMESTAMP, nullable=True)
    last_data_time = Column(TIMESTAMP, nullable=True)
    lag_hours = Column(Numeric, nullable=True)
    is_within_sla = Column(Boolean, nullable=True)
    miss_count = Column(Numeric, nullable=True)
    late_count = Column(Numeric, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)


class IndicatorTrustScore(Base):
    """Read-only ORM model for indicators.trust_scores."""

    __tablename__ = "trust_scores"
    __table_args__ = {"schema": "indicators"}

    indicator_id: str = Column(Text, primary_key=True)
    trust_score = Column(Numeric, nullable=True)
    lead_quality_score = Column(Numeric, nullable=True)
    stability_component = Column(Numeric, nullable=True)
    freshness_component = Column(Numeric, nullable=True)
    correlation_score = Column(Numeric, nullable=True)
    correlation_stability_score = Column(Numeric, nullable=True)
    importance_score = Column(Numeric, nullable=True)
    causality_score = Column(Numeric, nullable=True)
    data_completeness_pct = Column(Numeric, nullable=True)
    last_correlation_range = Column(Text, nullable=True)
    last_eval_at = Column(TIMESTAMP, nullable=True)
    is_recommended = Column(Boolean, nullable=True)
    notes = Column(Text, nullable=True)
    snapshot_time = Column(TIMESTAMP, nullable=True)
    last_data_time = Column(TIMESTAMP, nullable=True)
    lag_hours = Column(Numeric, nullable=True)
    is_within_sla = Column(Boolean, nullable=True)
    miss_count = Column(Numeric, nullable=True)
    late_count = Column(Numeric, nullable=True)
