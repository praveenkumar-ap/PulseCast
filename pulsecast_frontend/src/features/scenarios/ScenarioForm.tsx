"use client";

import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

type ScenarioFormValues = {
  name: string;
  description?: string;
  baseRunId?: string;
  fromMonth: string;
  toMonth: string;
  upliftPercent: number;
  skuIds?: string;
};

type ScenarioFormProps = {
  initialValues?: Partial<ScenarioFormValues>;
  mode: "create" | "edit";
  onSubmit: (values: ScenarioFormValues) => Promise<void> | void;
  submitting?: boolean;
  errorMessage?: string | null;
  runOptions?: Array<{ value: string; label: string; fromMonth?: string; toMonth?: string }>;
  runOptionsLoading?: boolean;
};

export function ScenarioForm({
  initialValues,
  mode,
  onSubmit,
  submitting,
  errorMessage,
  runOptions,
  runOptionsLoading,
}: ScenarioFormProps) {
  const [useLatestRun, setUseLatestRun] = useState(!initialValues?.baseRunId);
  const [form, setForm] = useState<ScenarioFormValues>({
    name: initialValues?.name ?? "",
    description: initialValues?.description ?? "",
    baseRunId: initialValues?.baseRunId ?? "",
    fromMonth: initialValues?.fromMonth ?? "",
    toMonth: initialValues?.toMonth ?? "",
    upliftPercent: initialValues?.upliftPercent ?? 10,
    skuIds: initialValues?.skuIds ?? "",
  });

  useEffect(() => {
    if (useLatestRun) return;
    if (!form.baseRunId && runOptions && runOptions.length > 0) {
      const first = runOptions[0];
      setForm((f) => ({
        ...f,
        baseRunId: f.baseRunId || first.value || "",
        fromMonth: f.fromMonth || first.fromMonth || "",
        toMonth: f.toMonth || first.toMonth || "",
      }));
    }
  }, [form.baseRunId, form.fromMonth, form.toMonth, runOptions, useLatestRun]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || (!useLatestRun && !form.baseRunId) || !form.fromMonth || !form.toMonth) return;
    await onSubmit({
      ...form,
      baseRunId: useLatestRun ? "" : form.baseRunId,
      skuIds: form.skuIds,
    });
  };

  return (
    <Card title={mode === "create" ? "New scenario" : "Edit scenario"}>
      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Name *</span>
            <input
              className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              required
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Linked run ID {useLatestRun ? "(auto)" : "*"}</span>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={useLatestRun}
                onChange={(e) => setUseLatestRun(e.target.checked)}
              />
              <span className="text-xs text-muted">Use latest run with available forecasts</span>
            </div>
            {!useLatestRun && (
              <>
                {runOptions && runOptions.length > 0 ? (
                  <select
                    className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                    value={form.baseRunId}
                    onChange={(e) => {
                      const nextRunId = e.target.value;
                      const meta = runOptions.find((opt) => opt.value === nextRunId);
                      setForm((f) => ({
                        ...f,
                        baseRunId: nextRunId,
                        fromMonth: meta?.fromMonth || f.fromMonth,
                        toMonth: meta?.toMonth || f.toMonth,
                      }));
                    }}
                    required
                  >
                    {runOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                    value={form.baseRunId}
                    onChange={(e) => setForm((f) => ({ ...f, baseRunId: e.target.value }))}
                    required
                    placeholder={runOptionsLoading ? "Loading runs..." : "Enter run id"}
                  />
                )}
              </>
            )}
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">From month (YYYY-MM) *</span>
            <input
              className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={form.fromMonth}
              onChange={(e) => setForm((f) => ({ ...f, fromMonth: e.target.value }))}
              required
              placeholder="2024-01"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">To month (YYYY-MM) *</span>
            <input
              className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={form.toMonth}
              onChange={(e) => setForm((f) => ({ ...f, toMonth: e.target.value }))}
              required
              placeholder="2024-06"
            />
          </label>
        </div>

        <label className="flex flex-col gap-1 text-sm">
          <span className="text-muted">Description</span>
          <textarea
            className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            rows={3}
          />
        </label>

        <div className="grid gap-4 sm:grid-cols-2">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Uplift percent *</span>
            <input
              type="number"
              className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={form.upliftPercent}
              onChange={(e) =>
                setForm((f) => ({ ...f, upliftPercent: Number(e.target.value) }))
              }
              step="0.1"
              required
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">SKU IDs (comma separated, optional)</span>
            <input
              className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={form.skuIds}
              onChange={(e) => setForm((f) => ({ ...f, skuIds: e.target.value }))}
              placeholder="sku-1, sku-2"
            />
          </label>
        </div>

        {errorMessage && <p className="text-sm text-rose-200">{errorMessage}</p>}

        <div className="flex justify-end gap-2">
          <Button type="submit" disabled={submitting}>
            {submitting ? "Saving..." : mode === "create" ? "Create scenario" : "Save changes"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
