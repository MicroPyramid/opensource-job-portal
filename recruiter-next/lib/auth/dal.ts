import "server-only";
import { cache } from "react";
import { redirect } from "next/navigation";
import { api, UnauthorizedError } from "@/lib/api/client";
import { hasAuthCookies } from "@/lib/auth/session";
import type { User } from "@/lib/types";

/**
 * Data Access Layer — the authoritative auth check.
 *
 * `proxy.ts` does a cheap cookie-presence check to keep logged-out traffic off
 * dashboard routes, but the Next docs are explicit that proxy is for optimistic
 * checks, not authorization. This module is what actually proves a session, by
 * asking Django who the caller is.
 *
 * The SvelteKit app checked auth in three places with slightly different
 * behaviour (hooks guard, +layout.server.ts, and per-route in +page.server.ts).
 * This replaces all three (MIGRATION.md debt #3).
 */

/**
 * Resolve the current recruiter, or null if unauthenticated.
 *
 * Wrapped in React `cache()` so the layout, the page and any Server Action in
 * the same request share one call to /recruiter/auth/me/ instead of N.
 */
export const getCurrentUser = cache(async (): Promise<User | null> => {
  if (!(await hasAuthCookies())) return null;

  try {
    return await api.get<User>("/recruiter/auth/me/");
  } catch (error) {
    // Expired or invalid token — treat as logged out rather than a 500.
    if (error instanceof UnauthorizedError) return null;
    throw error;
  }
});

/**
 * Require an authenticated recruiter, or redirect to login.
 *
 * Call this at the top of every Server Action. Actions are reachable by direct
 * POST, not only through the app's own UI, so the proxy having run is not a
 * guarantee that this particular request is authorized.
 *
 * @param redirectTo path to return to after login
 */
export async function requireAuth(redirectTo?: string): Promise<User> {
  const user = await getCurrentUser();

  if (!user) {
    // Via /session-expired/ rather than straight to /login/: the request may
    // still carry a cookie that Django has rejected, and proxy.ts would bounce
    // any credential-bearing request back to /dashboard/, looping forever. That
    // handler clears the cookies first. See app/session-expired/route.ts.
    redirect(
      redirectTo
        ? `/session-expired/?redirect=${encodeURIComponent(redirectTo)}`
        : "/session-expired/",
    );
  }

  return user;
}

/**
 * Require a recruiter who belongs to a company.
 *
 * The Company, Team and Microsite sections are hidden from the sidebar for
 * independent recruiters; this is the server-side counterpart of that check.
 */
export async function requireCompany(redirectTo?: string): Promise<User> {
  const user = await requireAuth(redirectTo);
  if (!user.company) redirect("/dashboard/");
  return user;
}
