"use client";

import React from "react";
import { Table, TableCell, TableRow } from "@/components/ui/Table";
import type { Alert } from "@/types/domain";

type Props = {
  alerts: Alert[];
  onSelect: (alert: Alert) => void;
};

const severityLabel: Record<string, string> = {
  LOW: "Low urgency",
  MEDIUM: "Medium urgency",
  HIGH: "High urgency",
  CRITICAL: "Critical urgency",
};

const statusLabel: Record<string, string> = {
  OPEN: "New",
  ACKNOWLEDGED: "Acknowledged",
  RESOLVED: "Resolved",
};

function friendlyType(type: Alert["type"]) {
  switch (type) {
    case "LEADING_INDICATOR_SPIKE":
      return "Indicator spike";
    case "DEMAND_SHOCK":
      return "Demand shock";
    case "SUPPLY_RISK":
      return "Supply risk";
    case "DATA_STALENESS":
      return "Data quality issue";
    default:
      return "Alert";
  }
}

export function AlertsTable({ alerts, onSelect }: Props) {
  if (!alerts.length) {
    return <p className="text-sm text-muted">No alerts for these filters.</p>;
  }

  return (
    <Table headers={["Title", "What changed", "Urgency", "When", "Category", "Status"]}>
      {alerts.map((alert) => (
        <TableRow
          key={alert.id}
          className="cursor-pointer"
          onClick={() => onSelect(alert)}
          tabIndex={0}
        >
          <TableCell>
            <div className="font-semibold text-heading">{alert.title}</div>
            <div className="text-xs text-muted">{friendlyType(alert.type)}</div>
          </TableCell>
          <TableCell>{alert.summary || "See details"}</TableCell>
          <TableCell>
            <span className="text-xs font-semibold text-primary">
              {severityLabel[alert.severity] ?? alert.severity}
            </span>
          </TableCell>
          <TableCell>{new Date(alert.triggeredAt).toLocaleString()}</TableCell>
          <TableCell>{alert.category || "—"}</TableCell>
          <TableCell>{statusLabel[alert.status] ?? alert.status}</TableCell>
        </TableRow>
      ))}
    </Table>
  );
}
