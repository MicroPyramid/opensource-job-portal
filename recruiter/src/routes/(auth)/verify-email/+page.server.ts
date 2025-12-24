import { fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { getApiBaseUrl } from '$lib/config/env';

export const load: PageServerLoad = async ({ url, cookies, fetch }) => {
	const token = url.searchParams.get('token');
	const email = url.searchParams.get('email') || '';

	// If no token, just show the waiting for verification state
	if (!token) {
		return {
			status: 'waiting' as const,
			email,
			errorMessage: ''
		};
	}

	// Verify the email with the token
	try {
		const response = await fetch(`${getApiBaseUrl()}/recruiter/auth/verify-email/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ token })
		});

		const data = await response.json();

		if (!response.ok) {
			// Check if token is expired or invalid
			const errorMessage = data.detail || data.message || 'Verification failed';
			const isExpired = errorMessage.toLowerCase().includes('expired') ||
			                  errorMessage.toLowerCase().includes('invalid');

			return {
				status: isExpired ? 'expired' as const : 'error' as const,
				email,
				errorMessage
			};
		}

		// Set HttpOnly cookies for JWT tokens
		if (data.access) {
			cookies.set('access_token', data.access, {
				httpOnly: true,
				secure: false,
				sameSite: 'lax',
				path: '/',
				maxAge: 60 * 15
			});
		}

		if (data.refresh) {
			cookies.set('refresh_token', data.refresh, {
				httpOnly: true,
				secure: false,
				sameSite: 'lax',
				path: '/',
				maxAge: 60 * 60 * 24 * 7
			});
		}

		return {
			status: 'success' as const,
			email,
			errorMessage: ''
		};
	} catch (error) {
		console.error('Email verification error:', error);
		return {
			status: 'error' as const,
			email,
			errorMessage: 'An unexpected error occurred during verification.'
		};
	}
};

export const actions: Actions = {
	resend: async ({ request, fetch }) => {
		const formData = await request.formData();
		const email = formData.get('email')?.toString() || '';

		if (!email) {
			return fail(400, {
				error: 'Email address is required',
				success: false
			});
		}

		try {
			const response = await fetch(`${getApiBaseUrl()}/recruiter/auth/resend-verification/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ email })
			});

			if (!response.ok) {
				const data = await response.json();
				return fail(400, {
					error: data.detail || data.message || 'Failed to resend verification email',
					success: false
				});
			}

			return {
				success: true,
				message: 'Verification email sent! Please check your inbox.'
			};
		} catch (error) {
			console.error('Resend verification error:', error);
			return fail(500, {
				error: 'An unexpected error occurred. Please try again.',
				success: false
			});
		}
	}
};
