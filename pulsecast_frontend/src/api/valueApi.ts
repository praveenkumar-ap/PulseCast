import { get } from "./httpClient";
import type { ApiError } from "./httpClient";
import type { ValueBenchmarks, ValueRunSummary, ValueScenarioSummary } from "@/types/domain";

// Backend response shapes
type ApiRunValue = {
  run_id: string;
  run_type?: string | null;
  period_start?: string | null;
  period_end?: string | null;
  family_id?: string | null;
  family_name?: string | null;
  skus_covered?: number | null;
  revenue_uplift_estimate?: number | null;
  scrap_avoidance_estimate?: number | null;
  working_capital_savings_estimate?: number | null;
  planner_productivity_hours_saved?: number | null;
  total_value_estimate?: number | null;
  case_label?: string | null;
  computed_at?: string | null;
};

type ApiScenarioValue = {
  scenario_id: string;
  scenario_name?: string | null;
  linked_run_id?: string | null;
  status?: string | null;
  revenue_uplift_estimate?: number | null;
  scrap_avoidance_estimate?: number | null;
  working_capital_savings_estimate?: number | null;
  total_value_estimate?: number | null;
  net_benefit?: number | null;
  currency?: string | null;
  case_label?: string | null;
};

type ApiBenchmarks = {
  accuracy_uplift_pct?: number | null;
  total_revenue_uplift?: number | null;
  total_scrap_avoided?: number | null;
  total_working_capital_impact?: number | null;
  planner_time_saved_hours?: number | null;
};

type ApiRunList = { runs: ApiRunValue[] };
type ApiScenarioList = { scenarios: ApiScenarioValue[] };
type ApiBenchmarksResponse = { benchmarks: ApiBenchmarks[] };

function mapRunValue(api: ApiRunValue): ValueRunSummary {
  return {
    runId: api.run_id,
    runType: api.run_type ?? undefined,
    periodStart: api.period_start ?? undefined,
    periodEnd: api.period_end ?? undefined,
    familyId: api.family_id ?? undefined,
    familyName: api.family_name ?? undefined,
    skusCovered: api.skus_covered ?? undefined,
    revenueUpliftEstimate: api.revenue_uplift_estimate ?? undefined,
    scrapAvoidanceEstimate: api.scrap_avoidance_estimate ?? undefined,
    workingCapitalSavingsEstimate: api.working_capital_savings_estimate ?? undefined,
    plannerProductivityHoursSaved: api.planner_productivity_hours_saved ?? undefined,
    totalValueEstimate: api.total_value_estimate ?? undefined,
    caseLabel: api.case_label ?? undefined,
    computedAt: api.computed_at ?? undefined,
  };
}

function mapScenarioValue(api: ApiScenarioValue): ValueScenarioSummary {
  return {
    scenarioId: api.scenario_id,
    scenarioName: api.scenario_name ?? undefined,
    status: api.status ?? undefined,
    linkedRunId: api.linked_run_id ?? undefined,
    revenueUpliftEstimate: api.revenue_uplift_estimate ?? undefined,
    scrapAvoidanceEstimate: api.scrap_avoidance_estimate ?? undefined,
    workingCapitalSavingsEstimate: api.working_capital_savings_estimate ?? undefined,
    totalValueEstimate: api.total_value_estimate ?? undefined,
    netBenefit: api.net_benefit ?? undefined,
    currency: api.currency ?? undefined,
    caseLabel: api.case_label ?? undefined,
  };
}

function mapBenchmarks(api: ApiBenchmarks): ValueBenchmarks {
  return {
    accuracyUpliftPct: api.accuracy_uplift_pct ?? undefined,
    totalRevenueUplift: api.total_revenue_uplift ?? undefined,
    totalScrapAvoided: api.total_scrap_avoided ?? undefined,
    totalWorkingCapitalImpact: api.total_working_capital_impact ?? undefined,
    plannerTimeSavedHours: api.planner_time_saved_hours ?? undefined,
  };
}

export async function getValueRuns() {
  const res = await get<ApiRunList>("/value/runs");
  return res.runs.map(mapRunValue);
}

export async function getValueScenarios(params?: { runId?: string; status?: string }) {
  const search = new URLSearchParams();
  if (params?.runId) search.set("run_id", params.runId);
  if (params?.status) search.set("status", params.status);
  const qs = search.toString();
  try {
    const res = await get<ApiScenarioList>(qs ? `/value/scenarios?${qs}` : "/value/scenarios");
    return res.scenarios.map(mapScenarioValue);
  } catch (err) {
    const apiErr = err as ApiError;
    if (apiErr.status && apiErr.status >= 500) {
      return [];
    }
    throw err;
  }
}

export async function getValueBenchmarks() {
  const res = await get<ApiBenchmarksResponse>("/value/benchmarks");
  const first = res.benchmarks[0] ?? {};
  return mapBenchmarks(first);
}

export const valueApi = {
  getValueRuns,
  getValueScenarios,
  getValueBenchmarks,
};
