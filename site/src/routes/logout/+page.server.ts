/**
 * Logout.
 *
 * Blacklists the refresh token at Django, then clears the HttpOnly cookies.
 * A POST-only action so a stray link prefetch cannot sign anyone out.
 */

import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config/env';
import { REFRESH_TOKEN, clearAuthCookies } from '$lib/server/auth';

/** Nothing to render — a GET here just goes home. */
export const load: PageServerLoad = async () => {
	throw redirect(303, '/');
};

export const actions: Actions = {
	default: async ({ cookies, fetch }) => {
		const refresh = cookies.get(REFRESH_TOKEN);

		if (refresh) {
			try {
				await fetch(`${API_BASE_URL}/auth/logout/`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ refresh })
				});
			} catch {
				// Blacklisting is best-effort; the cookies still get cleared so
				// the browser session ends either way.
			}
		}

		clearAuthCookies(cookies);
		throw redirect(303, '/');
	}
};
