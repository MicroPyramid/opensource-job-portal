/**
 * Auth cookie names and lifetimes — the single source of truth.
 *
 * Deliberately free of `server-only` and `next/headers` imports so `proxy.ts`
 * (which renews tokens) and `lib/auth/session.ts` (which issues them at login)
 * can share it. Duplicating these values is how the two drift apart.
 *
 * Lifetimes mirror SIMPLE_JWT in backend/jobsp/settings.py. Keep them in sync:
 * a cookie that outlives its JWT causes 401s the user can't explain, and one
 * that expires early forces needless refreshes.
 */

export const ACCESS_TOKEN = "access_token";
export const REFRESH_TOKEN = "refresh_token";

/**
 * 1 hour — SIMPLE_JWT.ACCESS_TOKEN_LIFETIME.
 *
 * The SvelteKit app used 15 minutes here while the JWT itself was valid for an
 * hour, so it refreshed ~4x more often than needed. That matters more than it
 * looks: ROTATE_REFRESH_TOKENS + BLACKLIST_AFTER_ROTATION are both on, so every
 * refresh invalidates the previous refresh token. Fewer refreshes, fewer races.
 */
export const ACCESS_MAX_AGE = 60 * 60;

/** 7 days — SIMPLE_JWT.REFRESH_TOKEN_LIFETIME. */
export const REFRESH_MAX_AGE = 60 * 60 * 24 * 7;

export const cookieOptions = {
  httpOnly: true,
  // Hardcoded `false` in the SvelteKit app, sending JWTs over plain HTTP.
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax",
  path: "/",
} as const;

export const accessCookieOptions = {
  ...cookieOptions,
  maxAge: ACCESS_MAX_AGE,
};

export const refreshCookieOptions = {
  ...cookieOptions,
  maxAge: REFRESH_MAX_AGE,
};
