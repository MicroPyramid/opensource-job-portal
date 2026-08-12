/**
 * Half-finished Google sign-ups.
 *
 * When Google returns an identity we have never seen, Django cannot create the
 * account yet — it still needs a company and the terms acceptance. It answers
 * with a *signed* blob of the verified Google profile (see
 * `GOOGLE_SIGNUP_SALT` in `api/v1/recruiter/auth_views.py`) which the client
 * replays to `auth/google/complete/` once the rest of the form is filled in.
 *
 * We hold that blob in an HttpOnly cookie between the callback and the signup
 * submit. It is tamper-proof server-side, but it is still a bearer credential
 * for one email address, so it stays out of the URL and out of reach of client
 * JavaScript.
 */

import { dev } from '$app/environment';
import type { Cookies } from '@sveltejs/kit';

export const GOOGLE_SIGNUP_COOKIE = 'google_signup';

/**
 * Must not outlive GOOGLE_SIGNUP_MAX_AGE in `auth_views.py`, or the form will
 * still look valid while the token inside it has already expired.
 */
export const GOOGLE_SIGNUP_MAX_AGE = 30 * 60;

export interface PendingGoogleSignup {
	token: string;
	email: string;
	first_name: string;
	last_name: string;
}

export function setPendingGoogleSignup(cookies: Cookies, pending: PendingGoogleSignup) {
	cookies.set(GOOGLE_SIGNUP_COOKIE, JSON.stringify(pending), {
		path: '/',
		httpOnly: true,
		secure: !dev,
		sameSite: 'lax',
		maxAge: GOOGLE_SIGNUP_MAX_AGE
	});
}

/** Returns null when absent or unparseable — either way there is nothing to resume. */
export function readPendingGoogleSignup(cookies: Cookies): PendingGoogleSignup | null {
	const raw = cookies.get(GOOGLE_SIGNUP_COOKIE);
	if (!raw) return null;

	try {
		const parsed = JSON.parse(raw);
		return typeof parsed?.token === 'string' ? parsed : null;
	} catch {
		return null;
	}
}

export function clearPendingGoogleSignup(cookies: Cookies) {
	cookies.delete(GOOGLE_SIGNUP_COOKIE, { path: '/' });
}
