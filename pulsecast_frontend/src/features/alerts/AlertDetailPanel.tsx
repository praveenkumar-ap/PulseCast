"use client";

import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import type { Alert, AlertStatus } from "@/types/domain";

type Props = {
  alert?: Alert | null;
  onClose: () => void;
  onUpdateStatus: (status: AlertStatus) => Promise<void>;
};

function describeAlert(alert: Alert) {
  switch (alert.type) {
    case "LEADING_INDICATOR_SPIKE":
      return "A leading indicator is moving faster than expected. Forecasts depending on it may need a refresh.";
    case "DEMAND_SHOCK":
      return "Demand is moving sharply against forecast. Check if you need to adjust stocking plans.";
    case "SUPPLY_RISK":
      return "Supply-side risk detected. Align with supply planning to avoid stockouts.";
    case "DATA_STALENESS":
      return "Data feeding this forecast is late. Outputs may be less reliable until it catches up.";
    default:
      return "An alert needs your attention. Review the details and decide next steps.";
  }
}

export function AlertDetailPanel({ alert, onClose, onUpdateStatus }: Props) {
  if (!alert) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-40 w-full max-w-lg overflow-y-auto border-l border-border bg-panel/95 backdrop-blur-xl shadow-card">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-muted">Alert</p>
          <p className="text-base font-semibold text-heading">{alert.title}</p>
          <p className="text-xs text-muted">
            Urgency: {alert.severity} · Status: {alert.status}
          </p>
        </div>
        <button className="text-sm text-muted hover:text-heading" onClick={onClose}>
          Close
        </button>
      </div>

      <div className="space-y-4 p-4">
        <div>
          <h3 className="text-sm font-semibold text-heading">What this alert means</h3>
          <p className="mt-1 text-sm text-muted">{describeAlert(alert)}</p>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-heading">Details</h3>
          <div className="mt-2 space-y-1 text-sm text-muted">
            <div>
              <span className="text-heading">Raised:</span> {new Date(alert.triggeredAt).toLocaleString()}
            </div>
            {alert.updatedAt && (
              <div>
                <span className="text-heading">Last updated:</span> {new Date(alert.updatedAt).toLocaleString()}
              </div>
            )}
            {alert.indicatorName && (
              <div>
                <span className="text-heading">Indicator:</span> {alert.indicatorName}
              </div>
            )}
            {alert.familyName && (
              <div>
                <span className="text-heading">Family:</span> {alert.familyName}
              </div>
            )}
            {alert.skuName && (
              <div>
                <span className="text-heading">SKU:</span> {alert.skuName}
              </div>
            )}
            {alert.summary && (
              <div>
                <span className="text-heading">What changed:</span> {alert.summary}
              </div>
            )}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-heading">What you can do next</h3>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-muted">
            <li>Review the forecast for the affected product for the next few months.</li>
            <li>Check supply plans to avoid stockouts or excess, depending on the alert.</li>
            <li>If data keeps coming in late, work with data owners to improve freshness.</li>
          </ul>
        </div>

        <div className="flex flex-wrap gap-2">
          {alert.relatedRunName && (
            <Link
              className="rounded-full border border-border px-3 py-1 text-sm text-primary hover:border-primary"
              href={`/forecasts/${alert.relatedRunName}`}
            >
              Open forecast run
            </Link>
          )}
          {alert.relatedScenarioName && (
            <Link
              className="rounded-full border border-border px-3 py-1 text-sm text-primary hover:border-primary"
              href={`/scenarios/${alert.relatedScenarioName}`}
            >
              Open scenario
            </Link>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" size="sm" onClick={() => onUpdateStatus("ACKNOWLEDGED")}>
            Mark as acknowledged
          </Button>
          <Button size="sm" onClick={() => onUpdateStatus("RESOLVED")}>
            Mark as resolved
          </Button>
        </div>
      </div>
    </div>
  );
}
