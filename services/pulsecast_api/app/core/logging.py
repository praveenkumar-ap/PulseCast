import logging
from typing import Optional

from .config import settings


def configure_logging(level: Optional[str] = None) -> None:
    """Configure application-wide logging."""
    log_level = (level or settings.log_level).upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger."""
    return logging.getLogger(name)
