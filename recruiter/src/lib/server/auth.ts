/**
 * Server-side auth helpers for the recruiter dashboard.
 *
 * JWTs live in HttpOnly cookies set by *this* SvelteKit server, never by
 * Django. Django only ever receives `Authorization: Bearer <token>` on
 * server-to-server calls, so the browser never holds a token and Django never
 * sees a cookie — which is what makes separate production domains work
 * without third-party cookies.
 */

import { dev } from '$app/environment';
import type { Cookies } from '@sveltejs/kit';
import { API_BASE_URL } from '$lib/config/env';

export const ACCESS_TOKEN = 'access_token';
export const REFRESH_TOKEN = 'refresh_token';

/**
 * Must track SIMPLE_JWT in jobsp/settings.py — ACCESS_TOKEN_LIFETIME is 1 hour
 * and REFRESH_TOKEN_LIFETIME is 7 days.
 */
const ACCESS_MAX_AGE = 60 * 60; // 1 hour
const REFRESH_MAX_AGE = 60 * 60 * 24 * 7; // 7 days

/**
 * `secure` follows the build rather than being hardcoded false — the
 * production dashboard is HTTPS, and a non-secure cookie is sent in the clear.
 */
function cookieOptions(maxAge: number) {
	return {
		httpOnly: true,
		secure: !dev,
		sameSite: 'lax' as const,
		path: '/',
		maxAge
	};
}

export function setAuthCookies(cookies: Cookies, access?: string, refresh?: string) {
	if (access) {
		cookies.set(ACCESS_TOKEN, access, cookieOptions(ACCESS_MAX_AGE));
	}
	if (refresh) {
		cookies.set(REFRESH_TOKEN, refresh, cookieOptions(REFRESH_MAX_AGE));
	}
}

export function clearAuthCookies(cookies: Cookies) {
	cookies.delete(ACCESS_TOKEN, { path: '/' });
	cookies.delete(REFRESH_TOKEN, { path: '/' });
}

/**
 * Exchange a refresh token for a new access token.
 *
 * Django runs ROTATE_REFRESH_TOKENS with BLACKLIST_AFTER_ROTATION, so this
 * also returns a *new* refresh token and blacklists the one just used. Both
 * must be persisted — keeping the old refresh cookie would kill the session on
 * the next refresh.
 */
export async function refreshAccessToken(
	refreshToken: string,
	fetchFn: typeof fetch = fetch
): Promise<{ access: string; refresh?: string } | null> {
	try {
		const response = await fetchFn(`${API_BASE_URL}/auth/token/refresh/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ refresh: refreshToken })
		});

		if (!response.ok) return null;

		const data = await response.json();
		if (!data.access) return null;

		return { access: data.access, refresh: data.refresh };
	} catch {
		return null;
	}
}
