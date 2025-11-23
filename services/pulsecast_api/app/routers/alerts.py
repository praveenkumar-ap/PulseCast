import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.rbac import require_roles
from ..repositories.alerts_repo import (
    VALID_SEVERITIES,
    VALID_STATUSES,
    acknowledge_alert,
    get_alert_by_id,
    list_alerts,
)
from ..schemas.alerts import AcknowledgeAlertRequest, AlertListResponse, AlertSchema

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    dependencies=[Depends(require_roles("PLANNER", "SOP_APPROVER", "DATA_SCIENTIST", "ADMIN", "SUPPORT_OPERATOR"))],
)


@router.get("", response_model=AlertListResponse)
def get_alerts(
    status: Optional[str] = Query(default=None, description="Filter by status"),
    severity: Optional[str] = Query(default=None, description="Filter by severity"),
    limit: int = Query(default=50, description="Max rows to return"),
    db: Session = Depends(get_db),
) -> AlertListResponse:
    """List alerts with optional filters."""
    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status filter")
    if severity and severity not in VALID_SEVERITIES:
        raise HTTPException(status_code=400, detail="Invalid severity filter")

    try:
        alerts = list_alerts(db, status, severity, limit)
    except SQLAlchemyError as exc:
        logger.error("DB error listing alerts", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error listing alerts", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    return AlertListResponse(alerts=[AlertSchema.model_validate(a) for a in alerts])


@router.get("/{alert_id}", response_model=AlertSchema)
def get_alert(alert_id: str, db: Session = Depends(get_db)) -> AlertSchema:
    """Fetch a single alert by ID."""
    try:
        alert_uuid = UUID(alert_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid alert_id") from exc

    try:
        alert = get_alert_by_id(db, alert_uuid)
    except SQLAlchemyError as exc:
        logger.error("DB error fetching alert %s", alert_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    return AlertSchema.model_validate(alert)


@router.post("/{alert_id}/acknowledge", response_model=AlertSchema)
def acknowledge(
    alert_id: str,
    payload: AcknowledgeAlertRequest,
    db: Session = Depends(get_db),
) -> AlertSchema:
    """Acknowledge an alert by ID."""
    try:
        alert_uuid = UUID(alert_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid alert_id") from exc

    try:
        alert = acknowledge_alert(db, alert_uuid)
    except SQLAlchemyError as exc:
        logger.error("DB error acknowledging alert %s", alert_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    logger.info("Alert %s acknowledged by %s", alert_id, payload.actor)
    return AlertSchema.model_validate(alert)
