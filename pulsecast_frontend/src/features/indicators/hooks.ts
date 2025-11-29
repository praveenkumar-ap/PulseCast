import { useCallback, useEffect, useMemo, useState } from "react";
import {
  createIndicator as apiCreateIndicator,
  getIndicatorDetail,
  listIndicatorTrust,
  listIndicators,
} from "@/api/indicatorsApi";
import type {
  Indicator,
  IndicatorFreshnessStatus,
  IndicatorQualitySummary,
  IndicatorFrequency,
} from "@/types/domain";
import type { ApiError } from "@/api/httpClient";

type Filters = {
  searchText: string;
  categoryFilter: string | "ALL";
  providerFilter: string | "ALL";
  frequencyFilter: IndicatorFrequency | "ALL";
};

const defaultFilters: Filters = {
  searchText: "",
  categoryFilter: "ALL",
  providerFilter: "ALL",
  frequencyFilter: "ALL",
};

export function useIndicatorsCatalog() {
  const [indicators, setIndicators] = useState<Indicator[]>([]);
  const [freshnessById] = useState<Record<string, IndicatorFreshnessStatus>>({});
  const [qualityById, setQualityById] = useState<Record<string, IndicatorQualitySummary>>({});
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await listIndicators({
        category: filters.categoryFilter === "ALL" ? undefined : filters.categoryFilter,
        providerName: filters.providerFilter === "ALL" ? undefined : filters.providerFilter,
        frequency: filters.frequencyFilter === "ALL" ? undefined : filters.frequencyFilter,
        search: filters.searchText || undefined,
      });
      setIndicators(list);
      const trust = await listIndicatorTrust();
      const trustMap: Record<string, IndicatorQualitySummary> = {};
      trust.forEach((t) => {
        trustMap[t.indicatorId] = t;
      });
      setQualityById(trustMap);
    } catch (err) {
      setError(err as ApiError);
    } finally {
      setLoading(false);
    }
  }, [filters.categoryFilter, filters.frequencyFilter, filters.providerFilter, filters.searchText]);

  useEffect(() => {
    load();
  }, [load]);

  const filtered = useMemo(() => {
    return indicators.filter((i) => {
      const matchSearch =
        !filters.searchText ||
        i.name.toLowerCase().includes(filters.searchText.toLowerCase()) ||
        (i.provider || "").toLowerCase().includes(filters.searchText.toLowerCase()) ||
        (i.category || "").toLowerCase().includes(filters.searchText.toLowerCase());
      return matchSearch;
    });
  }, [filters.searchText, indicators]);

  return {
    indicators: filtered,
    freshnessById,
    qualityById,
    filters,
    setFilters,
    loading,
    error,
    reload: load,
  };
}

export function useIndicatorDetail(indicatorId?: string) {
  const [indicator, setIndicator] = useState<Indicator | null>(null);
  const [freshness, setFreshness] = useState<IndicatorFreshnessStatus | undefined>(undefined);
  const [quality, setQuality] = useState<IndicatorQualitySummary | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    if (!indicatorId) return;
    setLoading(true);
    setError(null);
    getIndicatorDetail(indicatorId)
      .then(({ indicator, freshness, quality }) => {
        setIndicator(indicator);
        setFreshness(freshness);
        setQuality(quality);
      })
      .catch((err: ApiError) => setError(err))
      .finally(() => setLoading(false));
  }, [indicatorId]);

  return { indicator, freshness, quality, loading, error };
}

type WizardValues = {
  name: string;
  description?: string;
  providerName: string;
  category?: string;
  geographyScope?: string;
  frequency: IndicatorFrequency;
  expectedUpdateLagHours?: number;
  slaHours?: number;
  dataSourceType?: "API" | "File upload" | "Database" | "Other";
  dataOwnerContact?: string;
  notesForDataEngineering?: string;
};

export function useByosWizard() {
  const [step, setStep] = useState(1);
  const [values, setValues] = useState<WizardValues>({
    name: "",
    providerName: "",
    frequency: "DAILY",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successIndicator, setSuccessIndicator] = useState<Indicator | null>(null);

  const updateField = <K extends keyof WizardValues>(field: K, value: WizardValues[K]) => {
    setValues((v) => ({ ...v, [field]: value }));
  };

  const submit = async () => {
    if (!values.name || !values.providerName) {
      setError("Please provide a name and provider.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const created = await apiCreateIndicator(values);
      setSuccessIndicator(created);
      setStep(5);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Something went wrong while saving this indicator.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return {
    step,
    setStep,
    values,
    updateField,
    loading,
    error,
    successIndicator,
    goToNext: () => setStep((s) => Math.min(s + 1, 4)),
    goToPrevious: () => setStep((s) => Math.max(s - 1, 1)),
    submit,
  };
}
