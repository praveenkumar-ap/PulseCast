"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Table, TableCell, TableRow } from "@/components/ui/Table";
import { useScenariosList } from "./hooks";
import type { ScenarioStatus } from "@/types/domain";

const statusOptions: ScenarioStatus[] = [
  "DRAFT",
  "SUBMITTED",
  "APPROVED",
  "REJECTED",
  "ACTIVE",
  "ARCHIVED",
];

export function ScenariosListPage() {
  const router = useRouter();
  const [status, setStatus] = useState<ScenarioStatus | undefined>(undefined);
  const [runFilter, setRunFilter] = useState("");
  const { data, loading, error, reload } = useScenariosList({ status });

  const filtered = useMemo(() => {
    if (!data) return [];
    const needle = runFilter.toLowerCase();
    return data.filter(
      (s) =>
        (s.baseRunId || "").toLowerCase().includes(needle) ||
        s.name.toLowerCase().includes(needle)
    );
  }, [data, runFilter]);

  return (
    <div className="space-y-4">
      <div className="text-sm text-muted">
        <Link href="/home" className="text-primary hover:text-primary-strong">
          Home
        </Link>{" "}
        / Scenarios
      </div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-primary">Scenarios</p>
          <h1 className="text-2xl font-semibold text-heading">Scenario lab</h1>
          <p className="text-sm text-muted">Frame, submit, and track scenario assumptions and outputs.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={reload}>
            Refresh
          </Button>
          <Button size="sm" onClick={() => router.push("/scenarios/new")}>
            New scenario
          </Button>
        </div>
      </div>

      <Card>
        <div className="mb-3 grid gap-3 sm:grid-cols-3 sm:items-end">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Status</span>
            <select
              className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={status ?? ""}
              onChange={(e) =>
                setStatus(e.target.value ? (e.target.value as ScenarioStatus) : undefined)
              }
            >
              <option value="">All</option>
              {statusOptions.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Linked run id</span>
            <input
              className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={runFilter}
              onChange={(e) => setRunFilter(e.target.value)}
              placeholder="Filter by run id"
            />
          </label>
        </div>

        {loading && <p className="text-sm text-muted">Loading scenarios…</p>}
        {error && (
          <div className="flex items-center gap-2 text-sm text-rose-200">
            <span>Failed to load scenarios.</span>
            <Button size="sm" variant="secondary" onClick={reload}>
              Retry
            </Button>
          </div>
        )}

        {!loading && !error && filtered.length === 0 && (
          <p className="py-4 text-sm text-muted">No scenarios yet.</p>
        )}

        {!error && filtered.length > 0 && (
          <Table headers={["Name", "Status", "Run", "Created by", "Created at", "Updated at"]}>
            {filtered.map((s) => (
              <TableRow
                key={s.scenarioId}
                className="cursor-pointer"
                onClick={() => router.push(`/scenarios/${s.scenarioId}`)}
              >
                <TableCell>{s.name}</TableCell>
                <TableCell>{s.status}</TableCell>
                <TableCell>{s.baseRunId || "—"}</TableCell>
                <TableCell>{s.createdBy}</TableCell>
                <TableCell>{new Date(s.createdAt).toLocaleString()}</TableCell>
                <TableCell>{s.updatedAt ? new Date(s.updatedAt).toLocaleString() : "—"}</TableCell>
              </TableRow>
            ))}
          </Table>
        )}
      </Card>
    </div>
  );
}
