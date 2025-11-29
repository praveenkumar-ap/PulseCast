import { useCallback, useEffect, useState } from "react";
import { valueApi } from "@/api/valueApi";
import type { ValueBenchmarks, ValueRunSummary, ValueScenarioSummary } from "@/types/domain";

type AsyncState<T> = {
  data: T;
  loading: boolean;
  error: string | null;
  reload: () => void;
};

export function useValueOverview(): AsyncState<{ benchmarks: ValueBenchmarks | null; runs: ValueRunSummary[] }> {
  const [data, setData] = useState<{ benchmarks: ValueBenchmarks | null; runs: ValueRunSummary[] }>({
    benchmarks: null,
    runs: [],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [benchmarks, runs] = await Promise.all([valueApi.getValueBenchmarks(), valueApi.getValueRuns()]);
      setData({ benchmarks, runs });
    } catch (err) {
      setError("We couldn’t load your value metrics right now.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return { data, loading, error, reload: load };
}

export function useValueScenarios(runId?: string, status?: string): AsyncState<ValueScenarioSummary[]> {
  const [data, setData] = useState<ValueScenarioSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const scenarios = await valueApi.getValueScenarios({ runId, status });
      setData(scenarios);
    } catch (err) {
      setError("We couldn’t load scenario value details right now.");
    } finally {
      setLoading(false);
    }
  }, [runId, status]);

  useEffect(() => {
    void load();
  }, [load]);

  return { data, loading, error, reload: load };
}
