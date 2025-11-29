import { useCallback, useEffect, useMemo, useState } from "react";
import { monitorApi } from "@/api/monitorApi";
import type { ForecastAccuracyPoint, IndicatorFreshnessStatus, MonitorSummary } from "@/types/domain";
import type { ApiError } from "@/api/httpClient";

type Filters = {
  accuracyTimeRange: "LAST_30_DAYS" | "LAST_90_DAYS" | "LAST_YEAR";
  filterByRunId?: string;
  freshnessFilter: "ALL" | "ON_TIME" | "DELAYED";
};

const defaultFilters: Filters = {
  accuracyTimeRange: "LAST_30_DAYS",
  freshnessFilter: "ALL",
};

function sliceByRange(points: ForecastAccuracyPoint[], range: Filters["accuracyTimeRange"]) {
  const now = Date.now();
  const oneDay = 24 * 60 * 60 * 1000;
  const cutoff =
    range === "LAST_30_DAYS" ? now - 30 * oneDay : range === "LAST_90_DAYS" ? now - 90 * oneDay : now - 365 * oneDay;
  return points.filter((p) => new Date(p.date).getTime() >= cutoff);
}

export function useMonitorDashboard(initial?: Partial<Filters>) {
  const [indicatorFreshness, setIndicatorFreshness] = useState<IndicatorFreshnessStatus[]>([]);
  const [forecastAccuracy, setForecastAccuracy] = useState<ForecastAccuracyPoint[]>([]);
  const [summary, setSummary] = useState<MonitorSummary | undefined>(undefined);
  const [filters, setFilters] = useState<Filters>({ ...defaultFilters, ...initial });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [fresh, acc, sum] = await Promise.all([
        monitorApi.listIndicatorFreshness(),
        monitorApi.listForecastAccuracy({ runId: filters.filterByRunId }),
        monitorApi.getMonitorSummary(),
      ]);
      setIndicatorFreshness(fresh);
      const sliced = sliceByRange(acc, filters.accuracyTimeRange);
      setForecastAccuracy(sliced);
      setSummary(sum);
    } catch (err) {
      setError(err as ApiError);
    } finally {
      setLoading(false);
    }
  }, [filters.accuracyTimeRange, filters.filterByRunId]);

  useEffect(() => {
    load();
  }, [load]);

  const filteredFreshness = useMemo(() => {
    if (filters.freshnessFilter === "ALL") return indicatorFreshness;
    if (filters.freshnessFilter === "ON_TIME") {
      return indicatorFreshness.filter((f) => f.isWithinSla === true);
    }
    return indicatorFreshness.filter((f) => f.isWithinSla === false);
  }, [filters.freshnessFilter, indicatorFreshness]);

  return {
    indicatorFreshness: filteredFreshness,
    forecastAccuracy,
    summary,
    filters,
    setFilters,
    loading,
    error,
    reload: load,
  };
}
