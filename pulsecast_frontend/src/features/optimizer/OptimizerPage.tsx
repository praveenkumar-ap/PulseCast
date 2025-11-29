"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { OptimizerPolicyTable } from "./OptimizerPolicyTable";
import { OptimizerPolicyDetailPanel } from "./OptimizerPolicyDetailPanel";
import { useOptimizerPolicies } from "./hooks";
import { useSearchParams } from "next/navigation";
import { useScenariosList } from "@/features/scenarios/hooks";

export function OptimizerPage() {
  const searchParams = useSearchParams();
  const initialRunId = searchParams?.get("runId") || undefined;
  const initialScenarioId = searchParams?.get("scenarioId") || undefined;
  const { data: scenarios, loading: scenariosLoading } = useScenariosList();
  const {
    runs,
    runsLoading,
    availableSkus,
    selectedRunId,
    setSelectedRunId,
    selectedScenarioId,
    setSelectedScenarioId,
    filters,
    setFilters,
    policies,
    loading,
    error,
    reload,
  } = useOptimizerPolicies(initialRunId, initialScenarioId);
  const [selectedPolicy, setSelectedPolicy] = useState<typeof policies[number] | null>(null);

  return (
    <div className="space-y-5">
      <div className="text-sm text-muted">
        <Link href="/home" className="text-primary hover:text-primary-strong">
          Home
        </Link>{" "}
        / Inventory policies
      </div>
      <div>
        <p className="text-sm uppercase tracking-[0.2em] text-primary">Optimizer</p>
        <h1 className="text-2xl font-semibold text-heading">Inventory Policy Recommendations</h1>
        <p className="text-sm text-muted">
          See the recommended stock policies for each test kit. These settings balance stockouts against excess and expiry risk.
        </p>
      </div>

      <Card title="What these fields mean">
        <ul className="grid gap-2 text-sm text-muted sm:grid-cols-2">
          <li><strong className="text-heading">Base stock</strong>: target level you aim to keep on hand.</li>
          <li><strong className="text-heading">Target stock</strong>: total units after a reorder (cycle stock + safety stock) to cover expected demand plus buffer.</li>
          <li><strong className="text-heading">(s,S) policy</strong>: reorder when stock reaches s, up to S.</li>
          <li><strong className="text-heading">Safety stock</strong>: buffer to absorb demand swings.</li>
          <li><strong className="text-heading">Expiry horizon</strong>: how long before product expires; shorter horizons raise scrap risk.</li>
        </ul>
      </Card>

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-4">
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-muted">Forecast run</span>
              <select
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={selectedRunId || ""}
                onChange={(e) => {
                  setSelectedRunId(e.target.value || undefined);
                  setSelectedScenarioId(undefined);
                }}
              >
                {runsLoading && <option>Loading runs…</option>}
                {runs?.map((r) => (
                  <option key={r.runId} value={r.runId}>
                    {r.runId} ({r.runType ?? "run"})
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-muted">Scenario (optional)</span>
              <select
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={selectedScenarioId || ""}
                onChange={(e) => setSelectedScenarioId(e.target.value || undefined)}
              >
                <option value="">None – base forecast only</option>
                {scenariosLoading && <option>Loading scenarios…</option>}
                {scenarios?.map((s) => (
                  <option key={s.scenarioId} value={s.scenarioId}>
                    {s.name} ({s.status})
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" onClick={reload}>
              Refresh
            </Button>
          </div>
        </div>

        <div className="mt-3 grid gap-3 sm:grid-cols-3">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Family filter</span>
            <input
              className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={filters.family || ""}
              onChange={(e) => setFilters((f) => ({ ...f, family: e.target.value }))}
              placeholder="e.g., Respiratory"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">SKU filter</span>
            <select
              className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={filters.sku || ""}
              onChange={(e) => setFilters((f) => ({ ...f, sku: e.target.value || undefined }))}
            >
              <option value="">All SKUs</option>
              {availableSkus.map((sku) => (
                <option key={sku.value} value={sku.value}>
                  {sku.label}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Sort</span>
            <select
              className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={filters.sortBy || ""}
              onChange={(e) =>
                setFilters((f) => ({
                  ...f,
                  sortBy: (e.target.value as "stockoutRisk" | "scrapRisk" | "safetyStock" | "") || undefined,
                }))
              }
            >
              <option value="">Default order</option>
              <option value="stockoutRisk">Show highest stockout risk first</option>
              <option value="scrapRisk">Show highest scrap risk first</option>
              <option value="safetyStock">Show highest safety stock first</option>
            </select>
          </label>
        </div>

        <div className="mt-4 space-y-2">
          {loading && <p className="text-sm text-muted">Loading recommended policies…</p>}
          {error && (
            <div className="flex items-center gap-2 text-sm text-rose-200">
              <span>We couldn’t load policies. Check the selection and try again.</span>
              <Button size="sm" variant="secondary" onClick={reload}>
                Retry
              </Button>
            </div>
          )}
          {!loading && !error && policies.length === 0 && (
            <p className="text-sm text-muted">
              No policies available for this run/filters. Try another run or clear filters.
            </p>
          )}
          {!error && policies.length > 0 && (
            <OptimizerPolicyTable policies={policies} onSelect={setSelectedPolicy} />
          )}
        </div>
      </Card>

      <OptimizerPolicyDetailPanel policy={selectedPolicy} onClose={() => setSelectedPolicy(null)} />
    </div>
  );
}
