"use client";

import React from "react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { MonitorIndicatorFreshnessCard } from "./MonitorIndicatorFreshnessCard";
import { MonitorForecastAccuracyCard } from "./MonitorForecastAccuracyCard";
import { useMonitorDashboard } from "./hooks";

export function MonitorPage() {
  const { indicatorFreshness, forecastAccuracy, summary, filters, setFilters, loading, error, reload } =
    useMonitorDashboard();

  return (
    <div className="space-y-5">
      <div className="text-sm text-muted">
        <Link href="/home" className="text-primary hover:text-primary-strong">
          Home
        </Link>{" "}
        / Monitor
      </div>
      <div>
        <p className="text-sm uppercase tracking-[0.2em] text-primary">Monitor</p>
        <h1 className="text-2xl font-semibold text-heading">Monitor – Data & Forecast Health</h1>
        <p className="text-sm text-muted">
          This page shows whether your signals are arriving on time and how well the forecasts are performing.
        </p>
      </div>

      <Card title="What these metrics mean">
        <p className="text-sm text-muted">
          Data freshness tells you how up-to-date your signals are; late data can make forecasts slower to react.
          Forecast accuracy shows how close predictions were to actual demand; higher is better.
        </p>
      </Card>

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-4">
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-muted">Accuracy time range</span>
              <select
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={filters.accuracyTimeRange}
                onChange={(e) =>
                  setFilters((f) => ({ ...f, accuracyTimeRange: e.target.value as typeof filters.accuracyTimeRange }))
                }
              >
                <option value="LAST_30_DAYS">Last 30 days</option>
                <option value="LAST_90_DAYS">Last 90 days</option>
                <option value="LAST_YEAR">Last year</option>
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-muted">Freshness view</span>
              <select
                className="rounded-lg border border-border bg-panel px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={filters.freshnessFilter}
                onChange={(e) =>
                  setFilters((f) => ({ ...f, freshnessFilter: e.target.value as typeof filters.freshnessFilter }))
                }
              >
                <option value="ALL">All indicators</option>
                <option value="ON_TIME">Only on-time</option>
                <option value="DELAYED">Only delayed</option>
              </select>
            </label>
          </div>
          <Button variant="secondary" size="sm" onClick={reload}>
            Refresh
          </Button>
        </div>
      </Card>

      {loading && <p className="text-sm text-muted">Checking data and forecast health…</p>}
      {error && (
        <div className="flex items-center gap-2 text-sm text-rose-200">
          <span>We couldn’t load monitor data. Please try again.</span>
          <Button size="sm" variant="secondary" onClick={reload}>
            Retry
          </Button>
        </div>
      )}

      {!error && (
        <div className="grid gap-4 md:grid-cols-2">
          <MonitorIndicatorFreshnessCard
            freshness={indicatorFreshness}
            overallHealth={summary?.overallDataHealth}
          />
          <MonitorForecastAccuracyCard accuracy={forecastAccuracy} />
        </div>
      )}
    </div>
  );
}
