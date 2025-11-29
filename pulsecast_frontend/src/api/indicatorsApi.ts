import { get, post } from "./httpClient";
import type {
  Indicator,
  IndicatorFreshnessStatus,
  IndicatorQualitySummary,
  IndicatorFrequency,
} from "@/types/domain";

type ApiSummary = {
  indicator_id: string;
  name?: string | null;
  category?: string | null;
  provider?: string | null;
  status?: string | null;
  is_byo?: boolean | null;
  tags?: string | null;
  trust_score?: number | null;
};

type ApiTrustScore = {
  indicator_id: string;
  trust_score?: number | null;
  correlation_score?: number | null;
  importance_score?: number | null;
  is_recommended?: boolean | null;
  indicator_name?: string | null;
  provider?: string | null;
};

type ApiFreshness = {
  indicator_id: string;
  indicator_name?: string | null;
  provider?: string | null;
  last_data_time?: string | null;
  lag_hours?: number | null;
  is_within_sla?: boolean | null;
  sla_freshness_hours?: number | null;
};

type ApiDetail = {
  indicator: {
    catalog: {
      indicator_id: string;
      name?: string | null;
      description?: string | null;
      category?: string | null;
      frequency?: string | null;
      provider?: string | null;
      geo_scope?: string | null;
      is_byo?: boolean | null;
      status?: string | null;
      sla_freshness_hours?: number | null;
      license_type?: string | null;
      cost_estimate_per_month?: number | null;
      tags?: string | null;
    };
    quality?: {
      trust_score?: number | null;
      correlation_score?: number | null;
      importance_score?: number | null;
      is_recommended?: boolean | null;
    };
    freshness?: ApiFreshness;
  };
};

type ApiListResponse = { indicators: ApiSummary[] };
type ApiTrustListResponse = { scores: ApiTrustScore[] };

function mapIndicator(api: ApiSummary): Indicator {
  return {
    indicatorId: api.indicator_id,
    name: api.name || "Unnamed indicator",
    category: api.category || undefined,
    provider: api.provider || "Unknown provider",
    status: api.status || undefined,
    isByo: !!api.is_byo,
    tags: api.tags || undefined,
    trustScore: api.trust_score ?? undefined,
    frequency: "UNKNOWN",
  };
}

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

function mapQuality(api: ApiTrustScore): IndicatorQualitySummary {
  return {
    indicatorId: api.indicator_id,
    indicatorName: api.indicator_name || "",
    provider: api.provider || undefined,
    trustScore: api.trust_score ?? undefined,
    correlationScore: api.correlation_score ?? undefined,
    importanceScore: api.importance_score ?? undefined,
    isRecommended: api.is_recommended ?? undefined,
  };
}

export async function listIndicators(params?: {
  category?: string;
  providerName?: string;
  frequency?: IndicatorFrequency | "ALL";
  search?: string;
}) {
  const search = new URLSearchParams();
  if (params?.category) search.set("category", params.category);
  if (params?.providerName) search.set("provider", params.providerName);
  if (params?.search) search.set("search", params.search);
  const qs = search.toString();
  const res = await get<ApiListResponse>(qs ? `/indicators?${qs}` : "/indicators");
  return res.indicators.map(mapIndicator);
}

export async function getIndicatorDetail(id: string) {
  const res = await get<ApiDetail>(`/indicators/${id}`);
  const cat = res.indicator.catalog;
  const qual = res.indicator.quality;
  const fresh = res.indicator.freshness;
  const indicator: Indicator = {
    indicatorId: cat.indicator_id,
    name: cat.name || "Unnamed indicator",
    provider: cat.provider || "Unknown provider",
    category: cat.category || undefined,
    frequency: cat.frequency || "UNKNOWN",
    description: cat.description || undefined,
    geoScope: cat.geo_scope || undefined,
    isByo: !!cat.is_byo,
    status: cat.status || undefined,
    slaFreshnessHours: cat.sla_freshness_hours ?? undefined,
    licenseType: cat.license_type || undefined,
    costEstimatePerMonth: cat.cost_estimate_per_month ?? undefined,
    tags: cat.tags || undefined,
    trustScore: qual?.trust_score ?? undefined,
  };
  const freshness = fresh ? mapFreshness(fresh) : undefined;
  const quality = qual
    ? ({
        indicatorId: cat.indicator_id,
        indicatorName: cat.name || "",
        trustScore: qual.trust_score ?? undefined,
        correlationScore: qual.correlation_score ?? undefined,
        importanceScore: qual.importance_score ?? undefined,
        isRecommended: qual.is_recommended ?? undefined,
      } as IndicatorQualitySummary)
    : undefined;
  return { indicator, freshness, quality };
}

export async function listIndicatorTrust() {
  const res = await get<ApiTrustListResponse>("/indicators/trust");
  return res.scores.map(mapQuality);
}

export type CreateIndicatorRequest = {
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

type ApiCreateResponse = {
  indicator_id: string;
  name?: string | null;
  category?: string | null;
  provider?: string | null;
  status?: string | null;
  is_byo?: boolean | null;
  tags?: string | null;
};

export async function createIndicator(payload: CreateIndicatorRequest) {
  const res = await post<CreateIndicatorRequest, ApiCreateResponse>("/indicators/byos/register", {
    name: payload.name,
    description: payload.description,
    provider: payload.providerName,
    category: payload.category || "CUSTOM",
    frequency: payload.frequency,
    geo_scope: payload.geographyScope,
    owner_team: "Planning",
    owner_contact: payload.dataOwnerContact || "Unknown",
    license_type: "CUSTOM",
    cost_model: "UNKNOWN",
    connector_type: payload.dataSourceType || "OTHER",
    connector_config: {},
    cost_estimate_per_month: null,
    sla_freshness_hours: payload.slaHours,
    sla_coverage_notes: payload.notesForDataEngineering,
    is_byo: true,
    status: "ACTIVE",
  });
  return mapIndicator({
    indicator_id: res.indicator_id,
    name: res.name,
    category: res.category,
    provider: res.provider,
    status: res.status,
    is_byo: res.is_byo,
    tags: res.tags,
  });
}

export const indicatorsApi = {
  listIndicators,
  getIndicatorDetail,
  listIndicatorTrust,
  createIndicator,
};
