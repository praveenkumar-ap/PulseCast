import { buildApiUrl, runtimeEnv } from "@/config/env";
import { getAuthToken } from "@/auth/token";

export type ApiError = {
  status: number;
  message: string;
  details?: unknown;
};

async function parseJsonSafe(response: Response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

function buildError(status: number, fallbackMessage: string, details?: unknown): ApiError {
  const maybeObject =
    details && typeof details === "object" ? (details as Record<string, unknown>) : null;

  const detailMsg =
    (maybeObject?.detail as string | undefined) ||
    (maybeObject?.message as string | undefined);

  return {
    status,
    message: detailMsg || fallbackMessage,
    details,
  };
}

async function handleResponse<T>(response: Response): Promise<T> {
  const data = await parseJsonSafe(response);
  if (response.ok) {
    return data as T;
  }

  const error = buildError(
    response.status,
    `Request failed with status ${response.status}`,
    data
  );

  if (process.env.NODE_ENV !== "production") {
    console.error("[API]", error);
  }

  throw error;
}

type RequestInitExtra = RequestInit & { skipAuth?: boolean; includeBasePath?: boolean };

async function request<T>(path: string, init?: RequestInitExtra): Promise<T> {
  const url = buildApiUrl(path, { includeBasePath: init?.includeBasePath });
  const authHeaders: Record<string, string> = {};
  if (runtimeEnv.userId) authHeaders["X-User-Id"] = runtimeEnv.userId;
  if (runtimeEnv.userRole) authHeaders["X-User-Role"] = runtimeEnv.userRole;
  if (runtimeEnv.tenantId) authHeaders["X-Tenant-Id"] = runtimeEnv.tenantId;
  const bearer = getAuthToken();
  if (bearer && !init?.skipAuth) {
    authHeaders["Authorization"] = `Bearer ${bearer}`;
  }
  const response = await fetch(url, {
    ...init,
    headers: {
      Accept: "application/json",
      ...authHeaders,
      ...(init?.headers || {}),
    },
  });

  return handleResponse<T>(response);
}

export async function get<T>(path: string, init?: RequestInitExtra) {
  return request<T>(path, { ...init, method: "GET" });
}

export async function post<TBody extends object | undefined, TResponse>(
  path: string,
  body?: TBody,
  init?: RequestInitExtra
) {
  return request<TResponse>(path, {
    ...init,
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(init?.headers || {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
}

export const httpClient = { get, post };
