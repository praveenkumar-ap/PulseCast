type EnvConfig = {
  apiBaseUrl?: string;
  apiBasePath: string;
  healthBaseUrl?: string;
  healthPath: string;
  userId?: string;
  userRole?: string;
  tenantId?: string;
};

const rawBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
const rawBasePath = process.env.NEXT_PUBLIC_API_BASE_PATH?.trim() ?? "/api";
const rawHealthBaseUrl = process.env.NEXT_PUBLIC_HEALTH_BASE_URL?.trim();
const rawHealthPath = process.env.NEXT_PUBLIC_HEALTH_PATH?.trim() || "/health";
const rawUserId = process.env.NEXT_PUBLIC_API_USER_ID?.trim() || "dev-user";
const rawUserRole = process.env.NEXT_PUBLIC_API_USER_ROLE?.trim() || "ADMIN";
const rawTenantId = process.env.NEXT_PUBLIC_API_TENANT_ID?.trim();

function normalizePath(path: string) {
  if (!path.startsWith("/")) return `/${path}`;
  return path.replace(/\/+$/, "") || "/";
}

function normalizeBaseUrl(url?: string) {
  if (!url) return undefined;
  return url.replace(/\/+$/, "");
}

function normalizeBasePath(path?: string) {
  if (!path || path === "/") return "";
  return normalizePath(path);
}

const env: EnvConfig = {
  apiBaseUrl: normalizeBaseUrl(rawBaseUrl),
  apiBasePath: normalizeBasePath(rawBasePath),
  healthBaseUrl: normalizeBaseUrl(rawHealthBaseUrl) ?? normalizeBaseUrl(rawBaseUrl),
  healthPath: normalizePath(rawHealthPath),
  userId: rawUserId,
  userRole: rawUserRole,
  tenantId: rawTenantId,
};

type BuildOptions = {
  includeBasePath?: boolean;
};

export function buildApiUrl(path: string, options?: BuildOptions) {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }

  const normalizedPath = normalizePath(path);
  const useBasePath = options?.includeBasePath ?? true;

  const basePrefix = env.apiBaseUrl ?? "";
  const pathPrefix = useBasePath ? env.apiBasePath : "";
  const prefix = `${basePrefix}${pathPrefix}`;

  if (prefix.endsWith("/") && normalizedPath.startsWith("/")) {
    return `${prefix}${normalizedPath.slice(1)}`;
  }

  return `${prefix}${normalizedPath}`;
}

export function buildHealthUrl() {
  const base = env.healthBaseUrl || "";
  return `${base}${env.healthPath}`;
}

export const runtimeEnv = env;
