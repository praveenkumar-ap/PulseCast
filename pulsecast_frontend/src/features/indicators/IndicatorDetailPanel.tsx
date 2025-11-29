"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import type { Indicator, IndicatorFreshnessStatus, IndicatorQualitySummary } from "@/types/domain";

type Props = {
  indicator?: Indicator | null;
  freshness?: IndicatorFreshnessStatus;
  quality?: IndicatorQualitySummary;
  onClose: () => void;
};

function trustBadge(score?: number) {
  if (score === undefined || score === null) return "Unknown";
  if (score >= 0.75) return "High";
  if (score >= 0.5) return "Medium";
  return "Low";
}

export function IndicatorDetailPanel({ indicator, freshness, quality, onClose }: Props) {
  if (!indicator) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-40 w-full max-w-lg overflow-y-auto border-l border-border bg-panel/95 backdrop-blur-xl shadow-card">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Indicator</p>
          <p className="text-base font-semibold text-heading">{indicator.name}</p>
          <p className="text-xs text-muted">
            {indicator.provider} · {indicator.category || "Signal"}
          </p>
        </div>
        <button className="text-sm text-muted hover:text-heading" onClick={onClose}>
          Close
        </button>
      </div>

      <div className="space-y-4 p-4">
        <Card title="What this measures">
          <p className="text-sm text-muted">
            {indicator.description ||
              "This indicator tracks signals that help us sense demand and supply movements earlier."}
          </p>
        </Card>

        <Card title="Freshness" subtitle="On-time data keeps forecasts trustworthy.">
          <p className="text-sm text-muted">
            Last updated:{" "}
            {freshness?.lastDataTime
              ? new Date(freshness.lastDataTime).toLocaleString()
              : "Unknown"}
          </p>
          <p className="text-sm text-muted">
            {freshness?.slaFreshnessHours
              ? `Expected within ${freshness.slaFreshnessHours} hours`
              : "No freshness target set"}
            {freshness?.lagHours ? `; currently ${freshness.lagHours} hours behind` : ""}
          </p>
          <p className="mt-1 text-xs text-muted">
            If this data is late, forecasts that rely on it may react more slowly to changes.
          </p>
        </Card>

        <Card title="Trust" subtitle="How useful this signal has been historically.">
          <p className="text-sm text-muted">
            Trust: {trustBadge(indicator.trustScore ?? quality?.trustScore)}
          </p>
          {quality?.correlationScore !== undefined && (
            <p className="text-sm text-muted">
              Correlation with demand: {trustBadge(quality.correlationScore)}
            </p>
          )}
          {quality?.importanceScore !== undefined && (
            <p className="text-sm text-muted">
              Importance score: {trustBadge(quality.importanceScore)}
            </p>
          )}
          <p className="mt-1 text-xs text-muted">
            Higher trust means this signal has historically helped improve forecast accuracy.
          </p>
        </Card>

        <Card title="Usage hints">
          <ul className="list-disc space-y-1 pl-4 text-sm text-muted">
            <li>Review this indicator when demand is moving unexpectedly.</li>
            <li>Check freshness before relying on recent movements.</li>
            <li>Coordinate with data owners if the signal is repeatedly late.</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
