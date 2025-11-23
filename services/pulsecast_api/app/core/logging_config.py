import logging
from typing import Optional

from .config import settings


def configure_logging(level: Optional[str] = None) -> None:
    """Configure root logging with a consistent formatter."""
    log_level = (level or settings.log_level or "INFO").upper()
    fmt = "%(asctime)s %(levelname)s %(name)s - %(message)s"
    logging.basicConfig(level=log_level, format=fmt)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
