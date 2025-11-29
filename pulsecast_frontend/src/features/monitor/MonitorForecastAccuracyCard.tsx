"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import type { ForecastAccuracyPoint } from "@/types/domain";

type Props = {
  accuracy: ForecastAccuracyPoint[];
};

function summarize(points: ForecastAccuracyPoint[]) {
  if (!points.length) return { avg: 0, best: 0, worst: 0 };
  const values = points.map((p) => p.accuracyPercent ?? (p.wmape ? 100 - p.wmape : undefined)).filter((n): n is number => n !== undefined);
  if (!values.length) return { avg: 0, best: 0, worst: 0 };
  const avg = values.reduce((a, b) => a + b, 0) / values.length;
  return { avg, best: Math.max(...values), worst: Math.min(...values) };
}

export function MonitorForecastAccuracyCard({ accuracy }: Props) {
  const stats = summarize(accuracy);

  return (
    <Card
      title="Forecast accuracy"
      subtitle="Higher is better; shows how close forecasts were to actual demand over time."
      className="space-y-3"
    >
      <div className="flex items-center gap-4">
        <div className="rounded-2xl bg-panel px-4 py-3 text-sm">
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Average</p>
          <p className="text-lg font-semibold text-heading">{stats.avg.toFixed(1)}%</p>
        </div>
        <div className="text-sm text-muted">
          <p>Best recent: {stats.best.toFixed(1)}%</p>
          <p>Worst recent: {stats.worst.toFixed(1)}%</p>
          <p>Data points: {accuracy.length}</p>
        </div>
      </div>
      <div className="space-y-1 text-sm text-muted">
        {accuracy.slice(-10).map((p) => (
          <div
            key={`${p.date}-${p.runId ?? ""}`}
            className="flex items-center justify-between rounded-xl border border-border px-3 py-2"
          >
            <span>{p.date}</span>
            <span className="text-heading">
              {p.accuracyPercent !== undefined
                ? `${p.accuracyPercent.toFixed(1)}%`
                : p.wmape !== undefined
                ? `${(100 - p.wmape).toFixed(1)}%`
                : "—"}
            </span>
          </div>
        ))}
        {accuracy.length === 0 && <p className="text-sm text-muted">No accuracy data available.</p>}
      </div>
    </Card>
  );
}
