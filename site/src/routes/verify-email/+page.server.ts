import type { PageServerLoad, Actions } from './$types';
import { fail, redirect } from '@sveltejs/kit';
import { API_BASE_URL } from '$lib/config/env';

export const load: PageServerLoad = async ({ url, fetch, cookies }) => {
	const token = url.searchParams.get('token');
	const email = url.searchParams.get('email') || '';

	// If no token, show "check your email" state
	if (!token) {
		return {
			status: 'pending',
			email,
			message: ''
		};
	}

	// If token present, verify it
	try {
		const response = await fetch(`${API_BASE_URL}/auth/verify-email/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ token })
		});

		const data = await response.json();

		if (response.ok && data.success) {
			// Set auth cookies if tokens are returned
			if (data.access && data.refresh) {
				cookies.set('access_token', data.access, {
					path: '/',
					httpOnly: true,
					secure: process.env.NODE_ENV === 'production',
					sameSite: 'lax',
					maxAge: 60 * 60 * 24 * 7 // 7 days
				});

				cookies.set('refresh_token', data.refresh, {
					path: '/',
					httpOnly: true,
					secure: process.env.NODE_ENV === 'production',
					sameSite: 'lax',
					maxAge: 60 * 60 * 24 * 30 // 30 days
				});
			}

			return {
				status: 'success',
				email: data.user?.email || email,
				message: 'Email verified successfully'
			};
		}

		// Check if token expired
		const errorMessage = data.token?.[0] || data.detail || 'Invalid verification token';
		const isExpired = errorMessage.toLowerCase().includes('expired');

		return {
			status: isExpired ? 'expired' : 'error',
			email,
			message: errorMessage
		};
	} catch (error) {
		console.error('Verification error:', error);
		return {
			status: 'error',
			email,
			message: 'Failed to verify email. Please try again.'
		};
	}
};

export const actions: Actions = {
	resend: async ({ request, fetch }) => {
		const formData = await request.formData();
		const email = formData.get('email')?.toString() || '';

		if (!email) {
			return fail(400, {
				success: false,
				message: 'Email address is required'
			});
		}

		try {
			const response = await fetch(`${API_BASE_URL}/auth/resend-verification/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ email })
			});

			const data = await response.json();

			if (response.ok && data.success) {
				return {
					success: true,
					message: 'Verification email sent'
				};
			}

			// Extract error message
			let errorMessage = 'Failed to send verification email';
			if (data.email) {
				errorMessage = Array.isArray(data.email) ? data.email[0] : data.email;
			} else if (data.detail) {
				errorMessage = data.detail;
			}

			return fail(response.status, {
				success: false,
				message: errorMessage
			});
		} catch (error) {
			console.error('Resend verification error:', error);
			return fail(500, {
				success: false,
				message: 'Unable to connect to server. Please try again.'
			});
		}
	}
};
