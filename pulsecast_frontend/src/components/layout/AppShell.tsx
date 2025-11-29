"use client";

import React from "react";
import { navItemsForRole } from "@/lib/navigation";
import { useUserRole, UserRoleProvider } from "@/lib/UserRoleContext";
import { TopNav } from "./TopNav";
import { Sidebar } from "./Sidebar";
import { RequireAuth } from "@/auth/RequireAuth";

type AppShellProps = {
  children: React.ReactNode;
};

function AppShellInner({ children }: AppShellProps) {
  const { role } = useUserRole();
  const items = navItemsForRole(role);

  return (
    <RequireAuth>
      <div className="min-h-screen bg-background text-contrast">
        <TopNav />
        <div className="flex">
          <Sidebar items={items} />
          <main className="flex-1 px-5 py-6 sm:px-8 lg:px-10 lg:py-8">
            <div className="mx-auto max-w-6xl space-y-6">{children}</div>
          </main>
        </div>
      </div>
    </RequireAuth>
  );
}

export function AppShell({ children }: AppShellProps) {
  return (
    <UserRoleProvider>
      <AppShellInner>{children}</AppShellInner>
    </UserRoleProvider>
  );
}
