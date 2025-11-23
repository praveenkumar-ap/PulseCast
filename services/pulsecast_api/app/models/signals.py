from sqlalchemy import Column, Numeric, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID

from ..models import Base


class SignalStreamRaw(Base):
    """ORM model for signals.stream_raw (raw streaming events)."""

    __tablename__ = "stream_raw"
    __table_args__ = {"schema": "signals"}

    event_id = Column(UUID(as_uuid=True), primary_key=True)
    indicator_id = Column(Text, nullable=False)
    event_time = Column(TIMESTAMP, nullable=False)
    geo = Column(Text, nullable=True)
    value = Column(Numeric, nullable=False)
    source_system = Column(Text, nullable=False)
    ingested_at = Column(TIMESTAMP, nullable=False)
    payload_json = Column(Text, nullable=True)


class SignalNowcastWindow(Base):
    """ORM model for signals.nowcast_window (read-only view)."""

    __tablename__ = "nowcast_window"
    __table_args__ = {"schema": "signals"}

    indicator_id = Column(Text, primary_key=True)
    window_start = Column(TIMESTAMP, nullable=True)
    window_end = Column(TIMESTAMP, nullable=True)
    window_value = Column(Numeric, nullable=True)
    baseline_value = Column(Numeric, nullable=True)
    delta_value = Column(Numeric, nullable=True)
    delta_pct = Column(Numeric, nullable=True)


class ExternalSignalStaging(Base):
    """ORM model for signals.external_staging (staging before replay)."""

    __tablename__ = "external_staging"
    __table_args__ = {"schema": "signals"}

    event_id = Column(UUID(as_uuid=True), primary_key=True)
    indicator_id = Column(Text, nullable=False)
    event_time = Column(TIMESTAMP, nullable=False)
    geo = Column(Text, nullable=True)
    value = Column(Numeric, nullable=False)
    source_system = Column(Text, nullable=False)
    payload_json = Column(Text, nullable=True)
