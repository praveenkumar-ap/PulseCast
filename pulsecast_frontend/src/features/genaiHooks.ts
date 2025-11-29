import { useCallback, useMemo, useState } from "react";
import { genaiApi } from "@/api/genaiApi";
import type { GenaiAnswer, GenaiQuestionContext } from "@/types/domain";
import type { ApiError } from "@/api/httpClient";

const defaultSuggestions: Record<GenaiQuestionContext["scope"], string[]> = {
  FORECAST_RUN: [
    "Explain the key drivers behind this forecast.",
    "What changed versus the previous run?",
    "Which test kits look most uncertain and why?",
  ],
  SCENARIO: [
    "Explain this scenario to a non-technical stakeholder.",
    "What are the main assumptions and risks here?",
    "What should I watch out for if we follow this scenario?",
  ],
  VALUE_OVERVIEW: [
    "Explain where most of the value is coming from.",
    "Which drivers have the biggest impact on value right now?",
    "How is value trending versus earlier runs?",
  ],
  FREEFORM: ["Summarize this in simple language."],
};

export function useGenaiHelper(initialContext: GenaiQuestionContext, initialSuggestedQuestion?: string) {
  const [isOpen, setIsOpen] = useState(false);
  const [context, setContext] = useState<GenaiQuestionContext>(initialContext);
  const [question, setQuestion] = useState<string>(initialSuggestedQuestion || "");
  const [answer, setAnswer] = useState<GenaiAnswer | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const suggestions = useMemo(() => defaultSuggestions[context.scope] || defaultSuggestions.FREEFORM, [context.scope]);

  const openPanel = useCallback(
    (contextOverride?: GenaiQuestionContext, suggestedQuestion?: string) => {
      if (contextOverride) {
        setContext(contextOverride);
      }
      setQuestion(
        suggestedQuestion ||
          initialSuggestedQuestion ||
          (defaultSuggestions[contextOverride?.scope ?? context.scope] || defaultSuggestions.FREEFORM)[0]
      );
      setIsOpen(true);
    },
    [context.scope, initialSuggestedQuestion]
  );

  const closePanel = useCallback(() => {
    setIsOpen(false);
    setError(null);
  }, []);

  const ask = useCallback(async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await genaiApi.askGenai({ question, context });
      setAnswer(resp);
    } catch (err) {
      setError(err as ApiError);
    } finally {
      setLoading(false);
    }
  }, [context, question]);

  return {
    isOpen,
    openPanel,
    closePanel,
    context,
    question,
    setQuestion,
    ask,
    answer,
    loading,
    error,
    suggestions,
  };
}
