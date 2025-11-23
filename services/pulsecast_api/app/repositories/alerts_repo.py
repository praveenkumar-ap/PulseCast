import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models.alerts import Alert

logger = logging.getLogger(__name__)

VALID_STATUSES = {"OPEN", "ACKNOWLEDGED", "RESOLVED"}
VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
MAX_LIMIT = 200


def list_alerts(db: Session, status: Optional[str], severity: Optional[str], limit: int) -> List[Alert]:
    safe_limit = min(limit, MAX_LIMIT)
    stmt = select(Alert).order_by(Alert.triggered_at.desc()).limit(safe_limit)
    if status:
        stmt = stmt.where(Alert.status == status)
    if severity:
        stmt = stmt.where(Alert.severity == severity)

    try:
        return list(db.execute(stmt).scalars())
    except SQLAlchemyError as exc:
        logger.error("Failed to list alerts", exc_info=exc)
        raise


def get_alert_by_id(db: Session, alert_id: UUID) -> Optional[Alert]:
    stmt = select(Alert).where(Alert.alert_id == alert_id)
    try:
        return db.execute(stmt).scalar_one_or_none()
    except SQLAlchemyError as exc:
        logger.error("Failed to get alert %s", alert_id, exc_info=exc)
        raise


def acknowledge_alert(db: Session, alert_id: UUID) -> Optional[Alert]:
    alert = get_alert_by_id(db, alert_id)
    if alert is None:
        return None
    if alert.status in {"ACKNOWLEDGED", "RESOLVED"}:
        return alert

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
        raise
    return alert


def create_indicator_spike_alert(
    db: Session,
    indicator_id: str,
    severity: str,
    payload: dict,
) -> Alert:
    """Create a spike alert for indicator events."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    alert = Alert(
        alert_id=None,
        indicator_id=indicator_id,
        sku_id=None,
        geo_id=None,
        alert_type="LEADING_INDICATOR_SPIKE",
        severity=severity,
        status="OPEN",
        message="Leading indicator spike detected",
        triggered_at=now,
        acknowledged_at=None,
        created_at=now,
        updated_at=now,
    )
    try:
        db.add(alert)
        db.commit()
        return alert
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to create indicator spike alert", exc_info=exc)
        raise
