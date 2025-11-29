"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { AlertsTable } from "./AlertsTable";
import { AlertDetailPanel } from "./AlertDetailPanel";
import { useAlertsList, useAlertActions } from "./hooks";
import type { Alert } from "@/types/domain";

const severityOptions = [
  { value: "ALL", label: "All" },
  { value: "LOW", label: "Low" },
  { value: "MEDIUM", label: "Medium" },
  { value: "HIGH", label: "High" },
  { value: "CRITICAL", label: "Critical" },
];

const statusOptions = [
  { value: "ALL", label: "All" },
  { value: "OPEN", label: "New" },
  { value: "ACKNOWLEDGED", label: "Acknowledged" },
  { value: "RESOLVED", label: "Resolved" },
];

const timeOptions = [
  { value: "TODAY", label: "Today" },
  { value: "LAST_7_DAYS", label: "Last 7 days" },
  { value: "LAST_30_DAYS", label: "Last 30 days" },
];

const typeOptions = [
  { value: "ALL", label: "All types" },
  { value: "LEADING_INDICATOR_SPIKE", label: "Indicator spike" },
  { value: "DEMAND_SHOCK", label: "Demand shock" },
  { value: "SUPPLY_RISK", label: "Supply risk" },
  { value: "DATA_STALENESS", label: "Data quality issue" },
];

export function AlertsPage() {
  const { alerts, filters, setFilters, loading, error, reload } = useAlertsList();
  const { updateStatus } = useAlertActions();
  const [selected, setSelected] = useState<Alert | null>(null);

  const handleUpdateStatus = async (status: Alert["status"]) => {
    if (!selected) return;
    const updated = await updateStatus(selected.id, status);
    setSelected(updated);
    reload();
  };

  return (
    <div className="space-y-5">
      <div className="text-sm text-muted">
        <Link href="/home" className="text-primary hover:text-primary-strong">
          Home
        </Link>{" "}
        / Alerts
      </div>
      <div>
        <p className="text-sm uppercase tracking-[0.2em] text-primary">Alerts</p>
        <h1 className="text-2xl font-semibold text-heading">Alerts & Early Warnings</h1>
        <p className="text-sm text-muted">
          This page shows signals that may need your attention, like sudden demand changes, supply issues, or stale data.
        </p>
      </div>

      <Card title="How to read this">
        <p className="text-sm text-muted">
          Each alert tells you what changed, why it matters, and what you may want to check next. Use the filters to focus on the most urgent items.
        </p>
      </Card>

      <Card>
        <div className="grid gap-3 sm:grid-cols-4">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Show alerts with urgency</span>
            <select
              className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={filters.severityFilter}
              onChange={(e) =>
                setFilters((f) => ({
                  ...f,
                  severityFilter: e.target.value as typeof filters.severityFilter,
                }))
              }
            >
              {severityOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Show alerts with status</span>
            <select
              className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={filters.statusFilter}
              onChange={(e) =>
                setFilters((f) => ({
                  ...f,
                  statusFilter: e.target.value as typeof filters.statusFilter,
                }))
              }
            >
              {statusOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">For time period</span>
            <select
              className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={filters.timeFilter}
              onChange={(e) =>
                setFilters((f) => ({
                  ...f,
                  timeFilter: e.target.value as typeof filters.timeFilter,
                }))
              }
            >
              {timeOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Alert type</span>
            <select
              className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={filters.typeFilter}
              onChange={(e) =>
                setFilters((f) => ({
                  ...f,
                  typeFilter: e.target.value as typeof filters.typeFilter,
                }))
              }
            >
              {typeOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <p className="mt-2 text-xs text-muted">
          You are seeing {filters.statusFilter === "ALL" ? "all statuses" : filters.statusFilter} alerts from{" "}
          {filters.timeFilter.replace("_", " ").toLowerCase()}.
        </p>
      </Card>

      <Card>
        {loading && <p className="text-sm text-muted">Loading alerts…</p>}
        {error && (
          <div className="flex items-center gap-2 text-sm text-rose-200">
            <span>We couldn’t load alerts. Check your connection and try again.</span>
            <Button size="sm" variant="secondary" onClick={reload}>
              Retry
            </Button>
          </div>
        )}
        {!loading && !error && alerts.length === 0 && (
          <p className="text-sm text-muted">No alerts for these filters. Try widening the time window or status.</p>
        )}
        {!error && alerts.length > 0 && <AlertsTable alerts={alerts} onSelect={setSelected} />}
      </Card>

      <AlertDetailPanel
        alert={selected}
        onClose={() => setSelected(null)}
        onUpdateStatus={async (status) => handleUpdateStatus(status)}
      />
    </div>
  );
}
