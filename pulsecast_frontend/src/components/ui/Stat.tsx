import React from "react";
import { cn } from "@/lib/cn";

type StatProps = {
  label: string;
  value: string;
  delta?: string;
  tone?: "positive" | "negative" | "neutral";
  className?: string;
};

export function Stat({
  label,
  value,
  delta,
  tone = "neutral",
  className,
}: StatProps) {
  const toneColor =
    tone === "positive"
      ? "text-emerald-400"
      : tone === "negative"
      ? "text-rose-400"
      : "text-muted";

  return (
    <div
      className={cn(
        "rounded-2xl border border-border/80 bg-white/[0.02] px-4 py-3 shadow-inset",
        className
      )}
    >
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted">
        {label}
      </p>
      <div className="mt-1 flex items-baseline gap-2">
        <span className="text-2xl font-semibold text-heading">{value}</span>
        {delta && <span className={cn("text-sm font-medium", toneColor)}>{delta}</span>}
      </div>
    </div>
  );
}
