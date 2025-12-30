import type { Actions } from './$types';
import { fail } from '@sveltejs/kit';
import { API_BASE_URL } from '$lib/config/env';

export const actions: Actions = {
	register: async ({ request, fetch }) => {
		const formData = await request.formData();

		const email = formData.get('email')?.toString() || '';
		const password = formData.get('password')?.toString() || '';
		const confirm_password = formData.get('confirm_password')?.toString() || '';
		const full_name = formData.get('full_name')?.toString() || '';

		// Parse full name into first and last name
		const nameParts = full_name.trim().split(' ');
		const first_name = nameParts[0] || '';
		const last_name = nameParts.slice(1).join(' ') || '';

		// Validate required fields
		if (!email || !password || !confirm_password || !first_name) {
			return fail(400, {
				message: 'Please fill in all required fields',
				email
			});
		}

		// Validate passwords match
		if (password !== confirm_password) {
			return fail(400, {
				message: 'Passwords do not match',
				email
			});
		}

		try {
			const response = await fetch(`${API_BASE_URL}/auth/register/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					email,
					password,
					confirm_password,
					first_name,
					last_name
				})
			});

			const data = await response.json();

			if (!response.ok) {
				// Extract error message from API response
				let errorMessage = 'Registration failed. Please try again.';

				if (data.email) {
					errorMessage = Array.isArray(data.email) ? data.email[0] : data.email;
				} else if (data.password) {
					errorMessage = Array.isArray(data.password) ? data.password[0] : data.password;
				} else if (data.confirm_password) {
					errorMessage = Array.isArray(data.confirm_password)
						? data.confirm_password[0]
						: data.confirm_password;
				} else if (data.non_field_errors) {
					errorMessage = Array.isArray(data.non_field_errors)
						? data.non_field_errors[0]
						: data.non_field_errors;
				} else if (data.detail) {
					errorMessage = data.detail;
				}

				return fail(response.status, {
					message: errorMessage,
					email
				});
			}

			// Success - return email for redirect
			return {
				success: true,
				email
			};
		} catch (error) {
			console.error('Registration error:', error);
			return fail(500, {
				message: 'Unable to connect to server. Please try again.',
				email
			});
		}
	}
};
