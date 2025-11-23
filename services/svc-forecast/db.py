import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import settings

logger = logging.getLogger(__name__)


def _build_db_url() -> str:
    """Construct the SQLAlchemy database URL."""
    return (
        f"postgresql+psycopg://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )


try:
    engine = create_engine(_build_db_url(), future=True, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
except Exception as exc:  # noqa: BLE001
    logger.error("Failed to initialize database engine", exc_info=exc)
    raise


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency to provide a database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as exc:  # noqa: BLE001
        logger.error("Database session error", exc_info=exc)
        raise
    finally:
        db.close()
