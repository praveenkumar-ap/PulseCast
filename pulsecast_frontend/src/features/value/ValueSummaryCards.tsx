"use client";

import React from "react";
import { Card } from "@/components/ui/Card";

type Props = {
  totalValueUsd?: number;
  avgValuePerRunUsd?: number;
  totalRuns?: number;
};

function formatMoney(val?: number) {
  if (val === undefined || val === null) return "—";
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(1)}k`;
  return `$${val.toFixed(0)}`;
}

export function ValueSummaryCards({ totalValueUsd, avgValuePerRunUsd, totalRuns }: Props) {
  return (
    <div className="grid gap-3 sm:grid-cols-3">
      <Card>
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Total estimated value</p>
        <p className="mt-1 text-2xl font-semibold text-heading">{formatMoney(totalValueUsd)}</p>
      </Card>
      <Card>
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Average per forecast run</p>
        <p className="mt-1 text-2xl font-semibold text-heading">{formatMoney(avgValuePerRunUsd)}</p>
      </Card>
      <Card>
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Runs evaluated</p>
        <p className="mt-1 text-2xl font-semibold text-heading">{totalRuns ?? "—"}</p>
      </Card>
    </div>
  );
}
