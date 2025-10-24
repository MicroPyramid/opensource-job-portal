import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config/env';

export const load: PageServerLoad = async ({ params, cookies, fetch }) => {
	const jobId = params.id;

	// Get JWT token from cookies
	const accessToken = cookies.get('access_token');

	if (!accessToken) {
		throw error(401, 'Unauthorized');
	}

	try {
		// Fetch job details
		const jobResponse = await fetch(`${API_BASE_URL}/recruiter/jobs/${jobId}/`, {
			headers: {
				Authorization: `Bearer ${accessToken}`
			}
		});

		if (!jobResponse.ok) {
			if (jobResponse.status === 404) {
				throw error(404, 'Job not found');
			}
			throw error(jobResponse.status, 'Failed to fetch job details');
		}

		const job = await jobResponse.json();

		// Fetch applicants summary
		const applicantsResponse = await fetch(`${API_BASE_URL}/recruiter/jobs/${jobId}/applicants/`, {
			headers: {
				Authorization: `Bearer ${accessToken}`
			}
		});

		let applicantsData = {
			total_applicants: 0,
			stats: {
				pending: 0,
				shortlisted: 0,
				selected: 0,
				rejected: 0
			}
		};

		if (applicantsResponse.ok) {
			applicantsData = await applicantsResponse.json();
		}

		return {
			job,
			applicantsStats: applicantsData.stats,
			totalApplicants: applicantsData.total_applicants
		};
	} catch (err: any) {
		console.error('Error loading job details:', err);
		throw error(500, err.message || 'Failed to load job details');
	}
};
