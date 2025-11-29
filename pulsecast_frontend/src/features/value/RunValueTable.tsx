"use client";

import React from "react";
import { Table, TableCell, TableRow } from "@/components/ui/Table";
import type { ValueRunSummary } from "@/types/domain";

type Props = {
  runs: ValueRunSummary[];
  selectedRunId?: string;
  onSelect?: (run: ValueRunSummary) => void;
};

function money(val?: number) {
  if (val === undefined || val === null) return "—";
  return `$${val.toLocaleString()}`;
}

export function RunValueTable({ runs, selectedRunId, onSelect }: Props) {
  if (!runs.length) {
    return <p className="text-sm text-muted">No value results available yet.</p>;
  }

  return (
    <Table
      headers={[
        "Forecast run",
        "Case",
        "Revenue uplift",
        "Scrap avoided",
        "Working capital + Opex",
        "Total value",
        "Period",
      ]}
    >
      {runs.map((r) => {
        const isActive = r.runId === selectedRunId;
        const total =
          r.totalValueEstimate ??
          (r.revenueUpliftEstimate ?? 0) +
            (r.scrapAvoidanceEstimate ?? 0) +
            (r.workingCapitalSavingsEstimate ?? 0);
        return (
          <TableRow
            key={`${r.runId}-${r.caseLabel}`}
            className="cursor-pointer"
            onClick={() => onSelect?.(r)}
          >
            <TableCell className={isActive ? "font-semibold text-primary" : ""}>{r.runId}</TableCell>
            <TableCell>{r.caseLabel}</TableCell>
            <TableCell>{money(r.revenueUpliftEstimate)}</TableCell>
            <TableCell>{money(r.scrapAvoidanceEstimate)}</TableCell>
            <TableCell>{money(r.workingCapitalSavingsEstimate)}</TableCell>
            <TableCell>{money(total)}</TableCell>
            <TableCell>
              {r.periodStart && r.periodEnd ? `${r.periodStart} → ${r.periodEnd}` : "—"}
            </TableCell>
          </TableRow>
        );
      })}
    </Table>
  );
}
