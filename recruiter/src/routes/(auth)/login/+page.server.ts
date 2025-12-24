import { redirect, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { getApiBaseUrl } from '$lib/config/env';

export const load: PageServerLoad = async ({ url }) => {
	// Get redirect URL from query params (for post-login redirect)
	const redirectTo = url.searchParams.get('redirect') || '/dashboard/';

	return {
		redirectTo
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
				cookies.set('access_token', data.access, {
					httpOnly: true,
					secure: false, // Set to true in production (HTTPS)
					sameSite: 'lax',
					path: '/',
					maxAge: 60 * 15 // 15 minutes
				});
			}

			if (data.refresh) {
				cookies.set('refresh_token', data.refresh, {
					httpOnly: true,
					secure: false, // Set to true in production
					sameSite: 'lax',
					path: '/',
					maxAge: 60 * 60 * 24 * 7 // 7 days
				});
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
