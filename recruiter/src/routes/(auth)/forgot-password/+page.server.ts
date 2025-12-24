import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';
import { getApiBaseUrl } from '$lib/config/env';

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const formData = await request.formData();
		const email = formData.get('email')?.toString() || '';

		if (!email) {
			return fail(400, {
				error: 'Email address is required',
				email
			});
		}

		try {
			const response = await fetch(`${getApiBaseUrl()}/recruiter/auth/forgot-password/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ email })
			});

			if (!response.ok) {
				const data = await response.json();
				return fail(400, {
					error: data.detail || data.message || 'Failed to send reset link',
					email
				});
			}

			// Return success state to show confirmation UI
			return {
				success: true,
				email
			};
		} catch (error) {
			console.error('Forgot password error:', error);
			return fail(500, {
				error: 'An unexpected error occurred. Please try again.',
				email
			});
		}
	}
};
