"use client";

import React from "react";
import { Table, TableCell, TableRow } from "@/components/ui/Table";
import type { InventoryPolicy } from "@/types/domain";

type Props = {
  policies: InventoryPolicy[];
  onSelect: (policy: InventoryPolicy) => void;
};

export function OptimizerPolicyTable({ policies, onSelect }: Props) {
  if (!policies.length) {
    return <p className="text-sm text-muted">No policies available for this selection.</p>;
  }

  return (
    <Table
      headers={[
        "Test / SKU",
        "Policy",
        "Base stock",
        "Target stock",
        "Safety stock",
        "Expiry horizon",
        "Substitution",
      ]}
    >
      {policies.map((p) => {
        const targetRange =
          p.policyType === "SS_POLICY" && p.s !== undefined && p.S !== undefined
            ? `${p.s} → ${p.S}`
            : p.targetStockUnits !== undefined
            ? `${p.targetStockUnits.toFixed(0)} units`
            : p.baseStockLevel !== undefined
            ? `${p.baseStockLevel} units`
            : "—";
        const baseStock =
          p.baseStockLevel !== undefined
            ? `${p.baseStockLevel} units`
            : p.cycleStockUnits !== undefined
            ? `${p.cycleStockUnits.toFixed(0)} units`
            : "—";
        const safety = p.safetyStock ?? p.safetyStock === 0 ? p.safetyStock : p.safetyStock;
        return (
          <TableRow key={p.policyId ?? `${p.skuId}-${p.effectiveFrom}`} className="cursor-pointer" onClick={() => onSelect(p)}>
            <TableCell>
              <div className="font-semibold text-heading">
                {p.skuName || p.skuCode || p.skuId}
              </div>
              <div className="text-xs text-muted">
                {p.familyName || p.familyCode ? `Family: ${p.familyName || p.familyCode}` : ""}
              </div>
            </TableCell>
            <TableCell>{p.policyType === "SS_POLICY" ? "(s, S)" : "Recommended"}</TableCell>
            <TableCell>{baseStock}</TableCell>
            <TableCell>{targetRange}</TableCell>
            <TableCell>{safety !== undefined ? `${safety.toFixed(0)} units` : "—"}</TableCell>
            <TableCell>{p.expiryDays ? `${p.expiryDays} days` : "—"}</TableCell>
            <TableCell>
              {p.substitutionAllowed ? (
                <span className="text-emerald-300">Yes</span>
              ) : (
                <span className="text-muted">No</span>
              )}
            </TableCell>
          </TableRow>
        );
      })}
    </Table>
  );
}
