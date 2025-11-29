import { get } from "./httpClient";
import { buildHealthUrl } from "@/config/env";

export type HealthStatus = {
  status: string;
  env?: string;
  version?: string;
};

export async function fetchHealth() {
  const url = buildHealthUrl();
  return get<HealthStatus>(url, { includeBasePath: false });
}
