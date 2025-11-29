import { useCallback, useEffect, useState } from "react";
import {
  appendScenarioLedger,
  createScenario,
  getScenarioDetail,
  getScenarioLedger,
  listScenarios,
  type CreateScenarioPayload,
  type LedgerAction,
} from "@/api/scenariosApi";
import { listForecastRuns, listSkusForRun } from "@/api/forecastsApi";
import type {
  ScenarioDetail,
  ScenarioLedgerEntry,
  ScenarioStatus,
  ScenarioSummary,
} from "@/types/domain";
import type { ApiError } from "@/api/httpClient";
import { runtimeEnv } from "@/config/env";

type AsyncState<T> = { data: T | null; loading: boolean; error: ApiError | null };

export function useScenariosList(filters?: { status?: ScenarioStatus }) {
  const [state, setState] = useState<AsyncState<ScenarioSummary[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const load = useCallback(() => {
    setState((s) => ({ ...s, loading: true, error: null }));
    listScenarios({ status: filters?.status })
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((err: ApiError) => setState({ data: null, loading: false, error: err }));
  }, [filters?.status]);

  useEffect(() => {
    load();
  }, [load]);

  return { ...state, reload: load };
}

type ScenarioDetailState = {
  detail: ScenarioDetail | null;
  ledger: ScenarioLedgerEntry[];
  loading: boolean;
  error: ApiError | null;
};

export function useScenarioDetail(scenarioId: string) {
  const [state, setState] = useState<ScenarioDetailState>({
    detail: null,
    ledger: [],
    loading: true,
    error: null,
  });

  const load = useCallback(() => {
    if (!scenarioId) return;
    setState((s) => ({ ...s, loading: true, error: null }));
    Promise.all([getScenarioDetail(scenarioId), getScenarioLedger(scenarioId)])
      .then(([detail, ledger]) =>
        setState({ detail, ledger, loading: false, error: null })
      )
      .catch((err: ApiError) =>
        setState((s) => ({ ...s, loading: false, error: err }))
      );
  }, [scenarioId]);

  useEffect(() => {
    load();
  }, [load]);

  const appendLedger = (action: LedgerAction, comments?: string, assumptions?: string) => {
    const actor = runtimeEnv.userId || "dev-user";
    return appendScenarioLedger(scenarioId, {
      actionType: action,
      actor,
      comments,
      assumptions,
    }).then((entry) => {
      setState((s) => ({ ...s, ledger: [...s.ledger, entry] }));
      return entry;
    });
  };

  return { ...state, reload: load, appendLedger };
}

export function useCreateScenario() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const submit = (payload: Omit<CreateScenarioPayload, "createdBy"> & { createdBy?: string }) => {
    setLoading(true);
    setError(null);
    const createdBy = payload.createdBy || runtimeEnv.userId || "dev-user";
    return createScenario({ ...payload, createdBy })
      .finally(() => setLoading(false))
      .catch((err: ApiError) => {
        setError(err);
        throw err;
      });
  };

  return { submit, loading, error };
}

type WizardScope =
  | { type: "ALL" }
  | { type: "SKU"; skuIds: string[] };

export type WizardState = {
  step: number;
  runId?: string;
  runHorizon?: { fromMonth?: string; toMonth?: string };
  availableRuns: Array<{
    value: string;
    label: string;
    fromMonth?: string;
    toMonth?: string;
  }>;
  availableSkus: string[];
  scope: WizardScope;
  upliftPercent: number;
  scenarioName: string;
  notes?: string;
  errors?: string | null;
};

export function useScenarioWizard(initialRunId?: string) {
  const [state, setState] = useState<WizardState>({
    step: 1,
    availableRuns: [],
    availableSkus: [],
    scope: { type: "ALL" },
    upliftPercent: 5,
    scenarioName: "New scenario",
    notes: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<ApiError | null>(null);

  // load runs
  useEffect(() => {
    listForecastRuns()
      .then((runs) => {
        const options =
          runs?.map((r) => ({
            value: r.runId,
            label: `${r.runId}${r.runType ? ` (${r.runType})` : ""}`,
            fromMonth: r.horizonStartMonth?.slice(0, 7),
            toMonth: r.horizonEndMonth?.slice(0, 7),
          })) ?? [];
        const selected = initialRunId || options[0]?.value;
        const horizon = options.find((o) => o.value === selected);
        setState((s) => ({
          ...s,
          availableRuns: options,
          runId: selected,
          runHorizon: { fromMonth: horizon?.fromMonth, toMonth: horizon?.toMonth },
        }));
      })
      .catch(() => {
        setState((s) => ({ ...s, errors: "Failed to load forecast runs" }));
      });
  }, [initialRunId]);

  // load SKUs for selected run
  useEffect(() => {
    if (!state.runId) return;
    listSkusForRun(state.runId)
      .then((skus) => setState((s) => ({ ...s, availableSkus: skus ?? [] })))
      .catch(() => setState((s) => ({ ...s, errors: "Failed to load SKUs for run" })));
  }, [state.runId]);

  const next = () => setState((s) => ({ ...s, step: Math.min(5, s.step + 1) }));
  const prev = () => setState((s) => ({ ...s, step: Math.max(1, s.step - 1) }));

  const setRun = (runId: string) => {
    const horizon = state.availableRuns.find((r) => r.value === runId);
    setState((s) => ({
      ...s,
      runId,
      runHorizon: { fromMonth: horizon?.fromMonth, toMonth: horizon?.toMonth },
      scope: { type: "ALL" },
      availableSkus: [],
    }));
  };

  const setHorizon = (fromMonth?: string, toMonth?: string) =>
    setState((s) => ({ ...s, runHorizon: { fromMonth, toMonth } }));

  const setScope = (scope: WizardScope) => setState((s) => ({ ...s, scope }));

  const setUplift = (value: number) => setState((s) => ({ ...s, upliftPercent: value }));
  const setNotes = (value: string) => setState((s) => ({ ...s, notes: value }));
  const setScenarioName = (value: string) => setState((s) => ({ ...s, scenarioName: value }));

  const submit = async () => {
    if (!state.runId) throw new Error("Select a base run first");
    setSubmitting(true);
    setSubmitError(null);
    try {
      const payload: CreateScenarioPayload = {
        name: state.scenarioName || "New scenario",
        description: state.notes,
        baseRunId: state.runId,
        fromMonth: state.runHorizon?.fromMonth || "",
        toMonth: state.runHorizon?.toMonth || "",
        upliftPercent: state.upliftPercent,
        skuIds: state.scope.type === "SKU" ? state.scope.skuIds : undefined,
        createdBy: runtimeEnv.userId || "dev-user",
      };
      return await createScenario(payload);
    } catch (err) {
      setSubmitError(err as ApiError);
      throw err;
    } finally {
      setSubmitting(false);
    }
  };

  return {
    state,
    submitting,
    submitError,
    actions: {
      next,
      prev,
      setRun,
      setHorizon,
      setScope,
      setUplift,
      setNotes,
      setScenarioName,
      submit,
    },
  };
}
