"use client";

import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { UserRole } from "@/types/domain";

type RoleContextType = {
  role: UserRole;
  setRole: (role: UserRole) => void;
};

const UserRoleContext = createContext<RoleContextType | undefined>(undefined);
const STORAGE_KEY = "pulsecast-role";

export function UserRoleProvider({ children }: { children: React.ReactNode }) {
  const [role, setRoleState] = useState<UserRole>("PLANNER");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = window.localStorage.getItem(STORAGE_KEY) as UserRole | null;
      if (stored) {
        setRoleState(stored);
      }
    }
  }, []);

  const setRole = (next: UserRole) => {
    setRoleState(next);
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, next);
    }
  };

  const value = useMemo(() => ({ role, setRole }), [role]);

  return <UserRoleContext.Provider value={value}>{children}</UserRoleContext.Provider>;
}

export function useUserRole() {
  const ctx = useContext(UserRoleContext);
  if (!ctx) {
    throw new Error("useUserRole must be used within a UserRoleProvider");
  }
  return ctx;
}
