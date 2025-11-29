import logging
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from passlib.hash import pbkdf2_sha256
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models.auth import AuthUser

logger = logging.getLogger(__name__)


def _ensure_schema(db: Session) -> None:
    """Create schema/table if not present (lightweight bootstrap)."""
    try:
        db.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
        db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS auth.users (
                    id UUID PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NULL,
                    organization TEXT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'PLANNER',
                    created_at TIMESTAMP NULL
                )
                """
            )
        )
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to ensure auth schema/table", exc_info=exc)
        raise


def _hash_password(password: str) -> str:
    # Use PBKDF2-SHA256 to avoid bcrypt 72-byte limit but keep strong hashing.
    return pbkdf2_sha256.hash(password)


def _verify_password(password: str, hashed: str) -> bool:
    return pbkdf2_sha256.verify(password, hashed)


def create_user(
    db: Session, email: str, password: str, full_name: Optional[str], organization: Optional[str]
) -> AuthUser:
    _ensure_schema(db)
    normalized_email = email.lower().strip()
    if len(password) > 256:
        raise ValueError("Password must be at most 256 characters")
    existing = (
        db.query(AuthUser).filter(AuthUser.email == normalized_email).limit(1).one_or_none()
    )
    if existing:
        raise ValueError("User already exists")
    user = AuthUser(
        id=uuid4(),
        email=normalized_email,
        full_name=full_name,
        organization=organization,
        password_hash=_hash_password(password),
        role="PLANNER",
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[AuthUser]:
    _ensure_schema(db)
    normalized_email = email.lower().strip()
    user = (
        db.query(AuthUser).filter(AuthUser.email == normalized_email).limit(1).one_or_none()
    )
    if not user:
        return None
    if not _verify_password(password, user.password_hash):
        return None
    return user
