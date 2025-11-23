from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID

from pydantic import BaseModel


class BaseExplanation(BaseModel):
    title: str
    short_summary: str
    key_drivers: List[str]
    risks: List[str]
    recommended_actions: List[str]
    model_used: Optional[str] = None
    is_fallback: bool = False


class RunExplanation(BaseExplanation):
    run_id: str
    metrics_snapshot: Dict


class ScenarioExplanation(BaseExplanation):
    scenario_id: str
    status: Optional[str] = None
    created_by: Optional[str] = None
    assumptions_snapshot: Dict
    ledger_summary: List[Dict]
    optimizer_summary: Optional[Dict] = None


class ExplainRunRequest(BaseModel):
    run_id: str


class ExplainScenarioRequest(BaseModel):
    scenario_id: UUID
