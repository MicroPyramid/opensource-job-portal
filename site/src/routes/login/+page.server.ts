/**
 * Login.
 *
 * The only provider wired up is Google. The auth URL is fetched here so the
 * button is a real link in the server-rendered HTML rather than something the
 * page has to hydrate and then fetch before it can do anything.
 */

import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { API_BASE_URL, SITE_URL } from '$lib/config/env';

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
