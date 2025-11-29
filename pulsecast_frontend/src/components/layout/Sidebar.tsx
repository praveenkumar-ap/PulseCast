"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { navItems, type NavItem } from "@/lib/navigation";
import { cn } from "@/lib/cn";

type SidebarProps = {
  items?: NavItem[];
};

export function Sidebar({ items = navItems }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside className="hidden w-64 shrink-0 border-r border-border/70 bg-panel/70 px-3 py-6 backdrop-blur-xl md:block">
      <p className="px-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted">
        Workflow
      </p>
      <nav className="mt-3 space-y-2">
        {items.map((item) => {
          const isActive =
            item.path === "/"
              ? pathname === "/"
              : pathname === item.path || pathname.startsWith(`${item.path}/`);

          return (
            <Link
              key={item.path}
              href={item.path}
              className={cn(
                "group block rounded-xl border border-transparent px-3 py-3 transition-all duration-150",
                "hover:border-border hover:bg-white/5",
                isActive &&
                  "border-primary/80 bg-primary/10 text-heading shadow-inset"
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="text-sm font-semibold">{item.label}</span>
                {isActive && (
                  <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                )}
              </div>
              {item.description && (
                <p className="mt-1 text-xs text-muted">{item.description}</p>
              )}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
