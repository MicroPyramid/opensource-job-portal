import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, cookies }) => {
	try {
		// Fetch dashboard stats
		const statsResponse = await fetch('http://localhost:8000/api/v1/recruiter/dashboard/stats/');

		if (!statsResponse.ok) {
			if (statsResponse.status === 401) {
				throw redirect(302, '/login/');
			}
			console.error('Failed to fetch dashboard stats:', statsResponse.status);
			return {
				stats: null,
				recentJobs: []
			};
		}

		const data = await statsResponse.json();

		return {
			stats: data.stats,
			recentJobs: data.recent_jobs || []
		};
	} catch (error) {
		if (error instanceof Response && error.status === 302) {
			throw error;
		}
		console.error('Dashboard load error:', error);
		return {
			stats: null,
			recentJobs: [],
			error: 'Failed to load dashboard data'
		};
	}
};
