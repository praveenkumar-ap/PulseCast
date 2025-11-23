from sqlalchemy import Column, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID

from ..models import Base


class Alert(Base):
    """ORM model for alerts.alerts."""

    __tablename__ = "alerts"
    __table_args__ = {"schema": "alerts"}

    alert_id = Column(UUID(as_uuid=True), primary_key=True)
    indicator_id = Column(Text, nullable=True)
    sku_id = Column(Text, nullable=True)
    geo_id = Column(Text, nullable=True)
    alert_type = Column(Text, nullable=False)
    severity = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    message = Column(Text, nullable=True)
    triggered_at = Column(TIMESTAMP, nullable=False)
    acknowledged_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)
