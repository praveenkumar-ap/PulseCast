import { get, post } from "./httpClient";
import type { Alert, AlertSeverity, AlertStatus, AlertType } from "@/types/domain";

type ApiAlert = {
  alert_id: string;
  indicator_id?: string | null;
  sku_id?: string | null;
  geo_id?: string | null;
  alert_type: string;
  severity: string;
  status: string;
  message?: string | null;
  triggered_at: string;
  acknowledged_at?: string | null;
  created_at: string;
  updated_at: string;
};

type ApiAlertListResponse = { alerts: ApiAlert[] };

function mapAlert(api: ApiAlert): Alert {
  const friendlyTitle = api.message || "Alert";
  return {
    id: api.alert_id,
    type: (api.alert_type as AlertType) || "UNKNOWN",
    severity: (api.severity as AlertSeverity) || "LOW",
    status: (api.status as AlertStatus) || "OPEN",
    title: friendlyTitle,
    summary: api.message || undefined,
    createdAt: api.created_at,
    updatedAt: api.updated_at,
    triggeredAt: api.triggered_at,
    acknowledgedAt: api.acknowledged_at || undefined,
  };
}

export async function listAlerts(params?: {
  status?: AlertStatus | "ALL";
  severity?: AlertSeverity | "ALL";
  limit?: number;
}) {
  const search = new URLSearchParams();
  if (params?.status && params.status !== "ALL") search.set("status", params.status);
  if (params?.severity && params.severity !== "ALL") search.set("severity", params.severity);
  if (params?.limit) search.set("limit", String(params.limit));
  const qs = search.toString();
  const res = await get<ApiAlertListResponse>(qs ? `/alerts?${qs}` : "/alerts");
  return res.alerts.map(mapAlert);
}

export async function getAlert(alertId: string) {
  const res = await get<ApiAlert>(`/alerts/${alertId}`);
  return mapAlert(res);
}

export async function updateAlertStatus(alertId: string, newStatus: AlertStatus, note?: string) {
  if (newStatus === "ACKNOWLEDGED") {
    const res = await post<{ actor: string; note?: string }, ApiAlert>(`/alerts/${alertId}/acknowledge`, {
      actor: "planner",
      note,
    });
    return mapAlert(res);
  }
  // Backend only supports acknowledge; return current detail for other statuses
  return getAlert(alertId);
}

export const alertsApi = {
  listAlerts,
  getAlert,
  updateAlertStatus,
};
