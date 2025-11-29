import { post } from "./httpClient";
import type { AuthUser, TokenResponse } from "@/types/domain";

type SignupPayload = {
  email: string;
  password: string;
  fullName?: string;
  tenantId?: string;
};

type LoginPayload = {
  email: string;
  password: string;
};

type RawUser = {
  id?: string;
  user_id?: string;
  sub?: string;
  email?: string;
  fullName?: string;
  full_name?: string;
  role?: string;
  tenantId?: string;
  tenant_id?: string;
};

type RawTokenResponse = {
  access_token?: string;
  accessToken?: string;
  token_type?: string;
  tokenType?: string;
  user?: RawUser;
} & RawUser;

function normalizeUser(raw: RawUser): AuthUser {
  return {
    id: raw.id || raw.user_id || raw.sub || "",
    email: raw.email || "",
    fullName: raw.fullName || raw.full_name,
    role: raw.role,
    tenantId: raw.tenantId || raw.tenant_id,
  };
}

function normalizeTokenResponse(raw: RawTokenResponse): TokenResponse {
  if (raw.accessToken && raw.user) return raw as TokenResponse;
  return {
    accessToken: raw.access_token || raw.accessToken || "",
    tokenType: (raw.token_type || raw.tokenType || "bearer") as TokenResponse["tokenType"],
    user: raw.user ? normalizeUser(raw.user) : normalizeUser(raw),
  };
}

// Primary auth paths (no /api prefix; base path is empty for auth calls).
const AUTH_SIGNUP_PATH = "/auth/signup";
const AUTH_LOGIN_PATH = "/auth/login";
const AUTH_LOGOUT_PATH = "/auth/logout";

export async function signup(payload: SignupPayload): Promise<AuthUser | TokenResponse> {
  // Map frontend fields to backend expectations (full_name, organization)
  const body = {
    email: payload.email,
    password: payload.password,
    full_name: payload.fullName ?? payload.email,
    organization: payload.tenantId,
  };
  // Use base path (e.g., /api) so calls hit the main API service.
  const res = await post<typeof body, RawTokenResponse | RawUser>(AUTH_SIGNUP_PATH, body);
  if (res?.access_token || res?.accessToken) {
    return normalizeTokenResponse(res as RawTokenResponse);
  }
  if ((res as RawTokenResponse)?.user) return normalizeTokenResponse(res as RawTokenResponse);
  return normalizeUser(res as RawUser);
}

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const res = await post<LoginPayload, RawTokenResponse>(AUTH_LOGIN_PATH, payload);
  return normalizeTokenResponse(res);
}

export async function logout(): Promise<void> {
  await post(AUTH_LOGOUT_PATH, {}, { skipAuth: true });
}

export const authApi = {
  signup,
  login,
  logout,
};
