"use client";

import React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ScenarioWizard } from "./ScenarioWizard";

export function NewScenarioPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const runId = searchParams?.get("runId") || undefined;

  return (
    <ScenarioWizard
      initialRunId={runId}
      onCreated={(id) => {
        router.push(`/scenarios/${id}`);
      }}
    />
  );
}
