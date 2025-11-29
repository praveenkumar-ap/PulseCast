import React from "react";
import { cn } from "@/lib/cn";

type CardProps = {
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
  className?: string;
  children: React.ReactNode;
};

export function Card({
  title,
  subtitle,
  actions,
  className,
  children,
}: CardProps) {
  return (
    <section
      className={cn(
        "card-surface p-5 sm:p-6 border border-border shadow-card",
        className
      )}
    >
      {(title || subtitle || actions) && (
        <header className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            {title && (
              <h3 className="text-lg font-semibold leading-tight text-heading">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="mt-1 text-sm text-muted">{subtitle}</p>
            )}
          </div>
          {actions && <div className="flex gap-2">{actions}</div>}
        </header>
      )}
      <div>{children}</div>
    </section>
  );
}
