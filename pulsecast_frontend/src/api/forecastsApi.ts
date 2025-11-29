import { get } from "./httpClient";
import type {
  ForecastRun,
  ForecastRunValueImpact,
  ForecastSeries,
  ForecastSeriesPoint,
} from "@/types/domain";

type ApiForecastRun = {
  run_id: string;
  run_type?: string;
  horizon_start_month?: string | null;
  horizon_end_month?: string | null;
  skus_covered?: number | null;
  mape?: number | null;
  wape?: number | null;
  bias?: number | null;
  mae?: number | null;
  mape_vs_baseline_delta?: number | null;
  wape_vs_baseline_delta?: number | null;
  computed_at?: string | null;
};

type ApiValueImpact = {
  run_id: string;
  rev_uplift_estimate?: number | null;
  scrap_avoidance_estimate?: number | null;
  wc_savings_estimate?: number | null;
  productivity_savings_estimate?: number | null;
  assumptions_json?: string | null;
  computed_at?: string | null;
};

type ApiRunsResponse = { runs: ApiForecastRun[] };
type ApiRunDetailResponse = { run: ApiForecastRun; value_impact?: ApiValueImpact | null };

type ApiAccuracyItem = {
  run_id: string;
  sku_id: string;
  year_month: string;
  actual_units?: number | null;
  forecast_p50_units?: number | null;
  abs_error?: number | null;
  ape?: number | null;
};
type ApiAccuracyResponse = { items: ApiAccuracyItem[] };

type ApiSkuListResponse = { skus: string[] };

function mapRun(api: ApiForecastRun): ForecastRun {
  return {
    runId: api.run_id,
    runType: api.run_type ?? undefined,
    horizonStartMonth: api.horizon_start_month ?? undefined,
    horizonEndMonth: api.horizon_end_month ?? undefined,
    skusCovered: api.skus_covered ?? undefined,
    mape: api.mape ?? undefined,
    wape: api.wape ?? undefined,
    bias: api.bias ?? undefined,
    mae: api.mae ?? undefined,
    mapeVsBaselineDelta: api.mape_vs_baseline_delta ?? undefined,
    wapeVsBaselineDelta: api.wape_vs_baseline_delta ?? undefined,
    computedAt: api.computed_at ?? undefined,
  };
}

function mapValueImpact(api: ApiValueImpact | null | undefined): ForecastRunValueImpact | undefined {
  if (!api) return undefined;
  return {
    runId: api.run_id,
    revUpliftEstimate: api.rev_uplift_estimate ?? undefined,
    scrapAvoidanceEstimate: api.scrap_avoidance_estimate ?? undefined,
    wcSavingsEstimate: api.wc_savings_estimate ?? undefined,
    productivitySavingsEstimate: api.productivity_savings_estimate ?? undefined,
    assumptionsJson: api.assumptions_json ?? null,
    computedAt: api.computed_at ?? undefined,
  };
}

function mapAccuracyToSeries(response: ApiAccuracyResponse): ForecastSeries[] {
  const bySku = new Map<string, ForecastSeriesPoint[]>();
  response.items.forEach((item) => {
    const points = bySku.get(item.sku_id) ?? [];
    points.push({
      yearMonth: item.year_month,
      p50: item.forecast_p50_units ?? undefined,
      actualUnits: item.actual_units ?? undefined,
    });
    bySku.set(item.sku_id, points);
  });

  return Array.from(bySku.entries()).map(([skuId, points]) => ({
    id: skuId,
    label: skuId,
    points,
  }));
}

export async function listForecastRuns(): Promise<ForecastRun[]> {
  const res = await get<ApiRunsResponse>("/metrics/runs");
  return res.runs.map(mapRun);
}

export async function getForecastRunMetadata(
  runId: string
): Promise<{ run: ForecastRun; valueImpact?: ForecastRunValueImpact }> {
  const res = await get<ApiRunDetailResponse>(`/metrics/runs/${runId}`);
  return { run: mapRun(res.run), valueImpact: mapValueImpact(res.value_impact) };
}

type SeriesParams = {
  skuId?: string;
  inSeasonOnly?: boolean;
};

export async function getForecastSeriesForRun(
  runId: string,
  params: SeriesParams = {}
): Promise<ForecastSeries[]> {
  const search = new URLSearchParams();
  if (params.skuId) search.set("sku_id", params.skuId);
  const query = search.toString();
  const path = query ? `/metrics/runs/${runId}/accuracy?${query}` : `/metrics/runs/${runId}/accuracy`;
  const res = await get<ApiAccuracyResponse>(path);
  return mapAccuracyToSeries(res);
}

/**
 * Fetch the list of SKU ids available for a given run.
 * If the backend exposes a dedicated endpoint we will use it;
 * otherwise we derive SKUs from the accuracy endpoint.
 */
export async function listSkusForRun(runId: string): Promise<string[]> {
  // Try a dedicated endpoint first; if it 404s, fall back to accuracy-derived list.
  try {
    const res = await get<ApiSkuListResponse>(`/metrics/runs/${runId}/skus`);
    if (Array.isArray(res.skus)) return res.skus;
  } catch {
    // ignore and fall back
  }

  const series = await getForecastSeriesForRun(runId);
  const set = new Set<string>();
  series.forEach((s) => set.add(s.id));
  return Array.from(set);
}
