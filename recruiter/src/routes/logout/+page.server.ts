/**
 * Logout.
 *
 * Blacklists the refresh token at Django, then clears the HttpOnly cookies.
 * POST-only so a stray link prefetch cannot sign anyone out.
 */

import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config/env';
import { REFRESH_TOKEN, clearAuthCookies } from '$lib/server/auth';

/** Nothing to render — a GET here just goes to login. */
export const load: PageServerLoad = async () => {
	throw redirect(303, '/login/');
};

export const actions: Actions = {
	default: async ({ cookies, fetch }) => {
		const refresh = cookies.get(REFRESH_TOKEN);

		if (refresh) {
			try {
				await fetch(`${API_BASE_URL}/recruiter/auth/logout/`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ refresh })
				});
			} catch {
				// Best-effort blacklisting; the cookies still get cleared.
			}
		}

		clearAuthCookies(cookies);
		throw redirect(303, '/login/');
	}
};
