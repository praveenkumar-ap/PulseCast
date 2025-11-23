from sqlalchemy import Column, Date, Numeric, Text, TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SkuForecast(Base):
    """ORM model for analytics.sku_forecasts."""

    __tablename__ = "sku_forecasts"
    __table_args__ = {"schema": "analytics"}

    sku_id = Column(Text, primary_key=True)
    year_month = Column(Date, primary_key=True)
    p10 = Column(Numeric)
    p50 = Column(Numeric)
    p90 = Column(Numeric)
    run_id = Column(Text, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False)
