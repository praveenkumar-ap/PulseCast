from sqlalchemy import Column, Date, Numeric, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID

from ..models import Base


class RunValueSummary(Base):
    """Read-only ORM model for value.run_value_summary."""

    __tablename__ = "run_value_summary"
    __table_args__ = {"schema": "value"}

    run_id: str = Column(Text, primary_key=True)
    run_type = Column(Text, nullable=True)
    family_id = Column(Text, nullable=True)
    family_name = Column(Text, nullable=True)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    forecast_accuracy_uplift_pct = Column(Numeric, nullable=True)
    revenue_uplift_estimate = Column(Numeric, nullable=True)
    scrap_avoidance_estimate = Column(Numeric, nullable=True)
    working_capital_savings_estimate = Column(Numeric, nullable=True)
    planner_productivity_hours_saved = Column(Numeric, nullable=True)
    total_value_estimate = Column(Numeric, nullable=True)
    case_label = Column(Text, nullable=True)
    computed_at = Column(TIMESTAMP, nullable=True)


class ScenarioValueSummary(Base):
    """Read-only ORM model for value.scenario_value_summary."""

    __tablename__ = "scenario_value_summary"
    __table_args__ = {"schema": "value"}

    # scenario_id is a UUID in the db view/table; map as UUID for proper typing.
    scenario_id = Column(UUID(as_uuid=True), primary_key=True)
    scenario_name = Column(Text, nullable=True)
    base_run_id = Column(Text, nullable=True)
    status = Column(Text, nullable=True)
    family_id = Column(Text, nullable=True)
    family_name = Column(Text, nullable=True)
    expected_revenue_uplift_estimate = Column(Numeric, nullable=True)
    expected_scrap_avoidance_estimate = Column(Numeric, nullable=True)
    expected_working_capital_effect = Column(Numeric, nullable=True)
    expected_service_level_change = Column(Numeric, nullable=True)
    total_expected_value_estimate = Column(Numeric, nullable=True)
    case_label = Column(Text, nullable=True)
    rec_count = Column(Numeric, nullable=True)
    created_at = Column(TIMESTAMP, nullable=True)


class ValueBenchmark(Base):
    """Read-only ORM model for value.benchmarks."""

    __tablename__ = "benchmarks"
    __table_args__ = {"schema": "value"}

    metric_name: str = Column(Text, primary_key=True)
    scope = Column(Text, primary_key=True)
    scope_key = Column(Text, primary_key=True)
    value_numeric = Column(Numeric, nullable=True)
    value_text = Column(Text, nullable=True)
    as_of_date = Column(TIMESTAMP, nullable=True)
