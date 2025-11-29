"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForecastRuns } from "./hooks";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Table, TableCell, TableRow } from "@/components/ui/Table";
import type { ForecastRun } from "@/types/domain";

function formatDate(date?: string) {
  if (!date) return "—";
  const d = new Date(date);
  return d.toLocaleString();
}

function formatHorizon(run: ForecastRun) {
  if (run.horizonStartMonth && run.horizonEndMonth) {
    return `${run.horizonStartMonth} → ${run.horizonEndMonth}`;
  }
  return "—";
}

function formatAccuracy(run: ForecastRun) {
  if (run.mape !== undefined && run.mape !== null) {
    const baseline =
      run.mapeVsBaselineDelta !== undefined && run.mapeVsBaselineDelta !== null
        ? ` (${run.mapeVsBaselineDelta > 0 ? "+" : ""}${run.mapeVsBaselineDelta.toFixed(2)} vs base)`
        : "";
    return `${run.mape.toFixed(2)}${baseline}`;
  }
  return "—";
}

export function ForecastRunsPage() {
  const router = useRouter();
  const { data, loading, error, reload } = useForecastRuns();
  const [filter, setFilter] = useState("");

  const filtered = useMemo(() => {
    if (!data) return [];
    const needle = filter.toLowerCase();
    return data.filter(
      (run) =>
        run.runId.toLowerCase().includes(needle) ||
        (run.runType ?? "").toLowerCase().includes(needle)
    );
  }, [data, filter]);

  return (
    <div className="space-y-4">
      <div className="text-sm text-muted">
        <Link href="/home" className="text-primary hover:text-primary-strong">
          Home
        </Link>{" "}
        / Forecasts
      </div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-primary">Forecasts</p>
          <h1 className="text-2xl font-semibold text-heading">Forecast runs</h1>
          <p className="text-sm text-muted">
            Browse computed runs and drill into accuracy over time.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={reload}>
            Refresh
          </Button>
        </div>
      </div>

      <Card>
        <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter by run ID or model type"
            className="w-full rounded-lg border border-border bg-panel px-3 py-2 text-sm text-contrast outline-none ring-primary/20 focus:ring-2 sm:w-80"
          />
          {loading && <p className="text-sm text-muted">Loading forecast runs…</p>}
          {error && (
            <div className="flex items-center gap-2 text-sm text-rose-200">
              <span>Failed to load runs.</span>
              <Button size="sm" variant="secondary" onClick={reload}>
                Retry
              </Button>
            </div>
          )}
        </div>

        {!loading && !error && data?.length === 0 && (
          <p className="py-4 text-sm text-muted">No forecast runs available yet.</p>
        )}

        {!error && filtered.length > 0 && (
          <Table
            headers={["Run ID", "Model type", "Horizon", "Created at", "MAPE"]}
          >
            {filtered.map((run) => (
              <TableRow
                key={run.runId}
                className="cursor-pointer"
                onClick={() => router.push(`/forecasts/${run.runId}`)}
              >
                <TableCell>{run.runId}</TableCell>
                <TableCell>{run.runType ?? "—"}</TableCell>
                <TableCell>{formatHorizon(run)}</TableCell>
                <TableCell>{formatDate(run.computedAt)}</TableCell>
                <TableCell numeric>{formatAccuracy(run)}</TableCell>
              </TableRow>
            ))}
          </Table>
        )}
      </Card>
    </div>
  );
}
