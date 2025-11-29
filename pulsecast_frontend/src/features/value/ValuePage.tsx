import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useValueOverview, useValueScenarios } from "./hooks";
import type { ValueCaseLabel } from "@/types/domain";

type StatusFilter = "ALL" | "DRAFT" | "SUBMITTED" | "APPROVED" | "REJECTED";

const statusOptions: StatusFilter[] = ["ALL", "DRAFT", "SUBMITTED", "APPROVED", "REJECTED"];

function formatCurrency(value?: number): string {
  if (value == null) return "—";
  if (Math.abs(value) >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (Math.abs(value) >= 1_000) return `$${(value / 1_000).toFixed(1)}K`;
  return `$${value.toFixed(0)}`;
}

export default function ValuePage() {
  const { data: overview, loading, error, reload } = useValueOverview();
  const [selectedRun, setSelectedRun] = useState<string | undefined>(undefined);
  const [status, setStatus] = useState<StatusFilter>("ALL");
  const { data: scenarios, loading: scenariosLoading, error: scenariosError, reload: reloadScenarios } =
    useValueScenarios(selectedRun, status === "ALL" ? undefined : status);
  const router = useRouter();

  const tiles = useMemo(() => {
    const b = overview.benchmarks;
    return [
      {
        title: "Revenue gained",
        subtitle: "Extra sales from avoiding stockouts",
        value: b?.totalRevenueUplift,
      },
      {
        title: "Scrap avoided",
        subtitle: "Value of inventory you didn’t scrap",
        value: b?.totalScrapAvoided,
      },
      {
        title: "Working capital",
        subtitle: "Cash unlocked by holding less excess stock",
        value: b?.totalWorkingCapitalImpact,
      },
      {
        title: "Planner time saved",
        subtitle: "Hours saved with automated decisions",
        value: b?.plannerTimeSavedHours,
        formatter: (v?: number) => (v == null ? "—" : `${v.toFixed(0)} hrs`),
      },
    ];
  }, [overview.benchmarks]);

  const runOptions = useMemo(
    () =>
      overview.runs.map((r) => ({
        label: r.familyName ? `${r.runId} · ${r.familyName}` : r.runId,
        value: r.runId,
        caseLabel: r.caseLabel,
      })),
    [overview.runs]
  );

  const handleRowClick = (scenarioId: string) => {
    router.push(`/scenarios/${scenarioId}`);
  };

  const renderTile = (title: string, subtitle: string, value?: number, formatter?: (v?: number) => string) => (
    <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 shadow">
      <div className="text-sm text-slate-300">{title}</div>
      <div className="text-2xl font-semibold text-white mt-1">{formatter ? formatter(value) : formatCurrency(value)}</div>
      <div className="text-xs text-slate-400 mt-1">{subtitle}</div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Value & ROI</h1>
        <p className="text-slate-300 text-sm">
          See how PulseCast protects revenue, reduces scrap, frees working capital, and saves planner time.
        </p>
      </div>

      {error && (
        <div className="rounded border border-red-500/50 bg-red-900/20 p-3 text-red-100">
          {error} <button onClick={reload}>Try again</button>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {tiles.map((t) => (
          <div key={t.title}>{renderTile(t.title, t.subtitle, t.value, t.formatter)}</div>
        ))}
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 shadow space-y-3">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div>
            <div className="text-white font-medium">Forecast runs</div>
            <div className="text-xs text-slate-400">Value by forecast run and case.</div>
          </div>
          <div className="flex gap-2">
            <select
              className="bg-slate-800 text-white text-sm rounded px-2 py-1"
              value={selectedRun ?? ""}
              onChange={(e) => setSelectedRun(e.target.value || undefined)}
            >
              <option value="">All runs</option>
              {runOptions.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label} {o.caseLabel ? `(${o.caseLabel})` : ""}
                </option>
              ))}
            </select>
            <select
              className="bg-slate-800 text-white text-sm rounded px-2 py-1"
              value={status}
              onChange={(e) => setStatus(e.target.value as StatusFilter)}
            >
              {statusOptions.map((s) => (
                <option key={s} value={s}>
                  {s === "ALL" ? "All statuses" : s}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-slate-200">
            <thead className="text-slate-400">
              <tr>
                <th className="text-left py-2">Run</th>
                <th className="text-left py-2">Case</th>
                <th className="text-left py-2">Revenue uplift</th>
                <th className="text-left py-2">Scrap avoided</th>
                <th className="text-left py-2">Working capital</th>
                <th className="text-left py-2">Total value</th>
              </tr>
            </thead>
            <tbody>
              {overview.runs.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-3 text-slate-400">
                    {loading ? "Loading runs..." : "Value will appear after you run forecasts."}
                  </td>
                </tr>
              )}
              {overview.runs.map((r) => (
                <tr key={r.runId} className="border-t border-slate-800">
                  <td className="py-2">{r.runId}</td>
                  <td className="py-2">{r.caseLabel ?? "—"}</td>
                  <td className="py-2">{formatCurrency(r.revenueUpliftEstimate)}</td>
                  <td className="py-2">{formatCurrency(r.scrapAvoidanceEstimate)}</td>
                  <td className="py-2">{formatCurrency(r.workingCapitalSavingsEstimate)}</td>
                  <td className="py-2">{formatCurrency(r.totalValueEstimate)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 shadow space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-white font-medium">Scenarios</div>
            <div className="text-xs text-slate-400">Value for scenarios linked to selected runs.</div>
          </div>
          {scenariosError && (
            <div className="text-xs text-red-300">
              {scenariosError} <button onClick={reloadScenarios}>Try again</button>
            </div>
          )}
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-slate-200">
            <thead className="text-slate-400">
              <tr>
                <th className="text-left py-2">Scenario</th>
                <th className="text-left py-2">Status</th>
                <th className="text-left py-2">Linked run</th>
                <th className="text-left py-2">Revenue uplift</th>
                <th className="text-left py-2">Scrap avoided</th>
                <th className="text-left py-2">Working capital</th>
                <th className="text-left py-2">Total value</th>
              </tr>
            </thead>
            <tbody>
              {scenarios.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-3 text-slate-400">
                    {scenariosLoading ? "Loading scenarios..." : "Value will appear after scenarios are created."}
                  </td>
                </tr>
              )}
              {scenarios.map((s) => (
                <tr
                  key={s.scenarioId}
                  className="border-t border-slate-800 hover:bg-slate-800/40 cursor-pointer"
                  onClick={() => handleRowClick(s.scenarioId)}
                >
                  <td className="py-2">{s.scenarioName ?? s.scenarioId}</td>
                  <td className="py-2">{s.status ?? "—"}</td>
                  <td className="py-2">{s.linkedRunId ?? "—"}</td>
                  <td className="py-2">{formatCurrency(s.revenueUpliftEstimate)}</td>
                  <td className="py-2">{formatCurrency(s.scrapAvoidanceEstimate)}</td>
                  <td className="py-2">{formatCurrency(s.workingCapitalSavingsEstimate)}</td>
                  <td className="py-2">{formatCurrency(s.totalValueEstimate ?? s.netBenefit)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
