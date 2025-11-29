"use client";

import React, { useMemo, useState } from "react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { useValueRuns } from "@/features/value/hooks";
import { useGenaiHelper } from "@/features/genaiHooks";
import { GenaiPanel } from "@/features/GenaiPanel";
import { GenaiTriggerButton } from "@/features/GenaiTriggerButton";

type LoggedImpact = {
  title: string;
  amountUsd?: number;
  note?: string;
};

type ReviewForm = {
  date: string;
  time: string;
  audience: string;
};

export default function RoiPage() {
  const { runs: runValues, loading, error, reload: reloadRuns } = useValueRuns();
  const [impactOpen, setImpactOpen] = useState(false);
  const [reviewOpen, setReviewOpen] = useState(false);
  const [loggedImpacts, setLoggedImpacts] = useState<LoggedImpact[]>([]);
  const [scheduledReviews, setScheduledReviews] = useState<ReviewForm[]>([]);
  const [impactForm, setImpactForm] = useState<LoggedImpact>({ title: "" });
  const [reviewForm, setReviewForm] = useState<ReviewForm>({ date: "", time: "", audience: "" });
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const genai = useGenaiHelper(
    { scope: "VALUE_OVERVIEW", runId: runValues[0]?.runId, runLabel: runValues[0]?.runLabel },
    "Explain how this ROI view ties back to the forecast runs in plain language."
  );

  const initiatives = useMemo(
    () => [
      { name: "Activation uplift", owner: "Growth", roi: "+$1.2M" },
      { name: "NPS to retention", owner: "Product", roi: "+$630k" },
      { name: "Cost-to-serve", owner: "Ops", roi: "+$380k" },
    ],
    []
  );

  const exportDeck = () => {
    if (!runValues.length) return;
    const header = [
      "Forecast run",
      "Case",
      "Revenue uplift",
      "Scrap avoided",
      "Working capital savings",
      "Total value",
      "Period",
    ];
    const rows = runValues.map((r) => [
      r.runLabel || r.runId,
      r.caseLabel,
      r.revenueUpliftUsd ?? "",
      r.scrapAvoidedUsd ?? "",
      r.workingCapitalSavingsUsd ?? "",
      r.totalValueUsd ?? "",
      r.periodLabel ?? "",
    ]);
    const csv = [header, ...rows]
      .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","))
      .join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "pulsecast_value_export.csv";
    link.click();
    URL.revokeObjectURL(url);
    setActionMessage("Deck exported with current run value data.");
  };

  const submitImpact = () => {
    if (!impactForm.title) return;
    setLoggedImpacts((list) => [...list, impactForm]);
    setImpactForm({ title: "" });
    setActionMessage("Impact note captured. Add more detail anytime.");
    setImpactOpen(false);
  };

  const submitReview = () => {
    if (!reviewForm.date || !reviewForm.time) return;
    setScheduledReviews((list) => [...list, reviewForm]);
    setActionMessage("Review scheduled. Add it to your calendar.");
    setReviewForm({ date: "", time: "", audience: "" });
    setReviewOpen(false);
  };

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="ROI"
        title="Impact tracker"
        description="Close the loop between forecasts, scenarios, and realized outcomes."
        actions={
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" onClick={exportDeck} disabled={!runValues.length || loading}>
              Export deck
            </Button>
            <Button size="sm" onClick={() => setImpactOpen(true)}>
              Log impact
            </Button>
            <GenaiTriggerButton
              onClick={() =>
                genai.openPanel(
                  { scope: "VALUE_OVERVIEW", runId: runValues[0]?.runId, runLabel: runValues[0]?.runLabel },
                  "Explain this ROI view and the biggest drivers of impact."
                )
              }
              label="Ask AI"
            />
          </div>
        }
      />

      {loading && <p className="text-sm text-muted">Loading value data…</p>}
      {error && (
        <div className="rounded-xl border border-red-400/40 bg-red-500/10 p-3 text-sm text-red-100">
          <p>We could not load value metrics. Please retry.</p>
          <Button variant="secondary" size="sm" className="mt-2" onClick={reloadRuns}>
            Retry
          </Button>
        </div>
      )}
      {actionMessage && <p className="text-sm text-primary">{actionMessage}</p>}

      <Card title="Portfolio" subtitle="Where the value is coming from.">
        <div className="grid gap-3 md:grid-cols-3">
          {initiatives.map((item) => (
            <div key={item.name} className="rounded-xl border border-border bg-white/[0.02] p-4">
              <p className="text-sm font-semibold text-heading">{item.name}</p>
              <p className="mt-1 text-sm text-muted">Owner: {item.owner}</p>
              <p className="mt-3 text-xs text-primary">ROI: {item.roi}</p>
            </div>
          ))}
        </div>
      </Card>

      <Card
        title="Next reviews"
        subtitle="Keep stakeholders aligned on realized value."
        actions={
          <Button size="sm" onClick={() => setReviewOpen(true)}>
            Schedule review
          </Button>
        }
      >
        <ul className="space-y-2 text-sm text-muted">
          <li>• Sync with Finance on quarterly reconciliation.</li>
          <li>• Publish deltas between forecasted vs. realized lift.</li>
          <li>• Push highlights to the exec Monitor view.</li>
          {scheduledReviews.map((r, idx) => (
            <li key={`${r.date}-${r.time}-${idx}`} className="rounded-lg border border-border/60 bg-white/[0.02] px-3 py-2 text-heading">
              Review on {r.date} at {r.time} {r.audience ? `· Audience: ${r.audience}` : ""}
            </li>
          ))}
        </ul>
      </Card>

      {loggedImpacts.length > 0 && (
        <Card title="Logged impacts" subtitle="Quick notes you captured.">
          <ul className="space-y-2 text-sm text-muted">
            {loggedImpacts.map((i, idx) => (
              <li key={idx} className="rounded-lg border border-border px-3 py-2">
                <p className="text-heading">{i.title}</p>
                {i.amountUsd !== undefined && <p>Impact: ${i.amountUsd.toLocaleString()}</p>}
                {i.note && <p className="text-xs text-muted">{i.note}</p>}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {impactOpen && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-2xl bg-panel p-4 shadow-card">
            <h3 className="text-lg font-semibold text-heading">Log impact</h3>
            <p className="text-sm text-muted">Capture a quick note about realized value.</p>
            <div className="mt-3 space-y-2 text-sm">
              <input
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                placeholder="Impact title"
                value={impactForm.title}
                onChange={(e) => setImpactForm((f) => ({ ...f, title: e.target.value }))}
              />
              <input
                type="number"
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                placeholder="Amount (USD)"
                value={impactForm.amountUsd ?? ""}
                onChange={(e) => setImpactForm((f) => ({ ...f, amountUsd: Number(e.target.value) }))}
              />
              <textarea
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                placeholder="Notes"
                value={impactForm.note ?? ""}
                onChange={(e) => setImpactForm((f) => ({ ...f, note: e.target.value }))}
                rows={3}
              />
            </div>
            <div className="mt-3 flex justify-end gap-2">
              <Button variant="secondary" size="sm" onClick={() => setImpactOpen(false)}>
                Cancel
              </Button>
              <Button size="sm" onClick={submitImpact}>
                Save
              </Button>
            </div>
          </div>
        </div>
      )}

      {reviewOpen && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-2xl bg-panel p-4 shadow-card">
            <h3 className="text-lg font-semibold text-heading">Schedule review</h3>
            <p className="text-sm text-muted">Pick a date/time to align stakeholders.</p>
            <div className="mt-3 space-y-2 text-sm">
              <input
                type="date"
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={reviewForm.date}
                onChange={(e) => setReviewForm((f) => ({ ...f, date: e.target.value }))}
              />
              <input
                type="time"
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                value={reviewForm.time}
                onChange={(e) => setReviewForm((f) => ({ ...f, time: e.target.value }))}
              />
              <input
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
                placeholder="Audience (optional)"
                value={reviewForm.audience}
                onChange={(e) => setReviewForm((f) => ({ ...f, audience: e.target.value }))}
              />
            </div>
            <div className="mt-3 flex justify-end gap-2">
              <Button variant="secondary" size="sm" onClick={() => setReviewOpen(false)}>
                Cancel
              </Button>
              <Button size="sm" onClick={submitReview}>
                Save review
              </Button>
            </div>
          </div>
        </div>
      )}

      <GenaiPanel
        isOpen={genai.isOpen}
        onClose={genai.closePanel}
        question={genai.question}
        setQuestion={genai.setQuestion}
        ask={genai.ask}
        answer={genai.answer}
        loading={genai.loading}
        error={genai.error as unknown as Error | null}
        suggestions={genai.suggestions}
        scopeLabel="You’re asking about ROI and value."
      />
    </div>
  );
}
