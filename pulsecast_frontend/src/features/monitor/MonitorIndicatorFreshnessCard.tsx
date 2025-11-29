"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import type { IndicatorFreshnessStatus } from "@/types/domain";

type Props = {
  freshness: IndicatorFreshnessStatus[];
  overallHealth?: "GOOD" | "WARNING" | "CRITICAL";
};

export function MonitorIndicatorFreshnessCard({ freshness, overallHealth }: Props) {
  const total = freshness.length;
  const onTime = freshness.filter((f) => f.isWithinSla === true).length;
  const delayed = freshness.filter((f) => f.isWithinSla === false).length;
  const onTimePct = total > 0 ? Math.round((onTime / total) * 100) : 0;

  const healthLabel =
    overallHealth ||
    (onTimePct >= 85 ? "GOOD" : onTimePct >= 60 ? "WARNING" : "CRITICAL");

  return (
    <Card
      title="Data freshness"
      subtitle="Are signals arriving on time?"
      className="space-y-3"
    >
      <div className="flex items-center gap-4">
        <div className="rounded-2xl bg-panel px-4 py-3 text-sm">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Overall</p>
          <p className="text-lg font-semibold text-heading">{healthLabel}</p>
          <p className="text-xs text-muted">{onTimePct}% on time</p>
        </div>
        <div className="text-sm text-muted">
          <p>On-time indicators: {onTime}</p>
          <p>Late indicators: {delayed}</p>
          <p>Total tracked: {total}</p>
        </div>
      </div>
      <div className="space-y-2 text-sm">
        {freshness.slice(0, 5).map((f) => (
          <div
            key={f.indicatorId}
            className="flex items-center justify-between rounded-xl border border-border px-3 py-2"
          >
            <div>
              <p className="text-heading">{f.indicatorName}</p>
              <p className="text-xs text-muted">Provider: {f.provider}</p>
            </div>
            <p className="text-xs text-muted">
              {f.isWithinSla ? "On time" : f.lagHours ? `Late by ${f.lagHours}h` : "Unknown"}
            </p>
          </div>
        ))}
        {freshness.length === 0 && <p className="text-sm text-muted">No freshness data available.</p>}
      </div>
    </Card>
  );
}
