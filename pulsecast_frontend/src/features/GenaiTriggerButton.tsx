"use client";

import React from "react";
import { Button } from "@/components/ui/Button";

type Props = {
  onClick: () => void;
  label?: string;
};

export function GenaiTriggerButton({ onClick, label = "Ask AI about this" }: Props) {
  return (
    <Button size="sm" variant="secondary" onClick={onClick} className="inline-flex items-center gap-1">
      <span>✨</span>
      <span>{label}</span>
    </Button>
  );
}
