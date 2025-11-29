"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/auth/AuthContext";

export function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);

  React.useEffect(() => {
    if (isAuthenticated) {
      router.replace("/home");
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await login(email, password);
      setSuccess("Signed in. Redirecting…");
      router.replace("/home");
    } catch (err) {
      const apiErr = err as { message?: string };
      const message = apiErr?.message || "Email or password is incorrect. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <Card className="w-full max-w-md rounded-2xl bg-panel">
        <h1 className="text-2xl font-semibold text-heading">Sign in to PulseCast</h1>
        <p className="mt-1 text-sm text-muted">
          Use your email and password to load your forecasts, scenarios, and alerts.
        </p>

        <form onSubmit={handleSubmit} className="mt-4 space-y-3">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Work email</span>
            <input
              className="rounded-lg border border-border bg-background px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@company.com"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Password</span>
            <input
              className="rounded-lg border border-border bg-background px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Password you’ll use to open PulseCast"
              minLength={8}
            />
          </label>

          {error && <p className="text-sm text-rose-300">{error}</p>}
          {success && <p className="text-sm text-emerald-300">{success}</p>}

          <Button type="submit" size="sm" className="w-full" disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </Button>
        </form>

        <p className="mt-3 text-sm text-muted">
          New here?{" "}
          <Link href="/signup" className="text-primary hover:text-primary-strong">
            Create a new account
          </Link>
        </p>
      </Card>
    </div>
  );
}
