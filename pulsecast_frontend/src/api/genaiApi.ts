import { post } from "./httpClient";
import type { GenaiAnswer, GenaiAskRequest } from "@/types/domain";

type RunExplainResponse = {
  run_id: string;
  short_summary: string;
  key_drivers: string[];
  risks: string[];
  recommended_actions: string[];
  model_used?: string | null;
  is_fallback?: boolean;
};

type ScenarioExplainResponse = {
  scenario_id: string;
  short_summary: string;
  key_drivers: string[];
  risks: string[];
  recommended_actions: string[];
  model_used?: string | null;
  is_fallback?: boolean;
};

function mapExplainToAnswer(resp: RunExplainResponse | ScenarioExplainResponse): GenaiAnswer {
  return {
    answer: resp.short_summary,
    highlights: [
      ...(resp.key_drivers ?? []).map((text) => ({ text, title: "Key driver" })),
      ...(resp.recommended_actions ?? []).map((text) => ({ text, title: "Next step" })),
    ],
    caveats: resp.risks && resp.risks.length ? resp.risks.join(" • ") : undefined,
    sources: resp.model_used ? [`Model: ${resp.model_used}${resp.is_fallback ? " (fallback)" : ""}`] : undefined,
  };
}

export async function askGenai(request: GenaiAskRequest): Promise<GenaiAnswer> {
  const { context } = request;

  if (context.scope === "FORECAST_RUN" && context.runId) {
    const resp = await post<RunExplainResponse>("/explain/run", { run_id: context.runId });
    return mapExplainToAnswer(resp);
  }

  if (context.scope === "SCENARIO" && context.scenarioId) {
    const resp = await post<ScenarioExplainResponse>("/explain/scenario", { scenario_id: context.scenarioId });
    return mapExplainToAnswer(resp);
  }

  // Value overview or freeform fallback: reuse run explain when runId is provided.
  if (context.runId) {
    const resp = await post<RunExplainResponse>("/explain/run", { run_id: context.runId });
    return mapExplainToAnswer(resp);
  }

  // If we have no suitable backend endpoint, return a friendly fallback.
  return {
    answer:
      "I need a forecast run or scenario context to explain this. Please open a forecast run or scenario and try again.",
    highlights: [],
  };
}

export const genaiApi = {
  askGenai,
};
