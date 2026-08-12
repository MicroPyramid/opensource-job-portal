/**
 * Google OAuth callback.
 *
 * Runs entirely on the server: exchange the code for tokens, put them in
 * HttpOnly cookies, redirect. The browser never sees a JWT, and there is no
 * intermediate "Authenticating…" page that has to hydrate before it can act.
 */

import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { API_BASE_URL, SITE_URL } from '$lib/config/env';
import { setAuthCookies } from '$lib/server/auth';

export const load: PageServerLoad = async ({ url, cookies, fetch }) => {
	const code = url.searchParams.get('code');
	const oauthError = url.searchParams.get('error');

	if (oauthError) {
		throw redirect(303, `/login/?error=${encodeURIComponent(oauthError)}`);
	}

	if (!code) {
		throw redirect(303, '/login/?error=no_code');
	}

	// Must match the redirect_uri Google was given, or the exchange is rejected.
	const redirectUri = `${SITE_URL}/auth/google/callback/`;

	let data: {
		access?: string;
		refresh?: string;
		redirect_to?: string;
	};

	try {
		const response = await fetch(`${API_BASE_URL}/auth/google/callback/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ code, redirect_uri: redirectUri })
		});

		if (!response.ok) {
			throw redirect(303, '/login/?error=auth_failed');
		}

		data = await response.json();
	} catch (err) {
		// Re-throw SvelteKit redirects; anything else is a genuine failure.
		if (err && typeof err === 'object' && 'status' in err && 'location' in err) {
			throw err;
		}
		throw redirect(303, '/login/?error=auth_failed');
	}

	if (!data.access) {
		throw redirect(303, '/login/?error=auth_failed');
	}

	setAuthCookies(cookies, data.access, data.refresh);

	throw redirect(303, data.redirect_to || '/');
};
