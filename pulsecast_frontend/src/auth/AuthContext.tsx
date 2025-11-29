"use client";

import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { authApi } from "@/api/authApi";
import type { AuthUser, TokenResponse } from "@/types/domain";

type AuthContextType = {
  user: AuthUser | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (payload: { email: string; password: string; fullName?: string; tenantId?: string }) => Promise<void>;
  logout: () => Promise<void>;
  ready: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);
const STORAGE_KEY = "pulsecast-auth";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try {
        const parsed = JSON.parse(raw) as { user: AuthUser; accessToken: string };
        setUser(parsed.user);
        setAccessToken(parsed.accessToken);
      } catch {
        // ignore
      }
    }
    setHydrated(true);
  }, []);

  const persist = (nextUser: AuthUser | null, token: string | null) => {
    setUser(nextUser);
    setAccessToken(token);
    if (typeof window !== "undefined") {
      if (nextUser && token) {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ user: nextUser, accessToken: token }));
      } else {
        window.localStorage.removeItem(STORAGE_KEY);
      }
    }
  };

  const login = async (email: string, password: string) => {
    const resp = await authApi.login({ email, password });
    const maybeToken = (resp as TokenResponse).accessToken || null;
    const respUser = (resp as TokenResponse).user || (resp as unknown as AuthUser);
    persist(respUser, maybeToken);
  };

  const signup = async (payload: { email: string; password: string; fullName?: string; tenantId?: string }) => {
    const resp = await authApi.signup(payload);
    const maybeToken = (resp as TokenResponse).accessToken || null;
    const respUser = (resp as TokenResponse).user || (resp as unknown as AuthUser);
    persist(respUser, maybeToken);
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch {
      // ignore backend errors for logout
    }
    persist(null, null);
  };

  const value = useMemo(
    () => ({
      user,
      accessToken,
      isAuthenticated: Boolean(user), // until tokens are added, treat user presence as authenticated
      ready: hydrated,
      login,
      signup,
      logout,
    }),
    [user, accessToken, hydrated]
  );

  return <AuthContext.Provider value={value}>{hydrated ? children : null}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
