import { error, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { API_BASE_URL } from '$lib/config/env';

export const load: PageServerLoad = async ({ params, url, cookies, fetch }) => {
	const jobId = params.id;
	const statusFilter = url.searchParams.get('status') || 'all';
	const searchQuery = url.searchParams.get('search') || '';

	// Get JWT token from cookies
	const accessToken = cookies.get('access_token');

	if (!accessToken) {
		throw error(401, 'Unauthorized');
	}

	try {
		// Build query parameters
		const queryParams = new URLSearchParams();
		if (statusFilter !== 'all') {
			queryParams.set('status', statusFilter);
		}
		if (searchQuery) {
			queryParams.set('search', searchQuery);
		}

		// Fetch job details and applicants
		const [jobResponse, applicantsResponse] = await Promise.all([
			fetch(`${API_BASE_URL}/recruiter/jobs/${jobId}/`, {
				headers: {
					Authorization: `Bearer ${accessToken}`
				}
			}),
			fetch(`${API_BASE_URL}/recruiter/jobs/${jobId}/applicants/?${queryParams.toString()}`, {
				headers: {
					Authorization: `Bearer ${accessToken}`
				}
			})
		]);

		if (!jobResponse.ok) {
			if (jobResponse.status === 404) {
				throw error(404, 'Job not found');
			}
			throw error(jobResponse.status, 'Failed to fetch job details');
		}

		if (!applicantsResponse.ok) {
			throw error(applicantsResponse.status, 'Failed to fetch applicants');
		}

		const job = await jobResponse.json();
		const applicantsData = await applicantsResponse.json();

		return {
			job,
			applications: applicantsData.applications || [],
			stats: applicantsData.stats || {
				pending: 0,
				shortlisted: 0,
				selected: 0,
				rejected: 0
			},
			totalApplicants: applicantsData.total_applicants || 0,
			filters: {
				status: statusFilter,
				search: searchQuery
			}
		};
	} catch (err: any) {
		console.error('Error loading applicants:', err);
		throw error(500, err.message || 'Failed to load applicants');
	}
};

export const actions: Actions = {
	updateStatus: async ({ request, params, cookies, fetch }) => {
		const jobId = params.id;
		const accessToken = cookies.get('access_token');

		if (!accessToken) {
			return fail(401, { error: 'Unauthorized' });
		}

		const formData = await request.formData();
		const applicantId = formData.get('applicantId');
		const status = formData.get('status');
		const remarks = formData.get('remarks');

		if (!applicantId || !status) {
			return fail(400, { error: 'Missing required fields' });
		}

		try {
			const response = await fetch(
				`${API_BASE_URL}/recruiter/jobs/${jobId}/applicants/${applicantId}/update/`,
				{
					method: 'PATCH',
					headers: {
						'Content-Type': 'application/json',
						Authorization: `Bearer ${accessToken}`
					},
					body: JSON.stringify({
						status,
						remarks: remarks || ''
					})
				}
			);

			if (!response.ok) {
				const errorData = await response.json();
				return fail(response.status, { error: errorData.error || 'Failed to update status' });
			}

			const result = await response.json();

			return {
				success: true,
				message: result.message
			};
		} catch (err: any) {
			console.error('Error updating applicant status:', err);
			return fail(500, { error: err.message || 'Failed to update status' });
		}
	}
};
