"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { IndicatorList } from "./IndicatorList";
import { IndicatorDetailPanel } from "./IndicatorDetailPanel";
import { ByosWizard } from "./ByosWizard";
import { useIndicatorsCatalog, useIndicatorDetail } from "./hooks";
import type { IndicatorFrequency, Indicator } from "@/types/domain";

const frequencies: Array<{ value: IndicatorFrequency | "ALL"; label: string }> = [
  { value: "ALL", label: "All" },
  { value: "REAL_TIME", label: "Real-time" },
  { value: "HOURLY", label: "Hourly" },
  { value: "DAILY", label: "Daily" },
  { value: "WEEKLY", label: "Weekly" },
  { value: "MONTHLY", label: "Monthly" },
];

export function IndicatorsPage() {
  const { indicators, freshnessById, qualityById, filters, setFilters, loading, error, reload } =
    useIndicatorsCatalog();
  const [selected, setSelected] = useState<Indicator | null>(null);
  const { indicator: detailIndicator, freshness, quality } = useIndicatorDetail(selected?.indicatorId);
  const [showByos, setShowByos] = useState(false);

  const providers = Array.from(new Set(indicators.map((i) => i.provider || "Unknown")));
  const categories = Array.from(new Set(indicators.map((i) => i.category || "Other")));

  return (
    <div className="space-y-5">
      <div className="text-sm text-muted">
        <Link href="/home" className="text-primary hover:text-primary-strong">
          Home
        </Link>{" "}
        / Indicators
      </div>
      <div>
        <p className="text-sm uppercase tracking-[0.2em] text-primary">Indicators</p>
        <h1 className="text-2xl font-semibold text-heading">Indicators & Signals</h1>
        <p className="text-sm text-muted">
          This page lists all signals used by PulseCast, such as flu hospitalizations, weather, and search trends.
          You can see how often they update and how reliable they are.
        </p>
      </div>

      <Card title="What’s shown here">
        <p className="text-sm text-muted">
          Indicators are data sources that help us sense demand earlier. Freshness shows how up-to-date the signal is;
          trust shows how useful it has been historically.
        </p>
      </Card>

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="grid gap-3 sm:grid-cols-4">
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-muted">Search indicators</span>
              <input
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={filters.searchText}
                onChange={(e) => setFilters((f) => ({ ...f, searchText: e.target.value }))}
                placeholder="Search by name, provider, or category"
              />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-muted">Category</span>
              <select
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={filters.categoryFilter}
                onChange={(e) =>
                  setFilters((f) => ({
                    ...f,
                    categoryFilter: e.target.value as string | "ALL",
                  }))
                }
              >
                <option value="ALL">All</option>
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-muted">Provider</span>
              <select
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={filters.providerFilter}
                onChange={(e) =>
                  setFilters((f) => ({
                    ...f,
                    providerFilter: e.target.value as string | "ALL",
                  }))
                }
              >
                <option value="ALL">All</option>
                {providers.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-muted">Update frequency</span>
              <select
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={filters.frequencyFilter}
                onChange={(e) =>
                  setFilters((f) => ({ ...f, frequencyFilter: e.target.value as IndicatorFrequency | "ALL" }))
                }
              >
                {frequencies.map((f) => (
                  <option key={f.value} value={f.value}>
                    {f.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <Button size="sm" onClick={() => setShowByos((v) => !v)}>
            {showByos ? "Close wizard" : "Add a new indicator"}
          </Button>
        </div>
        <p className="mt-2 text-xs text-muted">Showing {indicators.length} indicators matching your filters.</p>
      </Card>

      {showByos && <ByosWizard />}

      <Card>
        {loading && <p className="text-sm text-muted">Loading indicators…</p>}
        {error && (
          <div className="flex items-center gap-2 text-sm text-rose-200">
            <span>We couldn’t load indicators. Check your connection and try again.</span>
            <Button size="sm" variant="secondary" onClick={reload}>
              Retry
            </Button>
          </div>
        )}
        {!loading && !error && indicators.length === 0 && (
          <p className="text-sm text-muted">No indicators match your filters. Try clearing filters.</p>
        )}
        {!error && indicators.length > 0 && (
          <IndicatorList
            indicators={indicators}
            freshnessById={freshnessById}
            qualityById={qualityById}
            onSelect={setSelected}
          />
        )}
      </Card>

      <IndicatorDetailPanel
        indicator={detailIndicator || selected}
        freshness={freshness}
        quality={quality}
        onClose={() => setSelected(null)}
      />
    </div>
  );
}
