import { useCallback, useEffect, useMemo, useState } from "react";
import { alertsApi } from "@/api/alertsApi";
import type { Alert, AlertSeverity, AlertStatus, AlertType } from "@/types/domain";
import type { ApiError } from "@/api/httpClient";

type TimeFilter = "TODAY" | "LAST_7_DAYS" | "LAST_30_DAYS";

type Filters = {
  statusFilter: AlertStatus | "ALL";
  severityFilter: AlertSeverity | "ALL";
  typeFilter: AlertType | "ALL";
  timeFilter: TimeFilter;
};

const defaultFilters: Filters = {
  statusFilter: "OPEN",
  severityFilter: "ALL",
  typeFilter: "ALL",
  timeFilter: "LAST_7_DAYS",
};

function withinTime(alert: Alert, filter: TimeFilter) {
  const ts = new Date(alert.triggeredAt).getTime();
  const now = Date.now();
  const oneDay = 24 * 60 * 60 * 1000;
  if (filter === "TODAY") return ts >= now - oneDay;
  if (filter === "LAST_7_DAYS") return ts >= now - 7 * oneDay;
  if (filter === "LAST_30_DAYS") return ts >= now - 30 * oneDay;
  return true;
}

export function useAlertsList(initial?: Partial<Filters>) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filters, setFilters] = useState<Filters>({ ...defaultFilters, ...initial });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await alertsApi.listAlerts({
        status: filters.statusFilter === "ALL" ? undefined : filters.statusFilter,
        severity: filters.severityFilter === "ALL" ? undefined : filters.severityFilter,
      });
      setAlerts(data);
    } catch (err) {
      setError(err as ApiError);
    } finally {
      setLoading(false);
    }
  }, [filters.severityFilter, filters.statusFilter]);

  useEffect(() => {
    load();
  }, [load]);

  const filteredAlerts = useMemo(() => {
    return alerts
      .filter((a) => (filters.typeFilter === "ALL" ? true : a.type === filters.typeFilter))
      .filter((a) => withinTime(a, filters.timeFilter));
  }, [alerts, filters.timeFilter, filters.typeFilter]);

  return { alerts: filteredAlerts, filters, setFilters, loading, error, reload: load };
}

export function useAlertActions() {
  const updateStatus = (alertId: string, newStatus: AlertStatus, note?: string) => {
    return alertsApi.updateAlertStatus(alertId, newStatus, note);
  };
  return { updateStatus };
}
