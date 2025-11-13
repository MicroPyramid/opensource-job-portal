/**
 * Job Preview Page - Server Load
 * Allows recruiters to preview how their job will appear on the public site
 */
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
		// Fetch job details for preview
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

		return {
			job,
			isPreview: true
		};
	} catch (err: any) {
		console.error('Error loading job preview:', err);
		throw error(500, err.message || 'Failed to load job preview');
	}
};
