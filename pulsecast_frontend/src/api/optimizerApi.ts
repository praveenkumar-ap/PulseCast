import { get, post } from "./httpClient";
import type { InventoryPolicy, InventoryPolicyComparison } from "@/types/domain";

type ApiPolicy = {
  policy_id: string;
  sku_id: string;
  location_id?: string | null;
  year_month: string;
  source_type: string;
  source_id?: string | null;
  service_level_target?: number | null;
  safety_stock_units?: number | null;
  cycle_stock_units?: number | null;
  target_stock_units?: number | null;
  created_at: string;
};

type ApiPolicyComparison = {
  current: ApiPolicy;
  previous?: ApiPolicy | null;
  delta_safety_stock?: number | null;
  delta_scrap_risk_pct?: number | null;
};

type ApiPoliciesResponse = { recommendations: ApiPolicy[] };
type ApiComparisonResponse = { comparisons: ApiPolicyComparison[] };

function mapPolicy(api: ApiPolicy): InventoryPolicy {
  return {
    policyId: api.policy_id,
    runId: api.source_id ?? "",
    scenarioId: api.source_type === "SCENARIO" ? api.source_id ?? undefined : undefined,
    skuId: api.sku_id,
    locationId: api.location_id ?? undefined,
    policyType: "RECOMMENDED",
    safetyStock: api.safety_stock_units ?? undefined,
    cycleStockUnits: api.cycle_stock_units ?? undefined,
    targetStockUnits: api.target_stock_units ?? undefined,
    effectiveFrom: api.year_month,
    serviceLevelTarget: api.service_level_target ?? undefined,
  };
}

function mapComparison(api: ApiPolicyComparison): InventoryPolicyComparison {
  return {
    current: mapPolicy(api.current),
    previous: api.previous ? mapPolicy(api.previous) : undefined,
    deltaSafetyStock: api.delta_safety_stock ?? undefined,
    deltaScrapRiskPercent: api.delta_scrap_risk_pct ?? undefined,
  };
}

type ListParams = {
  runId: string;
  scenarioId?: string;
  familyId?: string;
  skuId?: string;
};

export async function listInventoryPolicies(params: ListParams): Promise<InventoryPolicy[]> {
  const search = new URLSearchParams();
  search.set("source_type", params.scenarioId ? "SCENARIO" : "BASE_RUN");
  if (params.scenarioId) search.set("source_id", params.scenarioId);
  else search.set("source_id", params.runId);
  if (params.skuId) search.set("sku_id", params.skuId);
  const qs = search.toString();
  const res = await get<ApiPoliciesResponse>(
    qs ? `/optimizer/recommendations?${qs}` : "/optimizer/recommendations"
  );
  return (res.recommendations ?? []).map(mapPolicy);
}

type ComparisonParams = {
  runId: string;
  scenarioId?: string;
  previousRunId?: string;
};

export async function listInventoryPolicyComparisons(
  params: ComparisonParams
): Promise<InventoryPolicyComparison[]> {
  const search = new URLSearchParams();
  search.set("run_id", params.runId);
  if (params.scenarioId) search.set("scenario_id", params.scenarioId);
  if (params.previousRunId) search.set("previous_run_id", params.previousRunId);
  const qs = search.toString();

  try {
    const res = await get<ApiComparisonResponse>(
      qs ? `/optimizer/recommendations/compare?${qs}` : "/optimizer/recommendations/compare"
    );
    return (res.comparisons ?? []).map(mapComparison);
  } catch {
    // Comparison endpoint may not exist; fall back gracefully.
    return [];
  }
}

type RunOptimizerParams = {
  sourceType: "BASE_RUN" | "SCENARIO";
  sourceId?: string;
  fromMonth: string;
  toMonth: string;
  skuIds?: string[];
  serviceLevelTarget?: number;
};

type ApiRunResponse = {
  recommendations: ApiPolicy[];
};

export async function runOptimizer(params: RunOptimizerParams): Promise<InventoryPolicy[]> {
  const res = await post<RunOptimizerParams, ApiRunResponse>("/optimizer/run", {
    source_type: params.sourceType,
    source_id: params.sourceId,
    from_month: params.fromMonth,
    to_month: params.toMonth,
    sku_ids: params.skuIds,
    service_level_target: params.serviceLevelTarget,
  });
  const recs: ApiPolicy[] = res?.recommendations ?? [];
  return recs.map(mapPolicy);
}

export const optimizerApi = {
  listInventoryPolicies,
  listInventoryPolicyComparisons,
  runOptimizer,
};
