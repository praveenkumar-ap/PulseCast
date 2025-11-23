from sqlalchemy import Column, Date, Integer, Numeric, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID

from ..models import Base


class InventoryParameter(Base):
    """ORM model for inventory.parameters."""

    __tablename__ = "parameters"
    __table_args__ = {"schema": "inventory"}

    sku_id = Column(Text, primary_key=True)
    location_id = Column(Text, nullable=True)
    service_level_target = Column(Numeric, nullable=True)
    lead_time_days = Column(Integer, nullable=True)
    review_period_days = Column(Integer, nullable=True)
    min_order_qty = Column(Numeric, nullable=True)
    max_order_qty = Column(Numeric, nullable=True)


class InventoryRecommendation(Base):
    """ORM model for inventory.recommendations."""

    __tablename__ = "recommendations"
    __table_args__ = {"schema": "inventory"}

    policy_id = Column(UUID(as_uuid=True), primary_key=True)
    sku_id = Column(Text, nullable=False)
    location_id = Column(Text, nullable=True)
    year_month = Column(Date, nullable=False)
    source_type = Column(Text, nullable=False)
    source_id = Column(Text, nullable=True)
    service_level_target = Column(Numeric, nullable=True)
    safety_stock_units = Column(Numeric, nullable=True)
    cycle_stock_units = Column(Numeric, nullable=True)
    target_stock_units = Column(Numeric, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
