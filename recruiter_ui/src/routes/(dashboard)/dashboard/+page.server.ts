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
				recentJobs: [],
				error: 'Failed to load dashboard data'
			};
		}

		const data = await statsResponse.json();

		// Fetch recent applicants across all jobs
		const applicantsResponse = await fetch('http://localhost:8000/api/v1/recruiter/jobs/?ordering=-created_on&page_size=5');
		let recentApplicants: any[] = [];

		if (applicantsResponse.ok) {
			const jobsData = await applicantsResponse.json();
			// Get recent jobs and fetch applicants for each
			const jobsWithApplicants = jobsData.results || [];

			// Collect all applicants from recent jobs
			for (const job of jobsWithApplicants.slice(0, 3)) {
				const appResponse = await fetch(`http://localhost:8000/api/v1/recruiter/jobs/${job.id}/applicants/?ordering=-applied_on`);
				if (appResponse.ok) {
					const appData = await appResponse.json();
					const applications = appData.applications || [];
					// Add job title to each application
					applications.forEach((app: any) => {
						app.jobTitle = job.title;
					});
					recentApplicants = [...recentApplicants, ...applications];
				}
			}

			// Sort by applied date and take top 5
			recentApplicants.sort((a, b) => {
				return new Date(b.applied_on).getTime() - new Date(a.applied_on).getTime();
			});
			recentApplicants = recentApplicants.slice(0, 5);
		}

		return {
			stats: data.stats,
			recentJobs: data.recent_jobs || [],
			recentApplicants: recentApplicants
		};
	} catch (error) {
		if (error instanceof Response && error.status === 302) {
			throw error;
		}
		console.error('Dashboard load error:', error);
		return {
			stats: null,
			recentJobs: [],
			recentApplicants: [],
			error: 'Failed to load dashboard data'
		};
	}
};
