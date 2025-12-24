import { redirect, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { getApiBaseUrl } from '$lib/config/env';

export const load: PageServerLoad = async ({ url }) => {
	// Check for invitation token in URL
	const invitationToken = url.searchParams.get('invitation') || '';

	return {
		invitationToken
	};
};

export const actions: Actions = {
	register: async ({ request, fetch }) => {
		const formData = await request.formData();

		// Extract form data
		const accountType = formData.get('account_type')?.toString() || '';
		const firstName = formData.get('first_name')?.toString() || '';
		const lastName = formData.get('last_name')?.toString() || '';
		const email = formData.get('email')?.toString() || '';
		const phone = formData.get('phone')?.toString() || '';
		const jobTitle = formData.get('job_title')?.toString() || '';
		const password = formData.get('password')?.toString() || '';
		const confirmPassword = formData.get('confirm_password')?.toString() || '';

		// Company fields (for company accounts)
		const companyName = formData.get('company_name')?.toString() || '';
		const companyWebsite = formData.get('company_website')?.toString() || '';
		const companyIndustry = formData.get('company_industry')?.toString() || '';
		const companySize = formData.get('company_size')?.toString() || '';

		// Validation
		if (!firstName || !lastName || !email || !password) {
			return fail(400, {
				error: 'Please fill in all required fields',
				values: Object.fromEntries(formData)
			});
		}

		if (password !== confirmPassword) {
			return fail(400, {
				error: 'Passwords do not match',
				values: Object.fromEntries(formData)
			});
		}

		try {
			// Build request data
			const requestData: Record<string, any> = {
				account_type: accountType,
				first_name: firstName,
				last_name: lastName,
				email,
				password,
				confirm_password: confirmPassword,
				agree_to_terms: true
			};

			if (phone) requestData.phone = phone;
			if (jobTitle) requestData.job_title = jobTitle;

			// Add company fields if company account
			if (accountType === 'company') {
				if (companyName) requestData.company_name = companyName;
				if (companyWebsite) requestData.company_website = companyWebsite;
				if (companyIndustry) requestData.company_industry = companyIndustry;
				if (companySize) requestData.company_size = companySize;
			}

			const response = await fetch(`${getApiBaseUrl()}/recruiter/auth/register/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(requestData)
			});

			const data = await response.json();

			if (!response.ok) {
				// Format error message from Django validation errors
				let errorMessage = 'Registration failed';
				if (data.detail) {
					errorMessage = data.detail;
				} else if (typeof data === 'object') {
					const errors = Object.entries(data)
						.map(([field, msgs]) => {
							const messages = Array.isArray(msgs) ? msgs.join(', ') : msgs;
							return `${field}: ${messages}`;
						})
						.join('\n');
					if (errors) errorMessage = errors;
				}

				return fail(400, {
					error: errorMessage,
					values: Object.fromEntries(formData)
				});
			}

			// Redirect to verify email page
			throw redirect(302, `/verify-email?email=${encodeURIComponent(email)}`);
		} catch (error) {
			// Re-throw redirects
			if (error instanceof Response || (error as any)?.status === 302) {
				throw error;
			}

			console.error('Registration error:', error);
			return fail(500, {
				error: 'An unexpected error occurred. Please try again.',
				values: Object.fromEntries(formData)
			});
		}
	},

	acceptInvitation: async ({ request, cookies, fetch }) => {
		const formData = await request.formData();

		const token = formData.get('token')?.toString() || '';
		const firstName = formData.get('first_name')?.toString() || '';
		const lastName = formData.get('last_name')?.toString() || '';
		const password = formData.get('password')?.toString() || '';
		const confirmPassword = formData.get('confirm_password')?.toString() || '';

		// Validation
		if (!token || !firstName || !lastName || !password) {
			return fail(400, {
				error: 'Please fill in all required fields',
				values: Object.fromEntries(formData)
			});
		}

		if (password !== confirmPassword) {
			return fail(400, {
				error: 'Passwords do not match',
				values: Object.fromEntries(formData)
			});
		}

		try {
			const response = await fetch(`${getApiBaseUrl()}/recruiter/auth/accept-invitation/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					token,
					first_name: firstName,
					last_name: lastName,
					password,
					confirm_password: confirmPassword
				})
			});

			const data = await response.json();

			if (!response.ok) {
				let errorMessage = 'Failed to accept invitation';
				if (data.detail) {
					errorMessage = data.detail;
				} else if (typeof data === 'object') {
					const errors = Object.entries(data)
						.map(([field, msgs]) => {
							const messages = Array.isArray(msgs) ? msgs.join(', ') : msgs;
							return `${field}: ${messages}`;
						})
						.join('\n');
					if (errors) errorMessage = errors;
				}

				return fail(400, {
					error: errorMessage,
					values: Object.fromEntries(formData)
				});
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

			// Redirect to dashboard
			throw redirect(302, '/dashboard/');
		} catch (error) {
			// Re-throw redirects
			if (error instanceof Response || (error as any)?.status === 302) {
				throw error;
			}

			console.error('Accept invitation error:', error);
			return fail(500, {
				error: 'An unexpected error occurred. Please try again.',
				values: Object.fromEntries(formData)
			});
		}
	}
};
