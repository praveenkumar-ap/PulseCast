from datetime import date, datetime

from sqlalchemy import Column, Date, Numeric, Text, TIMESTAMP

from ..models import Base


class Forecast(Base):
    """ORM model for analytics.sku_forecasts."""

    __tablename__ = "sku_forecasts"
    __table_args__ = {"schema": "analytics"}

    sku_id = Column(Text, primary_key=True)
    year_month = Column(Date, primary_key=True)
    p10 = Column(Numeric, nullable=True)
    p50 = Column(Numeric, nullable=True)
    p90 = Column(Numeric, nullable=True)
    run_id = Column(Text, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False)
