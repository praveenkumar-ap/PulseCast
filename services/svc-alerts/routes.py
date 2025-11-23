import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import get_session
from models import Alert
from schemas import AckRequest, AlertListResponse, AlertSchema

logger = logging.getLogger(__name__)
router = APIRouter()

VALID_STATUSES = {"OPEN", "ACKNOWLEDGED", "RESOLVED"}
VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
DEFAULT_LIMIT = 50
MAX_LIMIT = 200


@router.get("/health")
def health() -> dict:
    """Health check endpoint."""
    try:
        return {"status": "ok", "service": "svc-alerts"}
    except Exception as exc:  # noqa: BLE001
        logger.error("Health check failed", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


def _parse_uuid(value: str, field_name: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        logger.warning("Invalid UUID for %s: %s", field_name, value)
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}") from exc


@router.get("/alerts", response_model=AlertListResponse)
def list_alerts(
    status: Optional[str] = Query(default=None, description="Filter by status"),
    severity: Optional[str] = Query(default=None, description="Filter by severity"),
    limit: int = Query(default=DEFAULT_LIMIT, description="Max rows to return, default 50"),
    db: Session = Depends(get_session),
) -> AlertListResponse:
    """List alerts with optional filters."""
    logger.info("Listing alerts status=%s severity=%s limit=%s", status, severity, limit)

    if status and status not in VALID_STATUSES:
        logger.warning("Invalid status filter: %s", status)
        raise HTTPException(status_code=400, detail="Invalid status filter")
    if severity and severity not in VALID_SEVERITIES:
        logger.warning("Invalid severity filter: %s", severity)
        raise HTTPException(status_code=400, detail="Invalid severity filter")

    safe_limit = min(limit, MAX_LIMIT)

    conditions = []
    if status:
        conditions.append(Alert.status == status)
    if severity:
        conditions.append(Alert.severity == severity)

    stmt = (
        select(Alert)
        .where(and_(*conditions)) if conditions else select(Alert)
    ).order_by(Alert.triggered_at.desc()).limit(safe_limit)

    try:
        result: List[Alert] = list(db.execute(stmt).scalars())
    except SQLAlchemyError as exc:
        logger.error("Failed to fetch alerts", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    return AlertListResponse(alerts=[AlertSchema.model_validate(row) for row in result])


@router.get("/alerts/{alert_id}", response_model=AlertSchema)
def get_alert(alert_id: str, db: Session = Depends(get_session)) -> AlertSchema:
    """Fetch a single alert by ID."""
    alert_uuid = _parse_uuid(alert_id, "alert_id")
    stmt = select(Alert).where(Alert.alert_id == alert_uuid)

    try:
        alert: Optional[Alert] = db.execute(stmt).scalar_one_or_none()
    except SQLAlchemyError as exc:
        logger.error("Failed to fetch alert %s", alert_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    return AlertSchema.model_validate(alert)


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertSchema)
def acknowledge_alert(
    alert_id: str,
    payload: AckRequest,
    db: Session = Depends(get_session),
) -> AlertSchema:
    """Acknowledge an alert by ID."""
    alert_uuid = _parse_uuid(alert_id, "alert_id")
    stmt = select(Alert).where(Alert.alert_id == alert_uuid)

    try:
        alert: Optional[Alert] = db.execute(stmt).scalar_one_or_none()
    except SQLAlchemyError as exc:
        logger.error("Failed to fetch alert %s for acknowledgment", alert_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    if alert.status in {"ACKNOWLEDGED", "RESOLVED"}:
        logger.info("Alert %s already %s", alert_id, alert.status)
        return AlertSchema.model_validate(alert)

    now = datetime.now(timezone.utc)
    alert.status = "ACKNOWLEDGED"
    alert.acknowledged_at = now
    alert.updated_at = now

    try:
        db.add(alert)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to acknowledge alert %s", alert_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    return AlertSchema.model_validate(alert)
