import { get, post } from "./httpClient";
import type {
  ScenarioDetail,
  ScenarioLedgerEntry,
  ScenarioStatus,
  ScenarioSummary,
} from "@/types/domain";

type ApiScenarioSummary = {
  scenario_id: string;
  name: string;
  status: ScenarioStatus;
  base_run_id?: string | null;
  uplift_percent?: number | null;
  created_by: string;
  created_at: string;
  updated_at: string;
};

type ApiScenarioDetailResponse = {
  header: {
    scenario_id: string;
    name: string;
    description?: string | null;
    status: ScenarioStatus;
    base_run_id?: string | null;
    uplift_percent?: number | null;
    created_by: string;
    created_at: string;
    updated_at: string;
  };
  results: Array<{
    sku_id: string;
    year_month: string;
    base_run_id?: string | null;
    p10: number;
    p50: number;
    p90: number;
    created_at: string;
  }>;
};

type ApiLedgerEntry = {
  ledger_id: string;
  scenario_id: string;
  version_seq: number;
  action_type: ScenarioLedgerEntry["actionType"];
  actor: string;
  actor_role?: string | null;
  assumptions?: string | null;
  comments?: string | null;
  created_at: string;
};

type ApiLedgerResponse = { events: ApiLedgerEntry[] };
type ApiListResponse = { scenarios: ApiScenarioSummary[] };

function mapSummary(api: ApiScenarioSummary): ScenarioSummary {
  return {
    scenarioId: api.scenario_id,
    name: api.name,
    status: api.status,
    baseRunId: api.base_run_id ?? undefined,
    upliftPercent: api.uplift_percent ?? undefined,
    createdBy: api.created_by,
    createdAt: api.created_at,
    updatedAt: api.updated_at,
  };
}

function mapDetail(api: ApiScenarioDetailResponse): ScenarioDetail {
  const horizon =
    api.results && api.results.length > 0
      ? {
          fromMonth: api.results[0].year_month,
          toMonth: api.results[api.results.length - 1].year_month,
        }
      : undefined;
  return {
    scenarioId: api.header.scenario_id,
    name: api.header.name,
    status: api.header.status,
    baseRunId: api.header.base_run_id ?? undefined,
    upliftPercent: api.header.uplift_percent ?? undefined,
    createdBy: api.header.created_by,
    createdAt: api.header.created_at,
    updatedAt: api.header.updated_at,
    description: api.header.description ?? undefined,
    results: api.results.map((r) => ({
      skuId: r.sku_id,
      yearMonth: r.year_month,
      baseRunId: r.base_run_id ?? undefined,
      p10: r.p10,
      p50: r.p50,
      p90: r.p90,
      createdAt: r.created_at,
    })),
    assumptions: {
      upliftPercent: api.header.uplift_percent ?? undefined,
      horizon,
      scope: { type: "ALL" }, // backend does not expose scope; default to ALL
    },
  };
}

function mapLedgerEntry(api: ApiLedgerEntry): ScenarioLedgerEntry {
  return {
    ledgerId: api.ledger_id,
    scenarioId: api.scenario_id,
    versionSeq: api.version_seq,
    actionType: api.action_type,
    actor: api.actor,
    actorRole: api.actor_role ?? undefined,
    assumptions: api.assumptions ?? undefined,
    comments: api.comments ?? undefined,
    createdAt: api.created_at,
  };
}

export async function listScenarios(params?: { status?: ScenarioStatus; limit?: number }) {
  const search = new URLSearchParams();
  if (params?.status) search.set("status", params.status);
  if (params?.limit) search.set("limit", String(params.limit));
  const query = search.toString();
  const path = query ? `/scenarios?${query}` : "/scenarios";
  const res = await get<ApiListResponse>(path);
  return res.scenarios.map(mapSummary);
}

export async function getScenarioDetail(id: string) {
  const res = await get<ApiScenarioDetailResponse>(`/scenarios/${id}`);
  return mapDetail(res);
}

export async function getScenarioLedger(id: string, limit = 50) {
  const res = await get<ApiLedgerResponse>(`/scenarios/${id}/ledger?limit=${limit}`);
  return res.events.map(mapLedgerEntry);
}

export type CreateScenarioPayload = {
  name: string;
  description?: string;
  createdBy: string;
  baseRunId?: string;
  skuIds?: string[];
  fromMonth: string;
  toMonth: string;
  upliftPercent: number;
};

export type CreateScenarioResponse = {
  scenarioId: string;
  name: string;
  status: ScenarioStatus;
  baseRunId: string;
  upliftPercent: number;
  fromMonth: string;
  toMonth: string;
  skuIds: string[];
  totalRows: number;
};

type ApiCreateResponse = {
  scenario_id: string;
  name: string;
  status: ScenarioStatus;
  base_run_id: string;
  uplift_percent: number;
  from_month: string;
  to_month: string;
  sku_ids: string[];
  total_rows: number;
};

export async function createScenario(payload: CreateScenarioPayload) {
  const res = await post<CreateScenarioPayload, ApiCreateResponse>("/scenarios", {
    name: payload.name,
    description: payload.description,
    created_by: payload.createdBy,
    base_run_id: payload.baseRunId,
    sku_ids: payload.skuIds,
    from_month: payload.fromMonth,
    to_month: payload.toMonth,
    uplift_percent: payload.upliftPercent,
  });
  return {
    scenarioId: res.scenario_id,
    name: res.name,
    status: res.status,
    baseRunId: res.base_run_id,
    upliftPercent: res.uplift_percent,
    fromMonth: res.from_month,
    toMonth: res.to_month,
    skuIds: res.sku_ids,
    totalRows: res.total_rows,
  } as CreateScenarioResponse;
}

export type LedgerAction =
  | "CREATE"
  | "EDIT"
  | "SUBMIT"
  | "APPROVE"
  | "REJECT"
  | "ARCHIVE"
  | "COMMENT"
  | "RUN_OPTIMIZER";

export async function appendScenarioLedger(
  scenarioId: string,
  payload: { actionType: LedgerAction; actor: string; actorRole?: string; assumptions?: string; comments?: string }
) {
  const res = await post<typeof payload, ApiLedgerEntry>(`/scenarios/${scenarioId}/ledger`, {
    action_type: payload.actionType,
    actor: payload.actor,
    actor_role: payload.actorRole,
    assumptions: payload.assumptions,
    comments: payload.comments,
  });
  return mapLedgerEntry(res);
}
