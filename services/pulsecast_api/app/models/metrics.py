from sqlalchemy import Column, Date, Numeric, Integer, Text, TIMESTAMP
from ..models import Base


class ForecastRunSummary(Base):
    """ORM model for analytics.forecast_run_summary."""

    __tablename__ = "forecast_run_summary"
    __table_args__ = {"schema": "analytics"}

    run_id = Column(Text, primary_key=True)
    run_type = Column(Text, nullable=True)
    horizon_start_month = Column(Date, nullable=True)
    horizon_end_month = Column(Date, nullable=True)
    skus_covered = Column(Integer, nullable=True)
    mape = Column(Numeric, nullable=True)
    wape = Column(Numeric, nullable=True)
    bias = Column(Numeric, nullable=True)
    mae = Column(Numeric, nullable=True)
    mape_vs_baseline_delta = Column(Numeric, nullable=True)
    wape_vs_baseline_delta = Column(Numeric, nullable=True)
    computed_at = Column(TIMESTAMP, nullable=True)


class ForecastAccuracyBySkuMonth(Base):
    """ORM model for analytics.forecast_accuracy_by_sku_month."""

    __tablename__ = "forecast_accuracy_by_sku_month"
    __table_args__ = {"schema": "analytics"}

    run_id = Column(Text, primary_key=True)
    sku_id = Column(Text, primary_key=True)
    year_month = Column(Date, primary_key=True)
    actual_units = Column(Numeric, nullable=True)
    forecast_p50_units = Column(Numeric, nullable=True)
    abs_error = Column(Numeric, nullable=True)
    ape = Column(Numeric, nullable=True)


class ValueImpactSummary(Base):
    """ORM model for analytics.value_impact_summary."""

    __tablename__ = "value_impact_summary"
    __table_args__ = {"schema": "analytics"}

    run_id = Column(Text, primary_key=True)
    rev_uplift_estimate = Column(Numeric, nullable=True)
    scrap_avoidance_estimate = Column(Numeric, nullable=True)
    wc_savings_estimate = Column(Numeric, nullable=True)
    productivity_savings_estimate = Column(Numeric, nullable=True)
    assumptions_json = Column(Text, nullable=True)
    computed_at = Column(TIMESTAMP, nullable=True)
