"use client";

import React from "react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/cn";
import type { GenaiAnswer } from "@/types/domain";

type GenaiPanelProps = {
  isOpen: boolean;
  onClose: () => void;
  question: string;
  setQuestion: (text: string) => void;
  ask: () => void;
  answer: GenaiAnswer | null;
  loading: boolean;
  error: Error | null;
  suggestions: string[];
  scopeLabel?: string;
};

export function GenaiPanel({
  isOpen,
  onClose,
  question,
  setQuestion,
  ask,
  answer,
  loading,
  error,
  suggestions,
  scopeLabel,
}: GenaiPanelProps) {
  return (
    <div
      className={cn(
        "fixed inset-y-0 right-0 z-40 w-full max-w-md transform border-l border-border/60 bg-panel/95 shadow-card backdrop-blur-xl transition-transform duration-200",
        isOpen ? "translate-x-0" : "translate-x-full"
      )}
    >
      <div className="flex items-start justify-between border-b border-border/60 px-4 py-4">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-primary">GenAI helper</p>
          <p className="text-base font-semibold text-heading">Ask AI about this</p>
          {scopeLabel && <p className="text-xs text-muted">{scopeLabel}</p>}
        </div>
        <button
          aria-label="Close"
          onClick={onClose}
          className="rounded-full p-2 text-muted hover:bg-white/10 hover:text-contrast"
        >
          ✕
        </button>
      </div>

      <div className="flex h-[calc(100%-64px)] flex-col space-y-4 overflow-y-auto px-4 py-3">
        <div>
          <p className="text-xs font-semibold text-muted">Suggested questions</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {suggestions.map((sug) => (
              <button
                key={sug}
                className="rounded-full border border-border/70 px-3 py-1 text-xs text-contrast transition hover:border-primary hover:text-primary"
                onClick={() => setQuestion(sug)}
              >
                {sug}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-xs text-muted">Your question</label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            placeholder="Ask in simple language, e.g. “Explain why demand increased for RSV this month.”"
            className="w-full rounded-xl border border-border bg-background px-3 py-2 text-sm text-contrast outline-none ring-primary/30 focus:ring-2"
          />
          <p className="text-xs text-muted">Ask about what changed, why, or what to watch out for.</p>
          <div className="flex justify-end">
            <Button size="sm" onClick={ask} disabled={loading}>
              {loading ? "Asking…" : "Ask AI"}
            </Button>
          </div>
        </div>

        <div className="flex-1">
          {loading && <p className="text-sm text-muted">Thinking… summarizing this for you.</p>}
          {error && (
            <div className="rounded-xl border border-red-400/40 bg-red-500/10 p-3 text-sm text-red-100">
              We couldn’t get an answer right now. Please try again.
            </div>
          )}
          {answer && !loading && (
            <div className="space-y-3">
              <p className="text-sm leading-relaxed text-contrast">{answer.answer}</p>
              {answer.highlights && answer.highlights.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-muted">Key points</p>
                  <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-contrast">
                    {answer.highlights.map((h, idx) => (
                      <li key={`${h.text}-${idx}`}>
                        {h.title ? <span className="font-semibold">{h.title}: </span> : null}
                        {h.text}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {answer.caveats && (
                <div className="rounded-lg border border-amber-300/50 bg-amber-500/10 p-3 text-sm text-amber-100">
                  <p className="font-semibold">Things to keep in mind</p>
                  <p className="text-xs leading-relaxed">{answer.caveats}</p>
                </div>
              )}
              {answer.sources && answer.sources.length > 0 && (
                <div className="text-xs text-muted">
                  Based on: {answer.sources.join(", ")}
                </div>
              )}
            </div>
          )}
          {!answer && !loading && !error && (
            <p className="text-sm text-muted">Ask a question to see an explanation in plain language.</p>
          )}
        </div>
      </div>
    </div>
  );
}
