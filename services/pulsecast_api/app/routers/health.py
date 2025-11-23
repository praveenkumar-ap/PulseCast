import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "env": settings.environment}


@router.get("/readyz")
def readyz(db: Session = Depends(get_db)) -> dict:
    checks = {}
    try:
        db.execute(text("select 1"))
        checks["db"] = "ok"
        return {"status": "ready", "checks": checks}
    except SQLAlchemyError as exc:
        logger.error("Readiness DB check failed", exc_info=exc)
        checks["db"] = "failed"
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "checks": checks, "details": "db check failed"},
        ) from exc
