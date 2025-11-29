"use client";

import React from "react";
import { Table, TableCell, TableRow } from "@/components/ui/Table";
import type { ValueScenarioSummary } from "@/types/domain";
import { cn } from "@/lib/cn";

type Props = {
  scenarios: ValueScenarioSummary[];
};

function money(val?: number) {
  if (val === undefined || val === null) return "—";
  return `$${val.toLocaleString()}`;
}

function valueTag(total?: number) {
  if (total === undefined || total === null) return { label: "Unknown", tone: "text-muted" };
  if (total > 1_000_000) return { label: "High value", tone: "text-emerald-300" };
  if (total > 0) return { label: "Positive", tone: "text-primary" };
  return { label: "Negative impact", tone: "text-rose-300" };
}

export function ScenarioValueTable({ scenarios }: Props) {
  if (!scenarios.length) {
    return <p className="text-sm text-muted">No scenario value results available.</p>;
  }

  return (
    <Table
      headers={[
        "Scenario",
        "Linked forecast run",
        "Case",
        "Revenue uplift",
        "Scrap avoided",
        "Working capital + Opex",
        "Total value",
        "Status",
        "Signal",
      ]}
    >
      {scenarios.map((s) => {
        const total =
          s.totalValueEstimate ??
          (s.revenueUpliftEstimate ?? 0) +
            (s.scrapAvoidanceEstimate ?? 0) +
            (s.workingCapitalSavingsEstimate ?? 0) ??
          s.netBenefit ??
          0;
        const tag = valueTag(total);
        return (
          <TableRow key={`${s.scenarioId}-${s.caseLabel ?? "VALUE"}`}>
            <TableCell>{s.scenarioName ?? s.scenarioId}</TableCell>
            <TableCell>{s.linkedRunId ?? "—"}</TableCell>
            <TableCell>{s.caseLabel ?? "—"}</TableCell>
            <TableCell>{money(s.revenueUpliftEstimate)}</TableCell>
            <TableCell>{money(s.scrapAvoidanceEstimate)}</TableCell>
            <TableCell>{money(s.workingCapitalSavingsEstimate)}</TableCell>
            <TableCell>{money(total)}</TableCell>
            <TableCell>
              <span
                className={cn(
                  "rounded-full px-2 py-1 text-xs",
                  s.status === "APPROVED"
                    ? "bg-emerald-500/10 text-emerald-200"
                    : "bg-amber-500/10 text-amber-100"
                )}
              >
                {s.status ?? "Pending"}
              </span>
            </TableCell>
            <TableCell className={cn("text-sm font-semibold", tag.tone)}>{tag.label}</TableCell>
          </TableRow>
        );
      })}
    </Table>
  );
}
