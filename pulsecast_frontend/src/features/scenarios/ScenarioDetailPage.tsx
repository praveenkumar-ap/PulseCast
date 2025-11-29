"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { ScenarioLedger } from "./ScenarioLedger";
import { ScenarioForm } from "./ScenarioForm";
import { useScenarioDetail } from "./hooks";
import { useGenaiHelper } from "@/features/genaiHooks";
import { GenaiPanel } from "@/features/GenaiPanel";
import { GenaiTriggerButton } from "@/features/GenaiTriggerButton";

export function ScenarioDetailPage() {
  const params = useParams();
  const router = useRouter();
  const scenarioId = Array.isArray(params?.scenarioId)
    ? params?.scenarioId[0]
    : (params?.scenarioId as string | undefined);

  const { detail, ledger, loading, error, reload, appendLedger } = useScenarioDetail(
    scenarioId ?? ""
  );

  const [editing, setEditing] = useState(false);
  const genai = useGenaiHelper(
    { scope: "SCENARIO", scenarioId: scenarioId ?? "", scenarioName: detail?.name },
    "Explain this scenario, its assumptions, and main risks in simple terms."
  );
  const assumptionSummary = useMemo(() => {
    if (!detail) return null;
    return {
      upliftPercent: detail.upliftPercent,
      baseRunId: detail.baseRunId,
      horizon: detail.assumptions?.horizon,
      scope: detail.assumptions?.scope,
    };
  }, [detail]);

  if (!scenarioId) {
    return <p className="text-sm text-muted">No scenario id provided.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Button variant="secondary" size="sm" onClick={() => router.push("/scenarios")}>
          ← Back to scenarios
        </Button>
        <p className="text-sm text-muted">Scenario ID: {scenarioId}</p>
      </div>

      {loading && <p className="text-sm text-muted">Loading scenario…</p>}
      {error && (
        <div className="flex items-center gap-2 text-sm text-rose-200">
          <span>Failed to load scenario.</span>
          <Button size="sm" variant="secondary" onClick={reload}>
            Retry
          </Button>
        </div>
      )}

      {detail && (
        <>
          <Card
            title={detail.name}
            subtitle={`Status: ${detail.status}`}
            actions={
              <div className="flex gap-2">
                <Link
                  href={`/forecasts/${detail.baseRunId ?? ""}`}
                  className="text-sm font-semibold text-primary"
                >
                  View linked run →
                </Link>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => router.push(`/optimizer?runId=${detail.baseRunId ?? ""}&scenarioId=${detail.scenarioId ?? scenarioId}`)}
                >
                  View policies for this scenario
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => router.push(`/value?runId=${detail.baseRunId ?? ""}&scenarioId=${detail.scenarioId ?? scenarioId}`)}
                >
                  View value impact
                </Button>
                <Button size="sm" variant="secondary" onClick={() => setEditing((e) => !e)}>
                  {editing ? "Cancel edit" : "Edit"}
                </Button>
                <GenaiTriggerButton
                  onClick={() =>
                    genai.openPanel(
                      { scope: "SCENARIO", scenarioId: scenarioId ?? "", scenarioName: detail.name },
                      "Explain this scenario, its assumptions, and main risks in simple terms."
                    )
                  }
                />
              </div>
            }
          >
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-muted">Base run</p>
                <p className="text-base font-semibold text-heading">{detail.baseRunId ?? "—"}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-muted">Created by</p>
                <p className="text-base font-semibold text-heading">{detail.createdBy}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-muted">Created</p>
                <p className="text-base font-semibold text-heading">
                  {new Date(detail.createdAt).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-muted">Updated</p>
                <p className="text-base font-semibold text-heading">
                  {detail.updatedAt ? new Date(detail.updatedAt).toLocaleString() : "—"}
                </p>
              </div>
              <div className="sm:col-span-2">
                <p className="text-xs uppercase tracking-[0.18em] text-muted">Description</p>
                <p className="text-base text-contrast">
                  {detail.description || "No description provided."}
                </p>
              </div>
            </div>
          </Card>

          <Card title="Assumptions">
            {assumptionSummary ? (
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] text-muted">Uplift %</p>
                  <p className="text-base font-semibold text-heading">
                    {assumptionSummary.upliftPercent ?? "—"}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] text-muted">Base run</p>
                  <p className="text-base font-semibold text-heading">
                    {assumptionSummary.baseRunId ?? "—"}
                  </p>
                </div>
                {assumptionSummary.horizon && (
                  <div className="sm:col-span-2">
                    <p className="text-xs uppercase tracking-[0.18em] text-muted">Horizon</p>
                    <p className="text-base font-semibold text-heading">
                      {assumptionSummary.horizon.fromMonth ?? "?"} →{" "}
                      {assumptionSummary.horizon.toMonth ?? "?"}
                    </p>
                  </div>
                )}
                {assumptionSummary.scope && (
                  <div className="sm:col-span-2">
                    <p className="text-xs uppercase tracking-[0.18em] text-muted">Scope</p>
                    <p className="text-base font-semibold text-heading">
                      {assumptionSummary.scope.type === "ALL"
                        ? "All SKUs"
                        : `SKUs: ${assumptionSummary.scope.skuIds?.join(", ") ?? "—"}`}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-muted">No assumptions captured.</p>
            )}
          </Card>

          {editing && (
            <ScenarioForm
              mode="edit"
              initialValues={{
                name: detail.name,
                description: detail.description || "",
                baseRunId: detail.baseRunId || "",
                upliftPercent: detail.upliftPercent || 0,
                fromMonth: detail.results[0]?.yearMonth ?? "",
                toMonth: detail.results[detail.results.length - 1]?.yearMonth ?? "",
              }}
              onSubmit={async () => {
                // No direct update endpoint; log edit in ledger.
                await appendLedger("EDIT", "Edited scenario metadata");
                setEditing(false);
                reload();
              }}
            />
          )}

          <Card
            title="Ledger"
            subtitle="Audit trail of scenario actions."
            actions={
              <div className="flex gap-2">
                <Button size="sm" variant="secondary" onClick={() => appendLedger("COMMENT", "Reviewed")}>
                  Add note
                </Button>
                <Button size="sm" onClick={() => appendLedger("APPROVE", "Approved scenario")}>
                  Approve
                </Button>
                <Button size="sm" variant="secondary" onClick={() => appendLedger("REJECT", "Rejected scenario")}>
                  Reject
                </Button>
              </div>
            }
          >
            <ScenarioLedger entries={ledger} />
          </Card>
        </>
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
        scopeLabel="You’re asking about this scenario."
      />
    </div>
  );
}
