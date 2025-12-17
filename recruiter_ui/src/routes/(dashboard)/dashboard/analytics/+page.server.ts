import { redirect, error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, cookies, url }) => {
	try {
		const period = url.searchParams.get('period') || '30d';

		// Fetch application analytics from API
		const response = await fetch(
			`http://localhost:8000/api/v1/recruiter/analytics/applications/?period=${period}`
		);

		if (!response.ok) {
			if (response.status === 401) {
				throw redirect(302, '/login/');
			}
			throw error(response.status, 'Failed to load analytics');
		}

		const data = await response.json();

		return {
			analytics: data,
			period: period
		};
	} catch (err) {
		// Re-throw redirects
		if (err instanceof Response && err.status === 302) {
			throw err;
		}
		console.error('Analytics load error:', err);
		throw error(500, 'Failed to load analytics data');
	}
};
