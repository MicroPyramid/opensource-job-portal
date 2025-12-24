import { redirect, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { getApiBaseUrl } from '$lib/config/env';

export const load: PageServerLoad = async ({ url }) => {
	// Get token from URL query params
	const token = url.searchParams.get('token') || '';

	return {
		token
	};
};

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const formData = await request.formData();

		const token = formData.get('token')?.toString() || '';
		const password = formData.get('password')?.toString() || '';
		const confirmPassword = formData.get('confirm_password')?.toString() || '';

		// Validation
		if (!token) {
			return fail(400, {
				error: 'Invalid or missing reset token'
			});
		}

		if (!password) {
			return fail(400, {
				error: 'Password is required'
			});
		}

		if (password !== confirmPassword) {
			return fail(400, {
				error: 'Passwords do not match'
			});
		}

		if (password.length < 8) {
			return fail(400, {
				error: 'Password must be at least 8 characters'
			});
		}

		try {
			const response = await fetch(`${getApiBaseUrl()}/recruiter/auth/reset-password/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					token,
					password,
					confirm_password: confirmPassword
				})
			});

			if (!response.ok) {
				const data = await response.json();
				let errorMessage = 'Failed to reset password';
				if (data.detail) {
					errorMessage = data.detail;
				} else if (data.token) {
					errorMessage = 'Reset link is invalid or has expired';
				} else if (data.password) {
					errorMessage = Array.isArray(data.password) ? data.password.join(', ') : data.password;
				}

				return fail(400, {
					error: errorMessage
				});
			}

			// Return success state to show confirmation UI
			return {
				success: true
			};
		} catch (error) {
			console.error('Reset password error:', error);
			return fail(500, {
				error: 'An unexpected error occurred. Please try again.'
			});
		}
	}
};
