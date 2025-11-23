from sqlalchemy import Column, Integer, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID

from ..models import Base


class ScenarioLedger(Base):
    """ORM model for scenarios.ledger (append-only)."""

    __tablename__ = "ledger"
    __table_args__ = {"schema": "scenarios"}

    ledger_id = Column(UUID(as_uuid=True), primary_key=True)
    scenario_id = Column(UUID(as_uuid=True), nullable=False)
    version_seq = Column(Integer, nullable=False)
    action_type = Column(Text, nullable=False)
    actor = Column(Text, nullable=False)
    actor_role = Column(Text, nullable=True)
    assumptions = Column(Text, nullable=True)
    comments = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
