import React from "react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/cn";

type PageHeaderProps = {
  title: string;
  eyebrow?: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
};

export function PageHeader({
  title,
  eyebrow,
  description,
  actions,
  className,
}: PageHeaderProps) {
  return (
    <div className={cn("flex flex-col gap-3 sm:flex-row sm:items-center", className)}>
      <div className="flex-1">
        {eyebrow && (
          <span className="inline-flex items-center rounded-full bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
            {eyebrow}
          </span>
        )}
        <div className="mt-2">
          <h1 className="text-2xl font-semibold text-heading sm:text-3xl">
            {title}
          </h1>
          {description && (
            <p className="mt-1 text-sm text-muted sm:text-base">
              {description}
            </p>
          )}
        </div>
      </div>
      {actions ?? (
        <div className="flex gap-2">
          <Button variant="secondary" size="sm">
            Export
          </Button>
          <Button size="sm">Create</Button>
        </div>
      )}
    </div>
  );
}
