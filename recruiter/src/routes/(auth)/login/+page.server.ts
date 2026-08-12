import { redirect, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { getApiBaseUrl, SITE_URL } from '$lib/config/env';
import { setAuthCookies } from '$lib/server/auth';

/** Anything the OAuth round trip can bounce back with. */
const OAUTH_ERRORS: Record<string, string> = {
	no_code: 'Google did not send an authorization code. Please try again.',
	auth_failed: 'We could not sign you in with Google. Please try again.',
	access_denied: 'Google sign-in was cancelled.',
	job_seeker_account:
		'That Google account belongs to a job seeker. Use the job seeker site, or sign in with a different account.',
	signup_expired: 'That Google sign-up expired. Please start again.'
};

export const load: PageServerLoad = async ({ url, fetch }) => {
	// Get redirect URL from query params (for post-login redirect)
	const redirectTo = url.searchParams.get('redirect') || '/dashboard/';

	// Must match the redirect_uri sent to the callback exchange, or Google
	// rejects it. SITE_URL is this app's origin, not the job seeker site.
	const redirectUri = `${SITE_URL}/auth/google/callback/`;

	// Fetched server-side so the page ships with a real href — the button works
	// before hydration, and no client code ever touches the API.
	let googleAuthUrl: string | null = null;
	try {
		const response = await fetch(
			`${getApiBaseUrl()}/recruiter/auth/google/url/?redirect_uri=${encodeURIComponent(
				redirectUri
			)}&account_type=company`
		);

		if (response.ok) {
			const data = await response.json();
			googleAuthUrl = data.auth_url ?? null;
		}
	} catch {
		// Google sign-in is optional; the password form still works without it.
	}

	const errorCode = url.searchParams.get('error');

	return {
		redirectTo,
		googleAuthUrl,
		oauthError: errorCode ? (OAUTH_ERRORS[errorCode] ?? OAUTH_ERRORS.auth_failed) : null
	};
};

export const actions: Actions = {
	default: async ({ request, cookies, fetch, url }) => {
		const formData = await request.formData();

		const email = formData.get('email')?.toString() || '';
		const password = formData.get('password')?.toString() || '';
		const rememberMe = formData.get('remember_me') === 'on';
		const redirectTo = formData.get('redirect_to')?.toString() || '/dashboard/';

		// Validate required fields
		if (!email || !password) {
			return fail(400, {
				error: 'Email and password are required',
				email
			});
		}

		try {
			// Call Django login API
			const response = await fetch(`${getApiBaseUrl()}/recruiter/auth/login/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					email,
					password,
					remember_me: rememberMe
				})
			});

			const data = await response.json();

			if (!response.ok) {
				// Format error message
				let errorMessage = 'Login failed. Please check your credentials.';
				if (data.detail) {
					errorMessage = data.detail;
				} else if (data.non_field_errors) {
					errorMessage = data.non_field_errors.join(', ');
				} else if (data.email) {
					errorMessage = `Email: ${data.email.join(', ')}`;
				} else if (data.password) {
					errorMessage = `Password: ${data.password.join(', ')}`;
				}

				return fail(400, {
					error: errorMessage,
					email
				});
			}

			// Set HttpOnly cookies for JWT tokens
			if (data.access) {
				setAuthCookies(cookies, data.access);
			}

			if (data.refresh) {
				setAuthCookies(cookies, undefined, data.refresh);
			}

			// Redirect to dashboard or requested URL
			throw redirect(302, redirectTo);
		} catch (error) {
			// Re-throw redirects
			if (error instanceof Response || (error as any)?.status === 302) {
				throw error;
			}

			console.error('Login error:', error);
			return fail(500, {
				error: 'An unexpected error occurred. Please try again.',
				email
			});
		}
	}
};
