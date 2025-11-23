from __future__ import annotations

import sys

from sqlalchemy.orm import Session

from services.pulsecast_api.app.core.db import SessionLocal
from services.pulsecast_api.app.core.logging import configure_logging, get_logger
from .early_warning_service import run_early_warning

logger = get_logger(__name__)


def main() -> None:
    configure_logging()
    db: Session | None = None
    try:
        db = SessionLocal()
        run_early_warning(db)
    except Exception:  # noqa: BLE001
        logger.exception("Early-warning job failed")
        sys.exit(1)
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    main()
