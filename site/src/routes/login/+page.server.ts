/**
 * Login.
 *
 * Two paths in: email/password via the form action below, and Google. The
 * Google auth URL is fetched in `load` so the button is a real link in the
 * server-rendered HTML rather than something the page has to hydrate and then
 * fetch before it can do anything.
 *
 * The password never touches the browser's JS — it posts to this action, which
 * calls Django and puts the returned JWTs straight into HttpOnly cookies.
 */

import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { API_BASE_URL, SITE_URL } from '$lib/config/env';
import { setAuthCookies } from '$lib/server/auth';

const OAUTH_ERRORS: Record<string, string> = {
	access_denied: 'Login was cancelled. Please try again.',
	invalid_request: 'Something went wrong. Please try again.',
	server_error: 'Server error occurred. Please try again later.',
	temporarily_unavailable: 'Service temporarily unavailable. Please try again later.',
	no_code: 'Google did not send an authorization code. Please try again.',
	auth_failed: 'We could not complete your sign-in. Please try again.'
};

export const load: PageServerLoad = async ({ url, locals, fetch }) => {
	// Already signed in — nothing to do here.
	if (locals.isAuthenticated) {
		throw redirect(303, url.searchParams.get('redirect') || '/');
	}

	const errorCode = url.searchParams.get('error');
	const redirectUri = `${SITE_URL}/auth/google/callback/`;

	let googleAuthUrl: string | null = null;

	try {
		const response = await fetch(
			`${API_BASE_URL}/auth/google/url/?redirect_uri=${encodeURIComponent(redirectUri)}`
		);

		if (response.ok) {
			const data = await response.json();
			googleAuthUrl = data.auth_url ?? null;
		}
	} catch {
		// Leave it null; the page renders the button disabled with a notice.
	}

	return {
		googleAuthUrl,
		error: errorCode ? (OAUTH_ERRORS[errorCode] ?? 'An error occurred during login.') : null
	};
};

/**
 * Django returns DRF validation errors, which are either `{field: [msg]}` or
 * `{non_field_errors: [msg]}`. Everything the login serializer raises lands in
 * `non_field_errors`, but field errors show up when a field is missing or
 * malformed, so handle both.
 */
function loginErrorMessage(data: unknown): string {
	const fallback = 'Invalid email or password.';
	if (!data || typeof data !== 'object') return fallback;

	const record = data as Record<string, unknown>;
	for (const key of ['non_field_errors', 'detail', 'email', 'password']) {
		const value = record[key];
		const message = Array.isArray(value) ? value[0] : value;
		if (typeof message === 'string' && message.trim()) return message;
	}
	return fallback;
}

export const actions: Actions = {
	login: async ({ request, fetch, cookies, url }) => {
		const formData = await request.formData();
		const email = formData.get('email')?.toString().trim() ?? '';
		const password = formData.get('password')?.toString() ?? '';

		// Echoed back so the field survives a failed attempt. The password
		// deliberately is not.
		if (!email || !password) {
			return fail(400, { message: 'Please enter your email and password.', email });
		}

		let response: Response;
		try {
			response = await fetch(`${API_BASE_URL}/auth/login/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email, password })
			});
		} catch {
			return fail(503, { message: 'Unable to reach the server. Please try again.', email });
		}

		const data = await response.json().catch(() => null);

		if (!response.ok) {
			return fail(response.status, { message: loginErrorMessage(data), email });
		}

		if (!data?.access) {
			return fail(502, { message: 'Sign-in failed. Please try again.', email });
		}

		setAuthCookies(cookies, data.access, data.refresh);

		// `redirect` is only honoured when it is a path on this site — an
		// absolute URL here would be an open redirect.
		const target = url.searchParams.get('redirect');
		throw redirect(303, target?.startsWith('/') && !target.startsWith('//') ? target : '/');
	}
};
