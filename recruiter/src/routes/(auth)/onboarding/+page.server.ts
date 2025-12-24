import { redirect, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { getApiBaseUrl } from '$lib/config/env';

export const load: PageServerLoad = async ({ cookies }) => {
	// Check for auth tokens - onboarding requires authentication
	const accessToken = cookies.get('access_token');
	const refreshToken = cookies.get('refresh_token');

	if (!accessToken && !refreshToken) {
		throw redirect(302, '/login/');
	}

	return {};
};

export const actions: Actions = {
	complete: async ({ request, cookies, fetch }) => {
		const formData = await request.formData();

		// Extract form data
		const about = formData.get('about')?.toString() || '';
		const headquarters = formData.get('headquarters')?.toString() || '';
		const foundedYear = formData.get('founded_year')?.toString() || '';

		// Team invitations (comma-separated emails)
		const inviteEmailsRaw = formData.get('invite_emails')?.toString() || '';
		const inviteEmails = inviteEmailsRaw
			.split(',')
			.map((e) => e.trim())
			.filter((e) => e);

		// Hiring preferences
		const jobCategoriesRaw = formData.get('job_categories')?.toString() || '';
		const jobCategories = jobCategoriesRaw
			.split(',')
			.map((c) => c.trim())
			.filter((c) => c);
		const hiringGoals = formData.get('hiring_goals')?.toString() || '';
		const monthlyHires = formData.get('monthly_hires')?.toString() || '';

		try {
			// Update company profile
			const profileResponse = await fetch(`${getApiBaseUrl()}/recruiter/company/profile/`, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					about,
					headquarters,
					founded_year: foundedYear || undefined,
					job_categories: jobCategories,
					hiring_goals: hiringGoals || undefined,
					monthly_hires: monthlyHires || undefined
				})
			});

			if (!profileResponse.ok) {
				const data = await profileResponse.json();
				let errorMessage = 'Failed to update profile';
				if (data.detail) {
					errorMessage = data.detail;
				}

				return fail(400, {
					error: errorMessage
				});
			}

			// Send team invitations if any
			if (inviteEmails.length > 0) {
				const inviteResponse = await fetch(`${getApiBaseUrl()}/recruiter/team/invite/`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({
						emails: inviteEmails
					})
				});

				// Don't fail if invitations fail, just log it
				if (!inviteResponse.ok) {
					console.error('Failed to send team invitations');
				}
			}

			// Redirect to dashboard
			throw redirect(302, '/dashboard/');
		} catch (error) {
			// Re-throw redirects
			if (error instanceof Response || (error as any)?.status === 302) {
				throw error;
			}

			console.error('Onboarding error:', error);
			return fail(500, {
				error: 'An unexpected error occurred. Please try again.'
			});
		}
	},

	skip: async () => {
		// Just redirect to dashboard without updating anything
		throw redirect(302, '/dashboard/');
	}
};
