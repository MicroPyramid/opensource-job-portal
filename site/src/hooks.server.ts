/**
 * SvelteKit server hooks.
 *
 * Two jobs:
 *  1. Keep a usable access token in the HttpOnly cookie, refreshing it when it
 *     has expired but the refresh token is still good.
 *  2. Attach that token to every Django API call made through `event.fetch`,
 *     so no load function or action has to remember to do it.
 *
 * The browser never holds a JWT, so an XSS on this site cannot steal one.
 */

import type { Handle } from '@sveltejs/kit';
import { redirect } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';
import {
	ACCESS_TOKEN,
	REFRESH_TOKEN,
	clearAuthCookies,
	refreshAccessToken,
	setAuthCookies
} from '$lib/server/auth';

/** Routes that require a signed-in job seeker. */
const PROTECTED_PREFIXES = ['/profile', '/applications', '/saved'];

/**
 * Refresh the access token when it has expired but the refresh token has not.
 *
 * Runs before anything reads `locals.accessToken`, so a load function never
 * sees a half-expired session.
 */
const tokenRefresh: Handle = async ({ event, resolve }) => {
	const { cookies } = event;
	let accessToken = cookies.get(ACCESS_TOKEN);
	const refreshToken = cookies.get(REFRESH_TOKEN);

	if (!accessToken && refreshToken) {
		const refreshed = await refreshAccessToken(refreshToken, event.fetch);

		if (refreshed) {
			// Store the rotated refresh token too, or the next refresh fails.
			setAuthCookies(cookies, refreshed.access, refreshed.refresh);
			accessToken = refreshed.access;
		} else {
			// The refresh token is dead — drop both so the user is cleanly
			// logged out rather than stuck retrying on every request.
			clearAuthCookies(cookies);
		}
	}

	event.locals.accessToken = accessToken ?? null;
	event.locals.isAuthenticated = Boolean(accessToken);

	return resolve(event);
};

/**
 * Add the JWT to Django API requests.
 *
 * Mirrors recruiter/src/hooks.server.ts: load functions and actions call
 * `fetch(...)` with a Django URL and the header appears automatically.
 */
const apiAuth: Handle = async ({ event, resolve }) => {
	const originalFetch = event.fetch;

	event.fetch = async (input, init) => {
		const url =
			typeof input === 'string'
				? input
				: input instanceof Request
					? input.url
					: input.toString();

		if (url.includes('/api/v1/') && event.locals.accessToken) {
			const headers = new Headers(init?.headers);

			if (!headers.has('Authorization')) {
				headers.set('Authorization', `Bearer ${event.locals.accessToken}`);
			}

			init = { ...init, headers };
		}

		return originalFetch(input, init);
	};

	return resolve(event);
};

/** Send signed-out visitors to login rather than rendering an empty page. */
const authGuard: Handle = async ({ event, resolve }) => {
	const { url, locals } = event;
	const needsAuth = PROTECTED_PREFIXES.some(
		(prefix) => url.pathname === prefix || url.pathname.startsWith(`${prefix}/`)
	);

	if (needsAuth && !locals.isAuthenticated) {
		throw redirect(302, `/login/?redirect=${encodeURIComponent(url.pathname)}`);
	}

	return resolve(event);
};

export const handle = sequence(tokenRefresh, apiAuth, authGuard);
