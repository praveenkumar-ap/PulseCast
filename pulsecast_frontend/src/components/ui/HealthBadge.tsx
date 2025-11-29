"use client";

import React, { useEffect, useState } from "react";
import { fetchHealth } from "@/api/healthApi";

type Status = "UNKNOWN" | "OK" | "DOWN";

function statusTone(status: Status) {
  switch (status) {
    case "OK":
      return { bg: "bg-emerald-500/15", dot: "bg-emerald-400", text: "text-emerald-200" };
    case "DOWN":
      return { bg: "bg-rose-500/15", dot: "bg-rose-400", text: "text-rose-200" };
    default:
      return { bg: "bg-amber-500/15", dot: "bg-amber-400", text: "text-amber-200" };
  }
}

export function HealthBadge() {
  const [status, setStatus] = useState<Status>("UNKNOWN");

  useEffect(() => {
    let mounted = true;
    fetchHealth()
      .then(() => {
        if (mounted) setStatus("OK");
      })
      .catch(() => {
        if (mounted) setStatus("DOWN");
      });
    return () => {
      mounted = false;
    };
  }, []);

  const tone = statusTone(status);

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${tone.bg} ${tone.text}`}
      title="Backend health"
    >
      <span className={`h-2.5 w-2.5 rounded-full ${tone.dot}`} />
      Backend: {status === "UNKNOWN" ? "Checking…" : status}
    </span>
  );
}
