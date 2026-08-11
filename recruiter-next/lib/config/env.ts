import "server-only";

/**
 * Environment Configuration
 *
 * Ports recruiter/src/lib/config/env.ts, with two changes:
 *  - The deprecated getApiBasePath() dead path is dropped (MIGRATION.md debt #7).
 *  - API_BASE_URL is server-only. Nothing in the browser calls Django directly,
 *    so it loses the PUBLIC_/NEXT_PUBLIC_ prefix.
 */

function required(name: string, value: string | undefined): string {
  if (!value) {
    throw new Error(
      `Missing required environment variable: ${name}. Copy .env.example to .env.`,
    );
  }
  return value;
}

/** Django REST API root, e.g. http://localhost:8000/api/v1 */
export const API_BASE_URL = required("API_BASE_URL", process.env.API_BASE_URL);

/** This app's own public origin, used for OAuth callback URLs. */
export const SITE_URL = required(
  "NEXT_PUBLIC_SITE_URL",
  process.env.NEXT_PUBLIC_SITE_URL,
);

export const isProduction = process.env.NODE_ENV === "production";
export const isDevelopment = process.env.NODE_ENV === "development";

/**
 * Build a fully-qualified API URL.
 * Every Django call goes through here — no hardcoded hosts (MIGRATION.md debt #1).
 */
export function apiUrl(endpoint: string): string {
  const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  return `${API_BASE_URL.replace(/\/$/, "")}${path}`;
}
