from sqlalchemy import Column, Integer, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID

from ..models import Base


class APIAuditLog(Base):
    """ORM for platform.api_audit_log."""

    __tablename__ = "api_audit_log"
    __table_args__ = {"schema": "platform"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(Text, nullable=True)
    user_id = Column(Text, nullable=True)
    user_role = Column(Text, nullable=True)
    path = Column(Text, nullable=False)
    method = Column(Text, nullable=False)
    status_code = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    action = Column(Text, nullable=True)
    entity_type = Column(Text, nullable=True)
    entity_id = Column(Text, nullable=True)
    payload_hash = Column(Text, nullable=True)
