"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import type { InventoryPolicy } from "@/types/domain";

type Props = {
  policy?: InventoryPolicy | null;
  onClose: () => void;
};

export function OptimizerPolicyDetailPanel({ policy, onClose }: Props) {
  if (!policy) return null;
  return (
    <div className="fixed inset-y-0 right-0 z-30 w-full max-w-md overflow-y-auto border-l border-border bg-panel/95 backdrop-blur-xl shadow-card">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Policy details</p>
          <p className="text-base font-semibold text-heading">{policy.skuName || policy.skuId}</p>
        </div>
        <button className="text-sm text-muted hover:text-heading" onClick={onClose}>
          Close
        </button>
      </div>
      <div className="space-y-4 p-4">
        <Card title="What this means" subtitle="Plain-language explanation of key levers.">
          <ul className="space-y-2 text-sm text-muted">
            <li>
              <strong className="text-heading">Policy type:</strong> {policy.policyType === "SS_POLICY" ? "(s,S)" : "Recommended base stock"} — orders
              trigger when stock hits the lower point and restock to the upper target.
            </li>
            <li>
              <strong className="text-heading">Target stock:</strong> total units to hold after a reorder (cycle stock + safety stock) so you cover expected demand plus a buffer.
            </li>
            <li>
              <strong className="text-heading">Safety stock:</strong> extra units to buffer demand swings; more safety lowers stockouts but raises holding/expiry risk.
            </li>
            <li>
              <strong className="text-heading">Expiry horizon:</strong> how long before stock is at risk of expiring; shorter horizons need tighter ordering.
            </li>
          </ul>
        </Card>
        <Card title="Numbers at a glance">
          <dl className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt className="text-muted">Target stock</dt>
              <dd className="text-heading">
                {policy.targetStockUnits !== undefined
                  ? `${policy.targetStockUnits.toFixed(0)} units`
                  : policy.baseStockLevel !== undefined
                  ? `${policy.baseStockLevel} units`
                  : "—"}
              </dd>
            </div>
            <div>
              <dt className="text-muted">Base stock</dt>
              <dd className="text-heading">
                {policy.baseStockLevel !== undefined
                  ? `${policy.baseStockLevel} units`
                  : policy.cycleStockUnits !== undefined
                  ? `${policy.cycleStockUnits.toFixed(0)} units`
                  : "—"}
              </dd>
            </div>
            <div>
              <dt className="text-muted">Safety stock</dt>
              <dd className="text-heading">
                {policy.safetyStock !== undefined ? `${policy.safetyStock.toFixed(0)} units` : "—"}
              </dd>
            </div>
            <div>
              <dt className="text-muted">Service level target</dt>
              <dd className="text-heading">
                {policy.serviceLevelTarget !== undefined ? `${(policy.serviceLevelTarget * 100).toFixed(1)}%` : "—"}
              </dd>
            </div>
            <div>
              <dt className="text-muted">Expiry horizon</dt>
              <dd className="text-heading">{policy.expiryDays ? `${policy.expiryDays} days` : "—"}</dd>
            </div>
            <div>
              <dt className="text-muted">Stock range</dt>
              <dd className="text-heading">
                {policy.s !== undefined && policy.S !== undefined ? `${policy.s} → ${policy.S}` : "—"}
              </dd>
            </div>
          </dl>
        </Card>
        <Card title="Context">
          <p className="text-sm text-muted">
            Based on run {policy.runId}
            {policy.scenarioId ? ` and scenario ${policy.scenarioId}` : ""}. Effective {policy.effectiveFrom}
            {policy.effectiveTo ? ` to ${policy.effectiveTo}` : ""}.
          </p>
        </Card>
      </div>
    </div>
  );
}
