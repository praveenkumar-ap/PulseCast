from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.metrics import ForecastAccuracyBySkuMonth, ForecastRunSummary, ValueImpactSummary
from ..models.scenarios import ScenarioHeader, ScenarioResult
from ..models.value import RunValueSummary as RunValueSummaryModel, ScenarioValueSummary as ScenarioValueSummaryModel
from ..models.scenarios_ledger import ScenarioLedger
from ..models.inventory import InventoryRecommendation
from ..services.llm_client import LLMClientError, LLMNotConfiguredError, generate_completion
from ..schemas.explanations import (
    BaseExplanation,
    RunExplanation,
    ScenarioExplanation,
)

logger = logging.getLogger(__name__)


def _load_run_context(db: Session, run_id: str, accuracy_limit: int = 5) -> Dict:
    run_stmt = select(ForecastRunSummary).where(ForecastRunSummary.run_id == run_id).limit(1)
    run_row = db.execute(run_stmt).scalar_one_or_none()
    if not run_row:
        raise ValueError("Run not found")

    value_stmt = select(ValueImpactSummary).where(ValueImpactSummary.run_id == run_id).limit(1)
    value_row = db.execute(value_stmt).scalar_one_or_none()
    run_value_stmt = select(RunValueSummaryModel).where(RunValueSummaryModel.run_id == run_id).limit(1)
    run_value_row = db.execute(run_value_stmt).scalar_one_or_none()

    acc_stmt = (
        select(ForecastAccuracyBySkuMonth)
        .where(ForecastAccuracyBySkuMonth.run_id == run_id)
        .order_by(ForecastAccuracyBySkuMonth.abs_error.desc())
        .limit(accuracy_limit)
    )
    acc_rows = list(db.execute(acc_stmt).scalars())

    top_skus = []
    for a in acc_rows:
        top_skus.append(
            {
                "sku_id": a.sku_id,
                "year_month": a.year_month.strftime("%Y-%m"),
                "actual_units": float(a.actual_units) if a.actual_units is not None else None,
                "forecast_p50_units": float(a.forecast_p50_units) if a.forecast_p50_units is not None else None,
                "abs_error": float(a.abs_error) if a.abs_error is not None else None,
                "ape": float(a.ape) if a.ape is not None else None,
            }
        )

    context = {
        "run": {
            "run_id": run_row.run_id,
            "run_type": run_row.run_type,
            "horizon_start_month": run_row.horizon_start_month,
            "horizon_end_month": run_row.horizon_end_month,
            "skus_covered": run_row.skus_covered,
        },
        "metrics": {
            "mape": float(run_row.mape) if run_row.mape is not None else None,
            "wape": float(run_row.wape) if run_row.wape is not None else None,
            "bias": float(run_row.bias) if run_row.bias is not None else None,
            "mae": float(run_row.mae) if run_row.mae is not None else None,
            "mape_vs_baseline_delta": float(run_row.mape_vs_baseline_delta) if run_row.mape_vs_baseline_delta is not None else None,
            "wape_vs_baseline_delta": float(run_row.wape_vs_baseline_delta) if run_row.wape_vs_baseline_delta is not None else None,
        },
        "value_impact": None,
        "value_summary": None,
        "top_skus": top_skus,
    }
    if value_row:
        context["value_impact"] = {
            "rev_uplift_estimate": float(value_row.rev_uplift_estimate) if value_row.rev_uplift_estimate is not None else None,
            "scrap_avoidance_estimate": float(value_row.scrap_avoidance_estimate) if value_row.scrap_avoidance_estimate is not None else None,
            "wc_savings_estimate": float(value_row.wc_savings_estimate) if value_row.wc_savings_estimate is not None else None,
            "productivity_savings_estimate": float(value_row.productivity_savings_estimate) if value_row.productivity_savings_estimate is not None else None,
            "assumptions_json": value_row.assumptions_json,
        }
    if run_value_row:
        context["value_summary"] = {
            "total_value_estimate": float(run_value_row.total_value_estimate) if run_value_row.total_value_estimate is not None else None,
            "revenue_uplift_estimate": float(run_value_row.revenue_uplift_estimate) if run_value_row.revenue_uplift_estimate is not None else None,
            "scrap_avoidance_estimate": float(run_value_row.scrap_avoidance_estimate) if run_value_row.scrap_avoidance_estimate is not None else None,
            "working_capital_savings_estimate": float(run_value_row.working_capital_savings_estimate) if run_value_row.working_capital_savings_estimate is not None else None,
            "planner_productivity_hours_saved": float(run_value_row.planner_productivity_hours_saved) if run_value_row.planner_productivity_hours_saved is not None else None,
            "case_label": run_value_row.case_label,
        }
    return context


def _build_run_prompt(context: Dict) -> str:
    facts = json.dumps(context, default=str)
    prompt = (
        "You are an S&OP analyst. Use the facts below to explain this forecast run clearly. "
        "Keep it concise and actionable. "
        "Structure: title, short summary (2-3 sentences), key drivers (bullets), risks (bullets), recommended actions (bullets). "
        "Facts:\n"
        f"{facts}"
    )
    return prompt


def _fallback_run_explanation(context: Dict) -> RunExplanation:
    metrics = context.get("metrics", {})
    title = f"Forecast run {context['run']['run_id']} summary"
    summary = f"Horizon {context['run']['horizon_start_month']} to {context['run']['horizon_end_month']}. "
    summary += f"MAPE={metrics.get('mape')}, WAPE={metrics.get('wape')}."
    return RunExplanation(
        title=title,
        short_summary=summary,
        key_drivers=["Based on latest forecast and available actuals."],
        risks=["LLM not configured or response unavailable."],
        recommended_actions=["Review top SKUs by error.", "Validate input assumptions."],
        model_used="none",
        is_fallback=True,
        run_id=context["run"]["run_id"],
        metrics_snapshot=context,
    )


def explain_run(db: Session, run_id: str, *, accuracy_limit: int = 5) -> RunExplanation:
    context = _load_run_context(db, run_id, accuracy_limit)
    prompt = _build_run_prompt(context)
    try:
        completion = generate_completion(prompt)
        explanation = RunExplanation(
            title=f"Forecast run {context['run']['run_id']}",
            short_summary=completion.strip(),
            key_drivers=[],
            risks=[],
            recommended_actions=[],
            model_used=settings.llm_model_name or "unknown",
            is_fallback=False,
            run_id=context["run"]["run_id"],
            metrics_snapshot=context,
        )
        logger.info("Generated run explanation via LLM for run_id=%s", run_id)
        return explanation
    except (LLMNotConfiguredError, LLMClientError):
        logger.warning("LLM unavailable for run explanation; using fallback for run_id=%s", run_id)
        return _fallback_run_explanation(context)
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error generating run explanation for run_id=%s", run_id, exc_info=exc)
        return _fallback_run_explanation(context)


def _load_scenario_context(db: Session, scenario_id: UUID) -> Dict:
    header_stmt = select(ScenarioHeader).where(ScenarioHeader.scenario_id == scenario_id)
    header = db.execute(header_stmt).scalar_one_or_none()
    if header is None:
        raise ValueError("Scenario not found")

    ledger_stmt = (
        select(ScenarioLedger)
        .where(ScenarioLedger.scenario_id == scenario_id)
        .order_by(ScenarioLedger.version_seq.asc())
    )
    ledger_rows = list(db.execute(ledger_stmt).scalars())

    rec_stmt = (
        select(InventoryRecommendation)
        .where(
            InventoryRecommendation.source_type == "SCENARIO",
            InventoryRecommendation.source_id == str(scenario_id),
        )
        .limit(20)
    )
    rec_rows = list(db.execute(rec_stmt).scalars())
    scenario_value_stmt = select(ScenarioValueSummaryModel).where(ScenarioValueSummaryModel.scenario_id == str(scenario_id))
    scenario_value_row = db.execute(scenario_value_stmt).scalar_one_or_none()

    assumptions = {
        "uplift_percent": float(header.uplift_percent) if header.uplift_percent is not None else None,
        "base_run_id": header.base_run_id,
    }

    ledger_summary = [
        {
            "version_seq": l.version_seq,
            "action_type": l.action_type,
            "actor": l.actor,
            "actor_role": l.actor_role,
            "comments": l.comments,
            "created_at": l.created_at,
        }
        for l in ledger_rows
    ]

    optimizer_summary = None
    if rec_rows:
        optimizer_summary = {
            "recommendation_rows": len(rec_rows),
            "sku_sample": list({r.sku_id for r in rec_rows})[:5],
        }
    value_summary = None
    if scenario_value_row:
        value_summary = {
            "total_expected_value_estimate": float(scenario_value_row.total_expected_value_estimate) if scenario_value_row.total_expected_value_estimate is not None else None,
            "expected_revenue_uplift_estimate": float(scenario_value_row.expected_revenue_uplift_estimate) if scenario_value_row.expected_revenue_uplift_estimate is not None else None,
            "expected_scrap_avoidance_estimate": float(scenario_value_row.expected_scrap_avoidance_estimate) if scenario_value_row.expected_scrap_avoidance_estimate is not None else None,
            "expected_working_capital_effect": float(scenario_value_row.expected_working_capital_effect) if scenario_value_row.expected_working_capital_effect is not None else None,
            "expected_service_level_change": float(scenario_value_row.expected_service_level_change) if scenario_value_row.expected_service_level_change is not None else None,
            "case_label": scenario_value_row.case_label,
        }

    context = {
        "scenario": {
            "scenario_id": str(header.scenario_id),
            "name": header.name,
            "status": header.status,
            "created_by": header.created_by,
            "created_at": header.created_at,
        },
        "assumptions": assumptions,
        "ledger": ledger_summary,
        "optimizer": optimizer_summary,
        "value_summary": value_summary,
    }
    return context


def _build_scenario_prompt(context: Dict) -> str:
    facts = json.dumps(context, default=str)
    prompt = (
        "You are a planning analyst. Explain this scenario concisely for S&OP. "
        "Provide: title, short summary, key changes/assumptions vs base, risks/trade-offs, talking points/actions. "
        "Facts:\n"
        f"{facts}"
    )
    return prompt


def _fallback_scenario_explanation(context: Dict) -> ScenarioExplanation:
    scenario = context["scenario"]
    title = f"Scenario {scenario['name'] or scenario['scenario_id']}"
    summary = f"Status: {scenario.get('status')}. Created by {scenario.get('created_by')}."
    return ScenarioExplanation(
        title=title,
        short_summary=summary,
        key_drivers=["Based on available scenario metadata and ledger history."],
        risks=["LLM not configured or response unavailable."],
        recommended_actions=["Review ledger steps", "Validate assumptions before approval"],
        model_used="none",
        is_fallback=True,
        scenario_id=scenario["scenario_id"],
        status=scenario.get("status"),
        created_by=scenario.get("created_by"),
        assumptions_snapshot=context.get("assumptions", {}),
        ledger_summary=context.get("ledger", []),
        optimizer_summary=context.get("optimizer"),
    )


def explain_scenario(db: Session, scenario_id: UUID) -> ScenarioExplanation:
    context = _load_scenario_context(db, scenario_id)
    prompt = _build_scenario_prompt(context)
    try:
        completion = generate_completion(prompt)
        explanation = ScenarioExplanation(
            title=context["scenario"]["name"] or f"Scenario {context['scenario']['scenario_id']}",
            short_summary=completion.strip(),
            key_drivers=[],
            risks=[],
            recommended_actions=[],
            model_used=settings.llm_model_name or "unknown",
            is_fallback=False,
            scenario_id=context["scenario"]["scenario_id"],
            status=context["scenario"].get("status"),
            created_by=context["scenario"].get("created_by"),
            assumptions_snapshot=context.get("assumptions", {}),
            ledger_summary=context.get("ledger", []),
            optimizer_summary=context.get("optimizer"),
        )
        logger.info("Generated scenario explanation via LLM for scenario_id=%s", scenario_id)
        return explanation
    except (LLMNotConfiguredError, LLMClientError):
        logger.warning("LLM unavailable for scenario explanation; using fallback for scenario_id=%s", scenario_id)
        return _fallback_scenario_explanation(context)
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error generating scenario explanation for scenario_id=%s", scenario_id, exc_info=exc)
        return _fallback_scenario_explanation(context)
