"use client";

import Link from "next/link";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/Card";
import { Stat } from "@/components/ui/Stat";
import { Button } from "@/components/ui/Button";
import { useScenariosList } from "@/features/scenarios/hooks";
import { useAlertsList } from "@/features/alerts/hooks";
import { useIndicatorsCatalog } from "@/features/indicators/hooks";

const quickLinks = [
  { label: "Forecasts", href: "/forecasts", summary: "Update outlooks and align assumptions." },
  { label: "Scenarios", href: "/scenarios", summary: "Run sensitivities to stress key levers." },
  { label: "Optimizer", href: "/optimizer", summary: "Pick the next move given constraints." },
  { label: "Alerts", href: "/alerts", summary: "Tighten guardrails for sudden changes." },
];

export function HomePage() {
  const { data: scenarios, loading: scenariosLoading, error: scenariosError } = useScenariosList({
    status: "SUBMITTED",
  });
  const { alerts, loading: alertsLoading, error: alertsError } = useAlertsList();
  const { indicators, loading: indicatorsLoading, error: indicatorsError } = useIndicatorsCatalog();

  const scenarioPending = scenarios?.length ?? 0;
  const highAlerts = alerts?.filter((a) => a.severity === "HIGH" || a.severity === "CRITICAL").length ?? 0;
  const liveSignals = indicators?.length ?? 0;
  const tasks = [
    {
      key: "scenarios",
      title: "Review open scenarios",
      subtitle: "See which what-if plans are waiting for approval.",
      cta: "Open scenarios",
      href: "/scenarios",
      countLabel: scenarioPending > 0 ? `${scenarioPending} waiting` : scenariosLoading ? "…" : "All caught up",
      hasError: Boolean(scenariosError),
    },
    {
      key: "alerts",
      title: "Check high-risk alerts",
      subtitle: "Look at alerts that may need your decision today.",
      cta: "Open alerts",
      href: "/alerts",
      countLabel: alertsLoading ? "…" : alertsError ? "n/a" : highAlerts > 0 ? `${highAlerts} high priority` : "None high priority",
      hasError: Boolean(alertsError),
    },
    {
      key: "signals",
      title: "Catch up on live signals",
      subtitle: "See which signals are feeding forecasts and if anything is stale.",
      cta: "Open indicators",
      href: "/indicators",
      countLabel: indicatorsLoading ? "…" : indicatorsError ? "n/a" : liveSignals > 0 ? `${liveSignals} signals` : "No signals listed",
      hasError: Boolean(indicatorsError),
    },
    {
      key: "optimizer",
      title: "See recent optimizer runs",
      subtitle: "Review recommended stock policies and expiry risks.",
      cta: "Open optimizer",
      href: "/optimizer",
      countLabel: "—",
      hasError: false,
    },
  ];

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Workspace"
        title="PulseCast Overview"
        description="See what’s changing, what needs your attention, and where to act next."
        actions={
          <div className="flex gap-2">
            <Button variant="secondary" size="sm">
              Export
            </Button>
            <Button size="sm">Create</Button>
          </div>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat
          label="Live signals – data sources currently feeding your forecasts"
          value={indicatorsLoading ? "…" : indicatorsError ? "n/a" : `${liveSignals}`}
          delta="+5 this week"
          tone="positive"
          className="rounded-2xl border-white/10 bg-white/[0.03]"
        />
        <Stat label="Experiments – scenario tests in progress" value="8" delta="3 running" tone="neutral" className="rounded-2xl border-white/10 bg-white/[0.03]" />
        <Stat
          label="Alerts watching – signals that may need action"
          value={alertsLoading ? "…" : alertsError ? "n/a" : `${alerts?.length ?? 0}`}
          delta={highAlerts > 0 ? `${highAlerts} high` : "Stable"}
          tone={highAlerts > 0 ? "negative" : "positive"}
          className="rounded-2xl border-white/10 bg-white/[0.03]"
        />
        <Stat label="Avg. ROI delta – change vs prior period" value="+12.4%" delta="QoQ" tone="positive" className="rounded-2xl border-white/10 bg-white/[0.03]" />
      </div>

      <div className="grid gap-4 lg:grid-cols-3 items-stretch">
        <Card
          title="Priorities for this cycle"
          subtitle="Keep these flows warm as you iterate."
          actions={
            <Link className="text-sm font-semibold text-primary hover:text-primary-strong" href="/optimizer">
              Open optimizer →
            </Link>
          }
          className="rounded-3xl border-white/15 bg-white/[0.03] lg:col-span-2 h-full"
        >
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl border border-border/60 bg-white/[0.03] p-4">
              <p className="text-sm font-semibold text-heading">Refresh demand curves</p>
              <p className="mt-1 text-sm text-muted">Pull the newest signals for Q3 and rerun the optimistic case.</p>
              <p className="mt-3 text-xs text-primary">Due: Today</p>
            </div>
            <div className="rounded-2xl border border-border/60 bg-white/[0.03] p-4">
              <p className="text-sm font-semibold text-heading">Scenario bake-off</p>
              <p className="mt-1 text-sm text-muted">Compare baseline vs. constrained spend and ship the diff.</p>
              <p className="mt-3 text-xs text-primary">Due: Tomorrow</p>
            </div>
          </div>
        </Card>

        <Card title="Health snapshot" subtitle="Signals holding steady across the stack." className="rounded-3xl border-white/15 bg-white/[0.03]">
          <ul className="space-y-2 text-sm text-muted">
            <li className="flex items-center justify-between">
              <span>Data latency</span>
              <span className="rounded-full bg-emerald-500/10 px-2 py-1 text-xs font-semibold text-emerald-300">Good</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Scenario freshness</span>
              <span className="rounded-full bg-amber-500/10 px-2 py-1 text-xs font-semibold text-amber-300">Needs run</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Alert noise</span>
              <span className="rounded-full bg-primary/10 px-2 py-1 text-xs font-semibold text-primary">In range</span>
            </li>
          </ul>
        </Card>
      </div>

      <Card
        title="What needs your attention"
        subtitle="Shortcuts into the work, not another menu. Use the sidebar for full navigation."
        className="rounded-3xl border-white/15 bg-white/[0.03]"
      >
        <div className="grid gap-3 md:grid-cols-2">
          {tasks.map((task) => (
            <div
              key={task.key}
              className="flex h-full flex-col justify-between rounded-2xl border border-border/60 bg-white/[0.02] p-4"
            >
              <div className="space-y-1">
                <p className="text-sm font-semibold text-heading">{task.title}</p>
                <p className="text-sm text-muted">{task.subtitle}</p>
                <p className="text-xs text-primary">
                  {task.hasError ? "n/a" : task.countLabel}
                </p>
              </div>
              <div className="mt-3">
                <Link
                  href={task.href}
                  className="inline-flex items-center rounded-lg border border-primary/60 px-3 py-2 text-sm font-semibold text-primary transition hover:border-primary hover:bg-primary/10"
                >
                  {task.cta} →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

export default HomePage;
