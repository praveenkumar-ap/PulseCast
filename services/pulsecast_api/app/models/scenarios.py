from sqlalchemy import Column, Date, Numeric, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID

from ..models import Base


STATUS_DRAFT = "DRAFT"
STATUS_ACTIVE = "ACTIVE"
STATUS_ARCHIVED = "ARCHIVED"
ALLOWED_STATUSES = {STATUS_DRAFT, STATUS_ACTIVE, STATUS_ARCHIVED}


class ScenarioHeader(Base):
    """ORM model for scenarios.header."""

    __tablename__ = "header"
    __table_args__ = {"schema": "scenarios"}

    scenario_id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Text, nullable=False)
    base_run_id = Column(Text, nullable=True)
    uplift_percent = Column(Numeric, nullable=True)
    created_by = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)


class ScenarioResult(Base):
    """ORM model for scenarios.results."""

    __tablename__ = "results"
    __table_args__ = {"schema": "scenarios"}

    scenario_id = Column(UUID(as_uuid=True), primary_key=True)
    sku_id = Column(Text, primary_key=True)
    year_month = Column(Date, primary_key=True)
    base_run_id = Column(Text, nullable=True)
    p10 = Column(Numeric, nullable=False)
    p50 = Column(Numeric, nullable=False)
    p90 = Column(Numeric, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
