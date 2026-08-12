/**
 * Server-side layout loader for (site) routes.
 *
 * The JWT lives in an HttpOnly cookie, so the user is resolved here on the
 * server and handed down through `data`. Signed-in pages therefore render
 * signed-in HTML on the first response instead of flashing logged-out markup
 * and hydrating afterwards.
 */

import type { LayoutServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config/env';
import { clearAuthCookies } from '$lib/server/auth';

export const load: LayoutServerLoad = async ({ locals, fetch, cookies }) => {
	if (!locals.isAuthenticated) {
		return { user: null, isAuthenticated: false };
	}

	try {
		const response = await fetch(`${API_BASE_URL}/auth/me/`);

		if (response.ok) {
			return { user: await response.json(), isAuthenticated: true };
		}

		// The token survived hooks.server.ts but Django rejected it — treat the
		// session as gone rather than rendering a half-authenticated shell.
		if (response.status === 401) {
			clearAuthCookies(cookies);
		}
	} catch {
		// Django unreachable: fall through to signed-out rather than 500 the
		// whole layout.
	}

	return { user: null, isAuthenticated: false };
};
