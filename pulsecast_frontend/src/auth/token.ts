export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem("pulsecast-auth");
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as { accessToken?: string };
    return parsed.accessToken || null;
  } catch {
    return null;
  }
}
