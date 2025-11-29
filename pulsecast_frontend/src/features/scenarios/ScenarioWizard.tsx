"use client";

import React from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useScenarioWizard } from "./hooks";

type WizardProps = {
  initialRunId?: string;
  onCreated?: (scenarioId: string) => void;
};

export function ScenarioWizard({ initialRunId, onCreated }: WizardProps) {
  const {
    state,
    submitting,
    submitError,
    actions: {
      next,
      prev,
      setRun,
      setHorizon,
      setScope,
      setUplift,
      setNotes,
      setScenarioName,
      submit,
    },
  } = useScenarioWizard(initialRunId);

  const selectedRun = state.availableRuns.find((r) => r.value === state.runId);
  const skuOptions = state.availableSkus;

  const scopeLabel =
    state.scope.type === "ALL"
      ? "All SKUs"
      : `Specific SKUs (${state.scope.skuIds.length} selected)`;

  const handleSubmit = async () => {
    const res = await submit();
    if (onCreated) onCreated(res.scenarioId);
  };

  if (!state.runId && state.availableRuns.length === 0) {
    return <p className="text-sm text-muted">Loading runs for scenario setup…</p>;
  }

  return (
    <div className="space-y-4">
      <Card title="New scenario" subtitle="Guided setup to avoid invalid combinations.">
        <div className="space-y-6">
          {state.errors && <p className="text-rose-300">{state.errors}</p>}
          <StepHeader step={1} label="Pick base run" active={state.step === 1} />
          {state.step === 1 && (
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="flex flex-col gap-1 text-sm">
                <span className="text-muted">Base run</span>
                <select
                  className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                  value={state.runId ?? ""}
                  onChange={(e) => setRun(e.target.value)}
                >
                  {state.availableRuns.map((r) => (
                    <option key={r.value} value={r.value}>
                      {r.label}
                    </option>
                  ))}
                </select>
              </label>
              <div className="rounded-lg border border-border bg-white/5 p-3 text-sm">
                <p className="text-muted">Allowed horizon</p>
                <p className="font-semibold text-heading">
                  {selectedRun?.fromMonth ?? "?"} → {selectedRun?.toMonth ?? "?"}
                </p>
              </div>
            </div>
          )}

          <StepHeader step={2} label="Choose horizon" active={state.step === 2} />
          {state.step === 2 && (
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="flex flex-col gap-1 text-sm">
                <span className="text-muted">From month</span>
                <input
                  type="month"
                  className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                  value={state.runHorizon?.fromMonth ?? ""}
                  min={selectedRun?.fromMonth}
                  max={selectedRun?.toMonth}
                  onChange={(e) =>
                    setHorizon(e.target.value, state.runHorizon?.toMonth ?? undefined)
                  }
                />
              </label>
              <label className="flex flex-col gap-1 text-sm">
                <span className="text-muted">To month</span>
                <input
                  type="month"
                  className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                  value={state.runHorizon?.toMonth ?? ""}
                  min={state.runHorizon?.fromMonth ?? selectedRun?.fromMonth}
                  max={selectedRun?.toMonth}
                  onChange={(e) =>
                    setHorizon(state.runHorizon?.fromMonth ?? undefined, e.target.value)
                  }
                />
              </label>
              <p className="sm:col-span-2 text-xs text-muted">
                Horizon is constrained to the run’s available window.
              </p>
            </div>
          )}

          <StepHeader step={3} label="Select scope" active={state.step === 3} />
          {state.step === 3 && (
            <div className="space-y-3">
              <div className="flex gap-3">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    checked={state.scope.type === "ALL"}
                    onChange={() => setScope({ type: "ALL" })}
                  />
                  All SKUs
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    checked={state.scope.type === "SKU"}
                    onChange={() => setScope({ type: "SKU", skuIds: [] })}
                  />
                  Specific SKUs
                </label>
              </div>
              {state.scope.type === "SKU" && (
                <label className="flex flex-col gap-1 text-sm">
                  <span className="text-muted">Choose SKUs (from this run)</span>
                  <select
                    multiple
                    className="min-h-[140px] rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                    value={state.scope.skuIds}
                    onChange={(e) => {
                      const opts = Array.from(e.target.selectedOptions).map((o) => o.value);
                      setScope({ type: "SKU", skuIds: opts });
                    }}
                  >
                    {skuOptions.map((sku) => (
                      <option key={sku} value={sku}>
                        {sku}
                      </option>
                    ))}
                  </select>
                  <span className="text-xs text-muted">
                    Only SKUs present in the selected run are shown.
                  </span>
                </label>
              )}
            </div>
          )}

          <StepHeader step={4} label="Assumptions" active={state.step === 4} />
          {state.step === 4 && (
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="flex flex-col gap-1 text-sm sm:col-span-2">
                <span className="text-muted">Scenario name</span>
                <input
                  className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                  value={state.scenarioName}
                  onChange={(e) => setScenarioName(e.target.value)}
                  placeholder="Name this scenario"
                />
              </label>
              <label className="flex flex-col gap-1 text-sm">
                <span className="text-muted">Demand uplift %</span>
                <input
                  type="number"
                  className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                  value={state.upliftPercent}
                  onChange={(e) => setUplift(Number(e.target.value || 0))}
                />
              </label>
              <label className="flex flex-col gap-1 text-sm sm:col-span-2">
                <span className="text-muted">Notes (optional)</span>
                <textarea
                  className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                  rows={3}
                  value={state.notes ?? ""}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add business context for this scenario"
                />
              </label>
            </div>
          )}

          <StepHeader step={5} label="Review" active={state.step === 5} />
          {state.step === 5 && (
            <div className="space-y-2 rounded-lg border border-border bg-white/5 p-3 text-sm">
              <p>
                <span className="text-muted">Run:</span> {selectedRun?.label ?? "—"}
              </p>
              <p>
                <span className="text-muted">Horizon:</span>{" "}
                {state.runHorizon?.fromMonth ?? "?"} → {state.runHorizon?.toMonth ?? "?"}
              </p>
              <p>
                <span className="text-muted">Scope:</span> {scopeLabel}
              </p>
              <p>
                <span className="text-muted">Uplift %:</span> {state.upliftPercent}
              </p>
              <p>
                <span className="text-muted">Name:</span> {state.scenarioName}
              </p>
              {state.notes && (
                <p>
                  <span className="text-muted">Notes:</span> {state.notes}
                </p>
              )}
              {submitError && (
                <p className="text-rose-300">
                  {submitError.message || "Scenario creation failed"}
                </p>
              )}
            </div>
          )}

          <div className="flex justify-between pt-2">
            <Button variant="secondary" onClick={prev} disabled={state.step === 1}>
              Previous
            </Button>
            {state.step < 5 ? (
              <Button onClick={next}>Next</Button>
            ) : (
              <Button onClick={handleSubmit} loading={submitting}>
                Create scenario
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}

function StepHeader({ step, label, active }: { step: number; label: string; active: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <span
        className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-semibold ${
          active ? "bg-primary text-black" : "bg-border text-muted"
        }`}
      >
        {step}
      </span>
      <p className="text-sm font-semibold text-heading">{label}</p>
    </div>
  );
}
