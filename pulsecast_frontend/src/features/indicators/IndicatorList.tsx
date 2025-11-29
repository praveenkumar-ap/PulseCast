"use client";

import React from "react";
import type { Indicator, IndicatorFreshnessStatus, IndicatorQualitySummary } from "@/types/domain";

type Props = {
  indicators: Indicator[];
  freshnessById?: Record<string, IndicatorFreshnessStatus>;
  qualityById?: Record<string, IndicatorQualitySummary>;
  onSelect: (indicator: Indicator) => void;
};

function trustLabel(score?: number) {
  if (score === undefined || score === null) return "Unknown";
  if (score >= 0.75) return "High";
  if (score >= 0.5) return "Medium";
  return "Low";
}

export function IndicatorList({ indicators, freshnessById, qualityById, onSelect }: Props) {
  if (!indicators.length) {
    return <p className="text-sm text-muted">No indicators match your filters.</p>;
  }

  return (
    <div className="grid gap-3 md:grid-cols-2">
      {indicators.map((ind) => {
        const fresh = freshnessById?.[ind.indicatorId];
        const qual = qualityById?.[ind.indicatorId];
        const freshnessLabel = fresh
          ? fresh.isWithinSla
            ? "On time"
            : fresh.lagHours
            ? `Late by ${fresh.lagHours}h`
            : "Unknown"
          : "Unknown";
        return (
          <button
            key={ind.indicatorId}
            className="card-surface w-full text-left transition hover:-translate-y-0.5 hover:border-primary/60"
            onClick={() => onSelect(ind)}
          >
            <div className="flex items-start justify-between gap-2 border-b border-border/80 px-4 py-3">
              <div>
                <p className="text-base font-semibold text-heading">{ind.name}</p>
                <p className="text-xs text-muted">Provider: {ind.provider}</p>
              </div>
              <span className="rounded-full bg-primary/10 px-2 py-1 text-xs text-primary">
                {ind.category || "Indicator"}
              </span>
            </div>
            <div className="space-y-1 px-4 py-3 text-sm text-muted">
              {ind.description && <p className="text-contrast">{ind.description}</p>}
              <p>Updates: {ind.frequency || "Unknown"}</p>
              <p>Freshness: {freshnessLabel}</p>
              <p>Trust: {trustLabel(ind.trustScore ?? qual?.trustScore)}</p>
            </div>
          </button>
        );
      })}
    </div>
  );
}
