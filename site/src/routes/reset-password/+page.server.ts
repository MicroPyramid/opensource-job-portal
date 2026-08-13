/**
 * Reset password.
 *
 * There is no "is this token valid?" endpoint — `POST /auth/reset-password/`
 * is the only thing that knows, and it tells us by rejecting the token. So the
 * page shows its invalid-token state in exactly two cases: the URL carried no
 * token at all, or a submit came back with a token error. It never claims a
 * token is good before trying it, which is what the old client-side
 * `validateToken()` did (it resolved to `true` after a 500ms sleep).
 */

import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config/env';

export const load: PageServerLoad = async ({ url }) => ({
	hasToken: Boolean(url.searchParams.get('token'))
});

/** Pull the first string out of a DRF `{field: [msg]}` entry. */
function firstError(data: Record<string, unknown>, key: string): string | null {
	const value = data[key];
	const message = Array.isArray(value) ? value[0] : value;
	return typeof message === 'string' && message.trim() ? message : null;
}

export const actions: Actions = {
	reset: async ({ request, fetch, url }) => {
		const formData = await request.formData();
		// Prefer the posted token so the form still works if the query string is
		// lost on re-render; fall back to the URL.
		const token = formData.get('token')?.toString() || url.searchParams.get('token') || '';
		const password = formData.get('password')?.toString() ?? '';
		const confirm_password = formData.get('confirm_password')?.toString() ?? '';

		if (!token) {
			return fail(400, { tokenExpired: true });
		}

		if (!password || !confirm_password) {
			return fail(400, { message: 'Please fill in both password fields.' });
		}

		if (password !== confirm_password) {
			return fail(400, { confirmPasswordError: 'Passwords do not match' });
		}

		let response: Response;
		try {
			response = await fetch(`${API_BASE_URL}/auth/reset-password/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ token, password, confirm_password })
			});
		} catch {
			return fail(503, { message: 'Unable to reach the server. Please try again.' });
		}

		if (response.ok) {
			return { success: true };
		}

		const data = (await response.json().catch(() => null)) as Record<string, unknown> | null;
		if (!data) {
			return fail(response.status, { message: 'Could not reset your password. Please try again.' });
		}

		// A rejected token means the link is spent or bogus — send the user back
		// to request a fresh one rather than letting them retype a password.
		if (firstError(data, 'token')) {
			return fail(400, { tokenExpired: true });
		}

		const confirmPasswordError = firstError(data, 'confirm_password');
		if (confirmPasswordError) {
			return fail(400, { confirmPasswordError });
		}

		// Django's AUTH_PASSWORD_VALIDATORS speak here — "too common", "too
		// short", "too similar to your email". Surface them verbatim.
		const passwordError = firstError(data, 'password') ?? firstError(data, 'non_field_errors');

		return fail(response.status, {
			passwordError: passwordError ?? 'Could not reset your password. Please try again.'
		});
	}
};
