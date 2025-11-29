"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/Button";
import { HealthBadge } from "@/components/ui/HealthBadge";
import { useUserRole } from "@/lib/UserRoleContext";
import { useAuth } from "@/auth/AuthContext";

export function TopNav() {
  const { role, setRole } = useUserRole();
  const [shared, setShared] = useState<string | null>(null);
  const [shareMenuOpen, setShareMenuOpen] = useState(false);
  const { user, logout } = useAuth();
  const [showMenu, setShowMenu] = useState(false);

  const shareUrl = typeof window !== "undefined" ? window.location.href : "";
  const shareSubject = encodeURIComponent("PulseCast link");
  const shareBody = encodeURIComponent(`Here’s the link I’m looking at: ${shareUrl}`);

  const openMail = (provider: "gmail" | "outlook" | "zoho") => {
    let href = "";
    if (provider === "gmail") {
      href = `https://mail.google.com/mail/?view=cm&fs=1&su=${shareSubject}&body=${shareBody}`;
    } else if (provider === "outlook") {
      href = `https://outlook.office.com/mail/deeplink/compose?subject=${shareSubject}&body=${shareBody}`;
    } else {
      href = `https://mail.zoho.com/zm/#compose?subject=${shareSubject}&body=${shareBody}`;
    }
    window.open(href, "_blank", "noreferrer");
    setShared("Opening email draft…");
    setShareMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-20 h-[var(--pc-nav-height)] border-b border-border/70 bg-background/70 backdrop-blur-xl">
      <div className="mx-auto flex h-full max-w-6xl items-center justify-between px-5 sm:px-8 lg:px-10">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-primary-strong text-heading shadow-card">
            <span className="text-sm font-semibold">PC</span>
          </div>
          <div className="leading-tight">
            <p className="text-sm uppercase tracking-[0.24em] text-primary">
              PulseCast
            </p>
            <p className="text-base font-semibold text-heading">
              Signal Intelligence Console
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden flex-col text-right text-xs text-muted sm:flex">
            <span className="font-semibold text-contrast">Viewing as</span>
            <select
              className="mt-1 rounded-lg border border-border bg-panel px-2 py-1 text-xs text-contrast outline-none ring-primary/30 focus:ring-2"
              value={role}
              onChange={(e) => setRole(e.target.value as typeof role)}
            >
              <option value="PLANNER">Planner</option>
              <option value="APPROVER">Approver</option>
              <option value="DATA_SCIENTIST">Data Scientist</option>
            </select>
          </div>
          <HealthBadge />
          <div className="relative">
            <Button variant="secondary" size="sm" onClick={() => setShareMenuOpen((v) => !v)}>
              Share
            </Button>
            {shareMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 rounded-xl border border-border bg-panel p-2 text-sm shadow-card">
                <p className="px-2 text-xs text-muted">Send via</p>
                <button
                  className="w-full rounded-lg px-3 py-2 text-left hover:bg-white/10"
                  onClick={() => openMail("gmail")}
                >
                  Gmail
                </button>
                <button
                  className="w-full rounded-lg px-3 py-2 text-left hover:bg-white/10"
                  onClick={() => openMail("outlook")}
                >
                  Outlook
                </button>
                <button
                  className="w-full rounded-lg px-3 py-2 text-left hover:bg-white/10"
                  onClick={() => openMail("zoho")}
                >
                  Zoho Mail
                </button>
              </div>
            )}
          </div>
          <div className="relative">
            <Button variant="secondary" size="sm" onClick={() => setShowMenu((v) => !v)}>
              {user?.email || "Account"}
            </Button>
            {showMenu && (
              <div className="absolute right-0 mt-2 w-40 rounded-xl border border-border bg-panel p-2 text-sm shadow-card">
                <p className="px-2 text-xs text-muted">{user?.email}</p>
                <button
                  className="w-full rounded-lg px-3 py-2 text-left hover:bg-white/10"
                  onClick={async () => {
                    await logout();
                    window.location.href = "/login";
                  }}
                >
                  Sign out
                </button>
              </div>
            )}
          </div>
          <Button size="sm">New scenario</Button>
        </div>
      </div>
      {shared && (
        <div className="mx-auto max-w-6xl px-5 sm:px-8 lg:px-10">
          <p className="mt-1 text-xs text-primary">{shared}</p>
        </div>
      )}
    </header>
  );
}
