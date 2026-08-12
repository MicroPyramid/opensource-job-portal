import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config/env';

export const load: PageServerLoad = async ({ fetch, cookies }) => {
	try {
		// Fetch dashboard stats with 30-day period for trends
		const statsResponse = await fetch(`${API_BASE_URL}/recruiter/dashboard/stats/?period=30d`);

		if (!statsResponse.ok) {
			if (statsResponse.status === 401) {
				throw redirect(302, '/login/');
			}
			console.error('Failed to fetch dashboard stats:', statsResponse.status);
			return {
				stats: null,
				pipeline: null,
				recentJobs: []
			};
		}

		const data = await statsResponse.json();

		return {
			stats: data.stats,
			pipeline: data.pipeline,
			recentJobs: data.recent_jobs || []
		};
	} catch (error) {
		if (error instanceof Response && error.status === 302) {
			throw error;
		}
		console.error('Dashboard load error:', error);
		return {
			stats: null,
			pipeline: null,
			recentJobs: [],
			error: 'Failed to load dashboard data'
		};
	}
};
