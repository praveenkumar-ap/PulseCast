"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/auth/AuthContext";
import type { TokenResponse } from "@/types/domain";

export function SignupPage() {
  const { signup, isAuthenticated } = useAuth();
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [tenant, setTenant] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
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
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const resp = await signup({ email, password, fullName, tenantId: tenant || undefined });
      const hasToken = !!(resp as TokenResponse)?.accessToken;
      setSuccess("Account created. Signing you in…");
      router.replace(hasToken ? "/home" : "/login");
    } catch (err) {
      const apiErr = err as { details?: { code?: string }; message?: string };
      const code = apiErr.details?.code;
      if (code === "EMAIL_EXISTS") {
        setError("This email is already registered. Try signing in instead.");
      } else {
        setError(apiErr.message || "We couldn’t create your account. Please try again or contact support.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <Card className="w-full max-w-md rounded-2xl bg-panel">
        <h1 className="text-2xl font-semibold text-heading">Create your PulseCast account</h1>
        <p className="mt-1 text-sm text-muted">Use a work email if possible. We’ll save your settings and scenarios.</p>

        <form onSubmit={handleSubmit} className="mt-4 space-y-3">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Full name</span>
            <input
              className="rounded-lg border border-border bg-background px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Your name"
            />
          </label>
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
            <span className="text-muted">Organization (optional)</span>
            <input
              className="rounded-lg border border-border bg-background px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              value={tenant}
              onChange={(e) => setTenant(e.target.value)}
              placeholder="Team or tenant name"
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
              minLength={8}
              placeholder="At least 8 characters"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted">Confirm password</span>
            <input
              className="rounded-lg border border-border bg-background px-3 py-2 text-contrast outline-none ring-primary/30 focus:ring-2"
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              minLength={8}
              placeholder="Re-enter password"
            />
          </label>

          {error && <p className="text-sm text-rose-300">{error}</p>}
          {success && <p className="text-sm text-emerald-300">{success}</p>}

          <Button type="submit" size="sm" className="w-full" disabled={loading}>
            {loading ? "Creating account…" : "Create account"}
          </Button>
        </form>

        <p className="mt-3 text-sm text-muted">
          Already have an account?{" "}
          <Link href="/login" className="text-primary hover:text-primary-strong">
            Sign in
          </Link>
        </p>
      </Card>
    </div>
  );
}
