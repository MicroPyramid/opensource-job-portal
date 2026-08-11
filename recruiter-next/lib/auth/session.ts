import "server-only";
import { cookies } from "next/headers";
import {
  ACCESS_TOKEN,
  REFRESH_TOKEN,
  accessCookieOptions,
  refreshCookieOptions,
} from "@/lib/auth/cookie-config";

/**
 * Auth cookie access for Server Components, Server Actions and Route Handlers.
 *
 * Django issues JWTs in the login response body; we hold them in HttpOnly cookies
 * so the browser never sees a token. Every cookie write in the app goes through
 * here — the original set them inline in four places (MIGRATION.md debt #2).
 *
 * IMPORTANT: `.set`/`.delete` only work in Server Actions and Route Handlers.
 * Setting cookies during Server Component render is not supported by Next.js, so
 * mid-render token renewal happens in `proxy.ts` instead.
 */

export { ACCESS_TOKEN, REFRESH_TOKEN } from "@/lib/auth/cookie-config";

/** Read the current access token, if any. Safe in Server Components. */
export async function getAccessToken(): Promise<string | undefined> {
  return (await cookies()).get(ACCESS_TOKEN)?.value;
}

/** Read the current refresh token, if any. Safe in Server Components. */
export async function getRefreshToken(): Promise<string | undefined> {
  return (await cookies()).get(REFRESH_TOKEN)?.value;
}

/**
 * True if the request carries either token. This is a presence check only — it
 * says nothing about whether the token is valid. Use `requireAuth()` for that.
 */
export async function hasAuthCookies(): Promise<boolean> {
  const store = await cookies();
  return store.has(ACCESS_TOKEN) || store.has(REFRESH_TOKEN);
}

/** Server Actions / Route Handlers only. */
export async function setAuthCookies(access: string, refresh: string) {
  const store = await cookies();
  store.set(ACCESS_TOKEN, access, accessCookieOptions);
  store.set(REFRESH_TOKEN, refresh, refreshCookieOptions);
}

/** Server Actions / Route Handlers only. */
export async function clearAuthCookies() {
  const store = await cookies();
  store.delete(ACCESS_TOKEN);
  store.delete(REFRESH_TOKEN);
}
