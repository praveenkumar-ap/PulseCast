"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useForecastRunDetail } from "./hooks";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Table, TableCell, TableRow } from "@/components/ui/Table";
import type { ForecastSeries } from "@/types/domain";
import { useGenaiHelper } from "@/features/genaiHooks";
import { GenaiPanel } from "@/features/GenaiPanel";
import { GenaiTriggerButton } from "@/features/GenaiTriggerButton";

function formatDate(date?: string) {
  if (!date) return "—";
  const d = new Date(date);
  return d.toLocaleString();
}

function formatNumber(val?: number | null, digits = 2) {
  if (val === undefined || val === null) return "—";
  return val.toFixed(digits);
}

function formatHorizon(start?: string, end?: string) {
  if (start && end) return `${start} → ${end}`;
  return "—";
}

type ChartProps = {
  series: ForecastSeries;
};

function SimpleSeriesChart({ series }: ChartProps) {
  const points = series.points;
  if (!points.length) return <p className="text-sm text-muted">No series data.</p>;

  const p50Values = points.map((p) => p.p50 ?? 0);
  const maxVal = Math.max(...p50Values, 1);
  const minVal = Math.min(...p50Values, 0);
  const range = Math.max(maxVal - minVal, 1);

  const width = Math.max(points.length * 60, 320);
  const height = 180;

  const linePath = points
    .map((p, idx) => {
      const x = (idx / Math.max(points.length - 1, 1)) * (width - 40) + 20;
      const y = height - ((p.p50 ?? 0) - minVal) / range * (height - 40) - 20;
      return `${idx === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");

  return (
    <div className="overflow-x-auto">
      <svg width={width} height={height} className="rounded-xl border border-border bg-panel">
        <path d={linePath} fill="none" stroke="#0ea5e9" strokeWidth={2} />
        {points.map((p, idx) => {
          const x = (idx / Math.max(points.length - 1, 1)) * (width - 40) + 20;
          const y = height - ((p.p50 ?? 0) - minVal) / range * (height - 40) - 20;
          return (
            <g key={`${p.yearMonth}-${idx}`}>
              <circle cx={x} cy={y} r={4} fill="#0ea5e9" />
              <text
                x={x}
                y={height - 10}
                textAnchor="middle"
                className="fill-current text-xs"
                fill="#94a3b8"
              >
                {p.yearMonth}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

export function ForecastRunDetailPage() {
  const params = useParams();
  const router = useRouter();
  const runId = Array.isArray(params?.runId) ? params?.runId[0] : (params?.runId as string | undefined);
  const { run, valueImpact, series, loading, error, changeView } = useForecastRunDetail(runId ?? "");

  const [selectedSku, setSelectedSku] = useState<string | undefined>(undefined);
  const genai = useGenaiHelper(
    { scope: "FORECAST_RUN", runId: runId ?? "", runLabel: run?.runType || runId },
    "Explain the key drivers behind this forecast run in simple language."
  );

  const activeSeries = useMemo(() => {
    if (!series.length) return null;
    if (selectedSku) return series.find((s) => s.id === selectedSku) ?? series[0];
    return series[0];
  }, [series, selectedSku]);

  if (!runId) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-muted">No run id provided.</p>
      </div>
    );
  }

  if (!loading && !run) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-muted">Run not found.</p>
        <Link href="/forecasts" className="text-primary hover:text-primary-strong">
          Back to forecasts
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-2">
        <Button variant="secondary" size="sm" onClick={() => router.push("/forecasts")}>
          ← Back to forecasts
        </Button>
        <Button size="sm" onClick={() => router.push(`/scenarios/new?runId=${runId}`)}>
          Create scenario from this run
        </Button>
        <Button size="sm" variant="secondary" onClick={() => router.push(`/optimizer?runId=${runId}`)}>
          View inventory policies
        </Button>
        <Button size="sm" variant="secondary" onClick={() => router.push(`/value?runId=${runId}`)}>
          View value impact
        </Button>
        <GenaiTriggerButton
          onClick={() =>
            genai.openPanel(
              { scope: "FORECAST_RUN", runId: runId ?? "", runLabel: run?.runType || runId },
              "Explain the key drivers behind this forecast run in simple language."
            )
          }
        />
        <p className="text-sm text-muted">Run ID: {runId}</p>
      </div>

      <Card
        title="Run summary"
        subtitle="Metadata and accuracy vs baseline."
      >
        {loading && <p className="text-sm text-muted">Loading run…</p>}
        {error && (
          <div className="flex items-center gap-2 text-sm text-rose-200">
            <span>Failed to load run.</span>
            <Button size="sm" variant="secondary" onClick={() => changeView({ skuId: selectedSku })}>
              Retry
            </Button>
          </div>
        )}
        {run && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-muted">Model</p>
              <p className="text-base font-semibold text-heading">{run.runType ?? "—"}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-muted">Computed at</p>
              <p className="text-base font-semibold text-heading">{formatDate(run.computedAt)}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-muted">Horizon</p>
              <p className="text-base font-semibold text-heading">
                {formatHorizon(run.horizonStartMonth, run.horizonEndMonth)}
              </p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-muted">MAPE</p>
              <p className="text-base font-semibold text-heading">
                {formatNumber(run.mape)}
                {run.mapeVsBaselineDelta !== undefined && (
                  <span className="text-sm text-muted">
                    {" "}
                    ({run.mapeVsBaselineDelta > 0 ? "+" : ""}
                    {formatNumber(run.mapeVsBaselineDelta)})
                  </span>
                )}
              </p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-muted">WAPE</p>
              <p className="text-base font-semibold text-heading">
                {formatNumber(run.wape)}
                {run.wapeVsBaselineDelta !== undefined && (
                  <span className="text-sm text-muted">
                    {" "}
                    ({run.wapeVsBaselineDelta > 0 ? "+" : ""}
                    {formatNumber(run.wapeVsBaselineDelta)})
                  </span>
                )}
              </p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-muted">SKUs covered</p>
              <p className="text-base font-semibold text-heading">{run.skusCovered ?? "—"}</p>
            </div>
            {valueImpact && (
              <div className="sm:col-span-2 lg:col-span-3">
                <p className="text-xs uppercase tracking-[0.18em] text-muted">Value impact</p>
                <p className="text-base font-semibold text-heading">
                  Rev uplift: {formatNumber(valueImpact.revUpliftEstimate)} · Scrap avoided:{" "}
                  {formatNumber(valueImpact.scrapAvoidanceEstimate)} · WC savings:{" "}
                  {formatNumber(valueImpact.wcSavingsEstimate)}
                </p>
              </div>
            )}
          </div>
        )}
      </Card>

      <Card
        title="Series"
        subtitle="P50 trajectory by SKU (P10/P90 unavailable from current API)."
        actions={
          <div className="flex items-center gap-3">
            <label className="text-xs text-muted">
              View by SKU:
              <select
                className="ml-2 rounded-md border border-border bg-panel px-2 py-1 text-sm text-contrast"
                value={selectedSku ?? ""}
                onChange={(e) => {
                  const sku = e.target.value || undefined;
                  setSelectedSku(sku);
                  changeView({ skuId: sku });
                }}
              >
                <option value="">All</option>
                {series.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
        }
      >
        {loading && <p className="text-sm text-muted">Loading series…</p>}
        {error && (
          <div className="flex items-center gap-2 text-sm text-rose-200">
            <span>Failed to load series.</span>
            <Button size="sm" variant="secondary" onClick={() => changeView({ skuId: selectedSku })}>
              Retry
            </Button>
          </div>
        )}
        {!loading && !error && !activeSeries && (
          <p className="text-sm text-muted">No series available.</p>
        )}
        {!loading && !error && activeSeries && (
          <div className="space-y-4">
            <SimpleSeriesChart series={activeSeries} />
            <Table headers={["SKU", "Month", "P50", "Actual"]}>
              {activeSeries.points.map((p) => (
                <TableRow key={`${activeSeries.id}-${p.yearMonth}`}>
                  <TableCell>{activeSeries.label}</TableCell>
                  <TableCell>{p.yearMonth}</TableCell>
                  <TableCell numeric>{formatNumber(p.p50)}</TableCell>
                  <TableCell numeric>{formatNumber(p.actualUnits)}</TableCell>
                </TableRow>
              ))}
            </Table>
          </div>
        )}
      </Card>

      <GenaiPanel
        isOpen={genai.isOpen}
        onClose={genai.closePanel}
        question={genai.question}
        setQuestion={genai.setQuestion}
        ask={genai.ask}
        answer={genai.answer}
        loading={genai.loading}
        error={genai.error as unknown as Error | null}
        suggestions={genai.suggestions}
        scopeLabel="You’re asking about this forecast run."
      />
    </div>
  );
}
