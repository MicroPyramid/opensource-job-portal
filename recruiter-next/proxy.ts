import { NextResponse, type NextRequest } from "next/server";
import {
  ACCESS_TOKEN,
  REFRESH_TOKEN,
  accessCookieOptions,
  refreshCookieOptions,
} from "@/lib/auth/cookie-config";

/**
 * Proxy — Next 16's rename of Middleware. Runs before every matched request.
 *
 * Replaces the `authGuard` in recruiter/src/hooks.server.ts, and does one thing
 * the SvelteKit app could not: silently renews an expired access token.
 *
 * Why here? Cookies cannot be written during Server Component render, so a page
 * that discovers its 15-minute access token just expired has no way to store a
 * fresh one. Proxy can set response cookies, so renewal happens before the page
 * ever runs.
 *
 * This is deliberately NOT the authorization check — that's `requireAuth()` in
 * lib/auth/dal.ts. Everything below is a cookie-presence test.
 */

/** Mirrors the publicRoutes list in the original hooks.server.ts. */
const PUBLIC_ROUTES = [
  "/login",
  "/signup",
  "/forgot-password",
  "/reset-password",
  "/verify-email",
  "/onboarding",
];

const isPublicRoute = (pathname: string) =>
  PUBLIC_ROUTES.some((route) => pathname.startsWith(route));

/**
 * Exchange a refresh token for a new access token.
 *
 * Note: /api/v1/auth/token/refresh/ (CookieTokenRefreshView) returns only
 * `{"message": "..."}` in the body and puts the new tokens in Set-Cookie headers
 * scoped to the Django host. Those cookies are useless to us — this app serves a
 * different origin in production — so we read the values back out of the header
 * and re-issue them as our own. See MIGRATION.md § Token refresh.
 */
async function refreshTokens(
  refreshToken: string,
): Promise<{ access: string; refresh: string } | null> {
  const base = process.env.API_BASE_URL;
  if (!base) return null;

  try {
    const response = await fetch(
      `${base.replace(/\/$/, "")}/auth/token/refresh/`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh: refreshToken }),
      },
    );

    if (!response.ok) return null;

    const setCookies = response.headers.getSetCookie();
    const read = (name: string) =>
      setCookies
        .find((c) => c.startsWith(`${name}=`))
        ?.split(";")[0]
        ?.slice(name.length + 1);

    const access = read(ACCESS_TOKEN);
    if (!access) return null;

    return { access, refresh: read(REFRESH_TOKEN) ?? refreshToken };
  } catch {
    // Django unreachable — fall through to the logged-out path rather than
    // erroring the whole request.
    return null;
  }
}

export async function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  let access = request.cookies.get(ACCESS_TOKEN)?.value;
  const refresh = request.cookies.get(REFRESH_TOKEN)?.value;
  let renewed: { access: string; refresh: string } | null = null;

  // Access token expired but the 7-day refresh token is still good — renew now
  // so the page render downstream sees a valid token.
  if (!access && refresh) {
    renewed = await refreshTokens(refresh);
    if (renewed) {
      access = renewed.access;
      request.cookies.set(ACCESS_TOKEN, renewed.access);
      request.cookies.set(REFRESH_TOKEN, renewed.refresh);
    }
  }

  const isAuthed = Boolean(access ?? refresh);

  /** Carry renewed cookies onto whatever response we end up returning. */
  const withRenewedCookies = (response: NextResponse) => {
    if (renewed) {
      response.cookies.set(ACCESS_TOKEN, renewed.access, accessCookieOptions);
      // Must persist the ROTATED refresh token: SIMPLE_JWT has
      // ROTATE_REFRESH_TOKENS + BLACKLIST_AFTER_ROTATION, so the token we just
      // spent is now blacklisted. Keeping the old one logs the user out.
      response.cookies.set(REFRESH_TOKEN, renewed.refresh, refreshCookieOptions);
    }
    return response;
  };

  if (pathname.startsWith("/dashboard") && !isAuthed) {
    const target = new URL("/login/", request.url);
    target.searchParams.set("redirect", `${pathname}${search}`);
    return withRenewedCookies(NextResponse.redirect(target));
  }

  if (isPublicRoute(pathname) && isAuthed) {
    return withRenewedCookies(
      NextResponse.redirect(new URL("/dashboard/", request.url)),
    );
  }

  return withRenewedCookies(NextResponse.next({ request }));
}

export const config = {
  // Skip static assets and image optimisation; everything else runs the guard.
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)"],
};
