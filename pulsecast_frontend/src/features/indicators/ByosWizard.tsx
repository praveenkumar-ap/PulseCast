"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { useByosWizard } from "./hooks";
import type { IndicatorFrequency } from "@/types/domain";

const stepTitles = [
  "Basic information",
  "Where and how often",
  "Timing and reliability",
  "Owner & notes",
];

export function ByosWizard() {
  const {
    step,
    values,
    updateField,
    loading,
    error,
    successIndicator,
    goToNext,
    goToPrevious,
    submit,
  } = useByosWizard();

  if (successIndicator) {
    return (
      <Card title="Indicator registered">
        <p className="text-sm text-muted">
          We’ve registered your indicator. Data engineers can now connect the source.
        </p>
        <p className="mt-2 text-sm text-heading">{successIndicator.name}</p>
      </Card>
    );
  }

  return (
    <Card
      title={`Step ${step} of 4 — ${stepTitles[step - 1]}`}
      subtitle="Answer in plain language; no technical config needed."
    >
      <div className="space-y-4">
        {step === 1 && (
          <>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-heading">Indicator name *</span>
              <input
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={values.name}
                onChange={(e) => updateField("name", e.target.value)}
                placeholder="Flu hospitalizations – US CDC"
                required
              />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-heading">What does this measure?</span>
              <textarea
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={values.description || ""}
                onChange={(e) => updateField("description", e.target.value)}
                placeholder="Number of weekly hospital admissions for flu in the US."
                rows={3}
              />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-heading">Who provides this data? *</span>
              <input
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={values.providerName}
                onChange={(e) => updateField("providerName", e.target.value)}
                placeholder="CDC, WHO, Google Trends"
                required
              />
            </label>
          </>
        )}

        {step === 2 && (
          <>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-heading">Where does this data apply?</span>
              <input
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={values.geographyScope || ""}
                onChange={(e) => updateField("geographyScope", e.target.value)}
                placeholder="Global, US, India, Europe"
              />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-heading">How often does it update? *</span>
              <select
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={values.frequency}
                onChange={(e) => updateField("frequency", e.target.value as IndicatorFrequency)}
              >
                <option value="REAL_TIME">Real-time</option>
                <option value="HOURLY">Hourly</option>
                <option value="DAILY">Daily</option>
                <option value="WEEKLY">Weekly</option>
                <option value="MONTHLY">Monthly</option>
              </select>
            </label>
          </>
        )}

        {step === 3 && (
          <>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-heading">When does this data usually arrive?</span>
              <input
                type="number"
                min={0}
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={values.expectedUpdateLagHours ?? ""}
                onChange={(e) => updateField("expectedUpdateLagHours", Number(e.target.value))}
                placeholder="e.g., 24 hours after the day ends"
              />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-heading">Latest acceptable delay</span>
              <input
                type="number"
                min={0}
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={values.slaHours ?? ""}
                onChange={(e) => updateField("slaHours", Number(e.target.value))}
                placeholder="If later than this, we consider it late (hours)"
              />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-heading">How is this data delivered?</span>
              <select
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={values.dataSourceType || "Other"}
                onChange={(e) =>
                  updateField(
                    "dataSourceType",
                    e.target.value as "API" | "File upload" | "Database" | "Other"
                  )
                }
              >
                <option value="API">API</option>
                <option value="File upload">File upload</option>
                <option value="Database">Database</option>
                <option value="Other">Other</option>
              </select>
            </label>
          </>
        )}

        {step === 4 && (
          <>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-heading">Who is responsible for this data?</span>
              <input
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={values.dataOwnerContact || ""}
                onChange={(e) => updateField("dataOwnerContact", e.target.value)}
                placeholder="Name or email"
              />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-heading">Notes for data engineering</span>
              <textarea
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={values.notesForDataEngineering || ""}
                onChange={(e) => updateField("notesForDataEngineering", e.target.value)}
                placeholder="Any context that helps us connect the source."
                rows={3}
              />
            </label>
          </>
        )}

        {error && <p className="text-sm text-rose-200">{error}</p>}

        <div className="flex items-center justify-between">
          <div className="text-xs text-muted">Step {step} of 4</div>
          <div className="flex gap-2">
            {step > 1 && (
              <Button variant="secondary" size="sm" onClick={goToPrevious}>
                Back
              </Button>
            )}
            {step < 4 && (
              <Button size="sm" onClick={goToNext}>
                Next
              </Button>
            )}
            {step === 4 && (
              <Button size="sm" disabled={loading} onClick={submit}>
                {loading ? "Submitting…" : "Submit indicator"}
              </Button>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
