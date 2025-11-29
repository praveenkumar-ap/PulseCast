import { get } from "./httpClient";
import type { ForecastAccuracyPoint, IndicatorFreshnessStatus, MonitorSummary } from "@/types/domain";

type ApiFreshness = {
  indicator_id: string;
  indicator_name?: string | null;
  provider?: string | null;
  last_data_time?: string | null;
  lag_hours?: number | null;
  sla_freshness_hours?: number | null;
  is_within_sla?: boolean | null;
};

type ApiAccuracyItem = {
  run_id?: string | null;
  run_label?: string | null;
  date: string;
  mape?: number | null;
  wmape?: number | null;
  mase?: number | null;
  accuracy_pct?: number | null;
};

type ApiFreshnessResponse = { items?: ApiFreshness[] };
type ApiAccuracyResponse = { items?: ApiAccuracyItem[] };

function mapFreshness(api: ApiFreshness): IndicatorFreshnessStatus {
  return {
    indicatorId: api.indicator_id,
    indicatorName: api.indicator_name || "",
    provider: api.provider || "",
    lastDataTime: api.last_data_time ?? null,
    lagHours: api.lag_hours ?? null,
    slaFreshnessHours: api.sla_freshness_hours ?? null,
    isWithinSla: api.is_within_sla ?? null,
  };
}

function mapAccuracy(api: ApiAccuracyItem): ForecastAccuracyPoint {
  return {
    date: api.date,
    runId: api.run_id ?? undefined,
    runLabel: api.run_label ?? undefined,
    mape: api.mape ?? undefined,
    wmape: api.wmape ?? undefined,
    mase: api.mase ?? undefined,
    accuracyPercent: api.accuracy_pct ?? undefined,
  };
}

export async function listIndicatorFreshness(): Promise<IndicatorFreshnessStatus[]> {
  // Backend lacks a dedicated endpoint; fall back to empty list gracefully.
  try {
    const res = await get<ApiFreshnessResponse>("/monitor/indicator_freshness");
    return (res.items ?? []).map(mapFreshness);
  } catch {
    return [];
  }
}

export async function listForecastAccuracy(params?: { runId?: string; fromDate?: string; toDate?: string }) {
  const search = new URLSearchParams();
  if (params?.runId) search.set("run_id", params.runId);
  if (params?.fromDate) search.set("from_date", params.fromDate);
  if (params?.toDate) search.set("to_date", params.toDate);
  const qs = search.toString();
  try {
    const res = await get<ApiAccuracyResponse>(
      qs ? `/monitor/forecast_accuracy?${qs}` : "/monitor/forecast_accuracy"
    );
    return (res.items ?? []).map(mapAccuracy);
  } catch {
    return [];
  }
}

export async function getMonitorSummary(): Promise<MonitorSummary | undefined> {
  try {
    const res = await get<MonitorSummary>("/monitor/summary");
    return res;
  } catch {
    return undefined;
  }
}

export const monitorApi = {
  listIndicatorFreshness,
  listForecastAccuracy,
  getMonitorSummary,
};
