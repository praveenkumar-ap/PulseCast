import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.rbac import require_roles
from ..schemas.explanations import (
    ExplainRunRequest,
    ExplainScenarioRequest,
    RunExplanation,
    ScenarioExplanation,
)
from ..services.explanation_service import explain_run, explain_scenario

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/explain",
    tags=["explain"],
    dependencies=[Depends(require_roles("PLANNER", "SOP_APPROVER", "DATA_SCIENTIST", "ADMIN"))],
)


@router.post("/run", response_model=RunExplanation)
def explain_run_endpoint(payload: ExplainRunRequest, db: Session = Depends(get_db)) -> RunExplanation:
    if not payload.run_id:
        raise HTTPException(status_code=400, detail="run_id is required")
    try:
        return explain_run(db, payload.run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        logger.error("DB error explaining run %s", payload.run_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error explaining run %s", payload.run_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.post("/scenario", response_model=ScenarioExplanation)
def explain_scenario_endpoint(payload: ExplainScenarioRequest, db: Session = Depends(get_db)) -> ScenarioExplanation:
    scenario_id = payload.scenario_id
    try:
        return explain_scenario(db, scenario_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        logger.error("DB error explaining scenario %s", scenario_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error explaining scenario %s", scenario_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
