import { useCallback, useEffect, useMemo, useState } from "react";
import { optimizerApi } from "@/api/optimizerApi";
import type { InventoryPolicy } from "@/types/domain";
import type { ApiError } from "@/api/httpClient";
import { useForecastRuns } from "@/features/forecasts/hooks";

type Filters = {
  family?: string;
  sku?: string;
  sortBy?: "stockoutRisk" | "scrapRisk" | "safetyStock";
};

export function useOptimizerPolicies(initialRunId?: string, initialScenarioId?: string) {
  const { data: runs, loading: runsLoading } = useForecastRuns();
  const [selectedRunId, setSelectedRunId] = useState<string | undefined>(initialRunId);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | undefined>(initialScenarioId);
  const [filters, setFilters] = useState<Filters>({});
  const [policies, setPolicies] = useState<InventoryPolicy[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    if (!runsLoading && runs && runs.length > 0 && !selectedRunId) {
      setSelectedRunId(runs[0].runId);
    }
  }, [runs, runsLoading, selectedRunId]);

  const load = useCallback(async () => {
    if (!selectedRunId) return;
    setLoading(true);
    setError(null);
    try {
      const currentPolicies = await optimizerApi.listInventoryPolicies({
        runId: selectedRunId,
        scenarioId: selectedScenarioId,
        skuId: filters.sku,
      });
      if (currentPolicies.length === 0) {
        const runMeta = runs?.find((r) => r.runId === selectedRunId);
        const fromMonth = (runMeta?.horizonStartMonth || "").slice(0, 7) || "2024-01";
        const toMonth = (runMeta?.horizonEndMonth || "").slice(0, 7) || "2024-12";
        await optimizerApi.runOptimizer({
          sourceType: selectedScenarioId ? "SCENARIO" : "BASE_RUN",
          sourceId: selectedScenarioId ?? selectedRunId,
          fromMonth,
          toMonth,
        });
        const refreshed = await optimizerApi.listInventoryPolicies({
          runId: selectedRunId,
          scenarioId: selectedScenarioId,
          skuId: filters.sku,
        });
        setPolicies(refreshed);
      } else {
        setPolicies(currentPolicies);
      }
    } catch (err) {
      setError(err as ApiError);
    } finally {
      setLoading(false);
    }
  }, [filters.sku, runs, selectedRunId, selectedScenarioId]);

  useEffect(() => {
    load();
  }, [load]);

  const filteredPolicies = useMemo(() => {
    let res = policies;
    if (filters.family) {
      res = res.filter(
        (p) =>
          p.familyName?.toLowerCase().includes(filters.family!.toLowerCase()) ||
          p.familyCode?.toLowerCase().includes(filters.family!.toLowerCase())
      );
    }
    if (filters.sku) {
      res = res.filter(
        (p) => p.skuId === filters.sku || p.skuCode === filters.sku || p.skuName === filters.sku
      );
    }
    if (filters.sortBy) {
      res = [...res].sort((a, b) => {
        if (filters.sortBy === "stockoutRisk") {
          return (b.stockoutRiskPercent ?? 0) - (a.stockoutRiskPercent ?? 0);
        }
        if (filters.sortBy === "scrapRisk") {
          return (b.scrapRiskPercent ?? 0) - (a.scrapRiskPercent ?? 0);
        }
        return (b.safetyStock ?? 0) - (a.safetyStock ?? 0);
      });
    }
    return res;
  }, [filters.family, filters.sku, filters.sortBy, policies]);

  return {
    runs,
    runsLoading,
    selectedRunId,
    setSelectedRunId,
    selectedScenarioId,
    setSelectedScenarioId,
    filters,
    setFilters,
    policies: filteredPolicies,
    availableSkus: Array.from(
      new Map(
        policies.map((p) => {
          const label = p.skuName || p.skuCode || p.skuId;
          const value = p.skuId;
          return [value, { value, label }];
        })
      ).values()
    ),
    loading,
    error,
    reload: load,
  };
}
