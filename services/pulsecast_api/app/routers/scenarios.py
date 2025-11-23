import json
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.rbac import require_roles
from ..models.scenarios import ALLOWED_STATUSES
from ..repositories.scenarios_repo import (
    create_uplift_scenario,
    get_scenario_with_results,
    list_scenarios,
)
from ..repositories.scenarios_ledger_repo import (
    append_event,
    list_events,
)
from ..schemas.scenarios import (
    CreateScenarioRequest,
    CreateScenarioResponse,
    ScenarioDetailResponse,
    ScenarioHeaderModel,
    ScenarioLedgerEvent,
    ScenarioLedgerEventCreate,
    ScenarioLedgerListResponse,
    ScenarioListResponse,
    ScenarioResultItem,
    ScenarioSummary,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/scenarios",
    tags=["scenarios"],
    dependencies=[Depends(require_roles("PLANNER", "SOP_APPROVER", "DATA_SCIENTIST", "ADMIN"))],
)


def _validate_month_order(from_month: str, to_month: str) -> None:
    if from_month > to_month:
        raise HTTPException(status_code=400, detail="from_month cannot be after to_month")


def _validate_status_filter(status: Optional[str]) -> None:
    if status and status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status filter")


@router.post("", response_model=CreateScenarioResponse)
def create_scenario(
    payload: CreateScenarioRequest,
    db: Session = Depends(get_db),
) -> CreateScenarioResponse:
    """Create an uplift scenario based on existing forecasts."""
    _validate_month_order(payload.from_month, payload.to_month)
    try:
        header, results = create_uplift_scenario(db, payload)
        # Append CREATE event to ledger
        assumptions = json.dumps(
            {
                "uplift_percent": payload.uplift_percent,
                "from_month": payload.from_month,
                "to_month": payload.to_month,
                "sku_ids": payload.sku_ids,
                "base_run_id": payload.base_run_id,
            }
        )
        append_event(
            db=db,
            scenario_id=header.scenario_id,
            action_type="CREATE",
            actor=payload.created_by,
            actor_role=None,
            assumptions=assumptions,
            comments=payload.description or "",
            now=datetime.utcnow(),
        )
    except ValueError as exc:
        logger.warning("Scenario creation validation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        logger.error("DB error creating scenario", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error creating scenario", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    sku_ids = sorted({r.sku_id for r in results})
    return CreateScenarioResponse(
        scenario_id=header.scenario_id,
        name=header.name,
        status=header.status,
        base_run_id=header.base_run_id or "",
        uplift_percent=float(header.uplift_percent) if header.uplift_percent is not None else 0.0,
        from_month=payload.from_month,
        to_month=payload.to_month,
        sku_ids=sku_ids,
        total_rows=len(results),
    )


@router.get("", response_model=ScenarioListResponse)
def list_scenarios_endpoint(
    status: Optional[str] = Query(default=None, description="Filter by status"),
    limit: int = Query(default=20, description="Max rows to return"),
    db: Session = Depends(get_db),
) -> ScenarioListResponse:
    """List scenarios with optional status filter."""
    _validate_status_filter(status)
    try:
        rows = list_scenarios(db, status, limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        logger.error("DB error listing scenarios", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error listing scenarios", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    summaries = [
        ScenarioSummary(
            scenario_id=r.scenario_id,
            name=r.name,
            status=r.status,
            base_run_id=r.base_run_id,
            uplift_percent=float(r.uplift_percent) if r.uplift_percent is not None else None,
            created_by=r.created_by,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat(),
        )
        for r in rows
    ]
    return ScenarioListResponse(scenarios=summaries)


@router.get("/{scenario_id}", response_model=ScenarioDetailResponse)
def get_scenario(
    scenario_id: str,
    db: Session = Depends(get_db),
) -> ScenarioDetailResponse:
    """Return scenario header and results."""
    try:
        scenario_uuid = UUID(scenario_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid scenario_id") from exc

    try:
        header, results = get_scenario_with_results(db, scenario_uuid)
    except SQLAlchemyError as exc:
        logger.error("DB error fetching scenario %s", scenario_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    if header is None:
        raise HTTPException(status_code=404, detail="Scenario not found")

    header_schema = ScenarioHeaderModel(
        scenario_id=header.scenario_id,
        name=header.name,
        description=header.description,
        status=header.status,
        base_run_id=header.base_run_id,
        uplift_percent=float(header.uplift_percent) if header.uplift_percent is not None else None,
        created_by=header.created_by,
        created_at=header.created_at.isoformat(),
        updated_at=header.updated_at.isoformat(),
    )
    result_items = [
        ScenarioResultItem(
            sku_id=r.sku_id,
            year_month=r.year_month.strftime("%Y-%m"),
            base_run_id=r.base_run_id,
            p10=float(r.p10),
            p50=float(r.p50),
            p90=float(r.p90),
            created_at=r.created_at.isoformat(),
        )
        for r in results
    ]
    return ScenarioDetailResponse(header=header_schema, results=result_items)


@router.get("/{scenario_id}/ledger", response_model=ScenarioLedgerListResponse)
def get_ledger(
    scenario_id: str,
    limit: int = Query(default=50),
    db: Session = Depends(get_db),
) -> ScenarioLedgerListResponse:
    try:
        scenario_uuid = UUID(scenario_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid scenario_id") from exc

    try:
        events = list_events(db, scenario_uuid, limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        logger.error("DB error fetching ledger for scenario %s", scenario_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    resp = [
        ScenarioLedgerEvent(
            ledger_id=e.ledger_id,
            scenario_id=e.scenario_id,
            version_seq=e.version_seq,
            action_type=e.action_type,
            actor=e.actor,
            actor_role=e.actor_role,
            assumptions=e.assumptions,
            comments=e.comments,
            created_at=e.created_at,
        )
        for e in events
    ]
    return ScenarioLedgerListResponse(events=resp)


@router.post("/{scenario_id}/ledger", response_model=ScenarioLedgerEvent)
def append_ledger(
    scenario_id: str,
    payload: ScenarioLedgerEventCreate,
    db: Session = Depends(get_db),
) -> ScenarioLedgerEvent:
    try:
        scenario_uuid = UUID(scenario_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid scenario_id") from exc

    try:
        event = append_event(
            db=db,
            scenario_id=scenario_uuid,
            action_type=payload.action_type,
            actor=payload.actor,
            actor_role=payload.actor_role,
            assumptions=payload.assumptions,
            comments=payload.comments,
            now=datetime.utcnow(),
        )
    except ValueError as exc:
        if str(exc) == "Scenario not found":
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        logger.error("DB error appending ledger for scenario %s", scenario_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error appending ledger for scenario %s", scenario_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

    return ScenarioLedgerEvent(
        ledger_id=event.ledger_id,
        scenario_id=event.scenario_id,
        version_seq=event.version_seq,
        action_type=event.action_type,
        actor=event.actor,
        actor_role=event.actor_role,
        assumptions=event.assumptions,
        comments=event.comments,
        created_at=event.created_at,
    )
