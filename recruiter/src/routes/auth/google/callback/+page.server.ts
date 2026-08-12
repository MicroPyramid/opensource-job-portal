/**
 * Google OAuth callback.
 *
 * Runs entirely on the server: exchange the code, put the tokens in HttpOnly
 * cookies, redirect. The browser never sees a JWT and there is no
 * "Authenticating…" page that has to hydrate before it can do anything.
 *
 * Django answers with one of two shapes:
 *   status: 'authenticated'             — the Google account is already linked
 *   status: 'additional_info_required'  — first time here, we still need a
 *                                         company before an account can exist
 *
 * The second case parks the signed identity in an HttpOnly cookie and hands
 * off to /signup/. Putting it in a cookie rather than the query string keeps
 * the token out of browser history, server logs and any Referer header.
 */

import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { getApiBaseUrl, SITE_URL } from '$lib/config/env';
import { setAuthCookies } from '$lib/server/auth';
import { setPendingGoogleSignup } from '$lib/server/google';

export const load: PageServerLoad = async ({ url, cookies, fetch }) => {
	const code = url.searchParams.get('code');
	const oauthError = url.searchParams.get('error');

	if (oauthError) {
		throw redirect(303, `/login/?error=${encodeURIComponent(oauthError)}`);
	}

	if (!code) {
		throw redirect(303, '/login/?error=no_code');
	}

	// Must match the redirect_uri the auth URL was built with, or Google
	// rejects the exchange.
	const redirectUri = `${SITE_URL}/auth/google/callback/`;

	let data: {
		status?: string;
		access?: string;
		refresh?: string;
		session_token?: string;
		google_data?: { email?: string; first_name?: string; last_name?: string };
		error?: string;
	};

	try {
		const response = await fetch(`${getApiBaseUrl()}/recruiter/auth/google/callback/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ code, redirect_uri: redirectUri })
		});

		data = await response.json();

		if (!response.ok) {
			// The one API error worth naming: a job seeker's Google account
			// cannot sign in here, and "try again" is useless advice for it.
			const isJobSeeker = data?.error?.includes('job seeker');
			throw redirect(303, `/login/?error=${isJobSeeker ? 'job_seeker_account' : 'auth_failed'}`);
		}
	} catch (err) {
		// Re-throw SvelteKit redirects; anything else is a genuine failure.
		if (err && typeof err === 'object' && 'status' in err && 'location' in err) {
			throw err;
		}
		throw redirect(303, '/login/?error=auth_failed');
	}

	if (data.status === 'authenticated' && data.access) {
		setAuthCookies(cookies, data.access, data.refresh);
		throw redirect(303, '/dashboard/');
	}

	if (data.status === 'additional_info_required' && data.session_token) {
		setPendingGoogleSignup(cookies, {
			token: data.session_token,
			email: data.google_data?.email ?? '',
			first_name: data.google_data?.first_name ?? '',
			last_name: data.google_data?.last_name ?? ''
		});

		throw redirect(303, '/complete-signup/');
	}

	throw redirect(303, '/login/?error=auth_failed');
};
