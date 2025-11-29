import { NextResponse } from "next/server";

const backendBase = process.env.PULSECAST_API_BASE_URL || "http://localhost:8003";
const backendBasePath = (process.env.PULSECAST_API_BASE_PATH || "").replace(/\/+$/, "");
const defaultUserId = process.env.NEXT_PUBLIC_API_USER_ID || "dev-user";
const defaultUserRole = process.env.NEXT_PUBLIC_API_USER_ROLE || "ADMIN";
const defaultTenantId = process.env.NEXT_PUBLIC_API_TENANT_ID;

async function proxy(req: Request) {
  const url = new URL(req.url);
  const path = url.pathname.replace(/^\/api\/backend/, "") || "/";
  const target = new URL(`${backendBasePath}${path}${url.search}`, backendBase);

  const headers: Record<string, string> = {};
  req.headers.forEach((value, key) => {
    if (!["host", "content-length"].includes(key.toLowerCase())) {
      headers[key] = value;
    }
  });
  if (!headers["x-user-id"]) headers["x-user-id"] = defaultUserId;
  if (!headers["x-user-role"]) headers["x-user-role"] = defaultUserRole;
  if (defaultTenantId && !headers["x-tenant-id"]) headers["x-tenant-id"] = defaultTenantId;

  const outgoingBody =
    req.method === "GET" || req.method === "HEAD" ? undefined : Buffer.from(await req.arrayBuffer());

  const init: RequestInit = {
    method: req.method,
    headers,
    body: outgoingBody,
  };

  const resp = await fetch(target.toString(), init);
  const respBody = await resp.arrayBuffer();
  return new NextResponse(respBody, {
    status: resp.status,
    headers: resp.headers,
  });
}

export async function GET(req: Request) {
  return proxy(req);
}

export async function POST(req: Request) {
  return proxy(req);
}

export async function PUT(req: Request) {
  return proxy(req);
}

export async function PATCH(req: Request) {
  return proxy(req);
}

export async function DELETE(req: Request) {
  return proxy(req);
}
