from sqlalchemy import Column, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID

from ..models import Base


class AuthUser(Base):
    """Minimal auth user table for signup/login (no tokens yet)."""

    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(Text, unique=True, nullable=False)
    full_name = Column(Text, nullable=True)
    organization = Column(Text, nullable=True)
    password_hash = Column(Text, nullable=False)
    role = Column(Text, nullable=False, default="PLANNER")
    created_at = Column(TIMESTAMP, nullable=True)
