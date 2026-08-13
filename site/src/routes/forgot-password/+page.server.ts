/**
 * Forgot password.
 *
 * Django deliberately answers 200 whether or not the address has an account,
 * so the page must not branch on that — any "no such user" feedback here would
 * hand out an account-enumeration oracle. A successful POST always renders the
 * same "check your email" state.
 */

import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config/env';

export const load: PageServerLoad = async () => ({});

export const actions: Actions = {
	request: async ({ request, fetch }) => {
		const formData = await request.formData();
		const email = formData.get('email')?.toString().trim() ?? '';

		if (!email) {
			return fail(400, { message: 'Please enter your email address.', email });
		}

		let response: Response;
		try {
			response = await fetch(`${API_BASE_URL}/auth/forgot-password/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email })
			});
		} catch {
			return fail(503, {
				message: 'Unable to reach the server. Please try again.',
				email
			});
		}

		if (!response.ok) {
			// The only 400 here is a malformed address; the endpoint does not
			// distinguish known from unknown emails.
			const data = await response.json().catch(() => null);
			const detail = data && typeof data === 'object' ? (data as Record<string, unknown>).email : null;
			const message = Array.isArray(detail) ? detail[0] : detail;

			return fail(response.status, {
				message: typeof message === 'string' ? message : 'Please enter a valid email address.',
				email
			});
		}

		return { success: true, email };
	}
};
