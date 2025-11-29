import React from "react";
import { cn } from "@/lib/cn";

type TableProps = {
  headers: string[];
  children: React.ReactNode;
  className?: string;
};

export function Table({ headers, children, className }: TableProps) {
  return (
    <div className={cn("overflow-hidden rounded-2xl border border-border/70 bg-panel/70", className)}>
      <table className="min-w-full divide-y divide-border/70 text-sm">
        <thead className="bg-white/5 text-left text-xs uppercase tracking-[0.14em] text-muted">
          <tr>
            {headers.map((h) => (
              <th key={h} className="px-4 py-3 font-semibold">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border/60 text-contrast">{children}</tbody>
      </table>
    </div>
  );
}

type TableRowProps = React.HTMLAttributes<HTMLTableRowElement>;

export function TableRow({ className, children, ...rest }: TableRowProps) {
  return (
    <tr
      className={cn(
        "transition hover:bg-white/5 focus-within:bg-white/5",
        className
      )}
      {...rest}
    >
      {children}
    </tr>
  );
}

type TableCellProps = {
  children: React.ReactNode;
  numeric?: boolean;
  className?: string;
};

export function TableCell({ children, numeric, className }: TableCellProps) {
  return (
    <td
      className={cn(
        "px-4 py-3 align-middle text-sm text-contrast",
        numeric ? "text-right tabular-nums" : "text-left",
        className
      )}
    >
      {children}
    </td>
  );
}
