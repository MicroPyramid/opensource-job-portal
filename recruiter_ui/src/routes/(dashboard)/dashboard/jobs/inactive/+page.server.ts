/**
 * Inactive Jobs Page - Server Load
 * Shows Disabled and Expired jobs in a dedicated view
 */
import type { PageServerLoad, Actions } from './$types';
import { error, redirect } from '@sveltejs/kit';
import type { JobsListResponse } from '$lib/types';

export const load: PageServerLoad = async ({ fetch, url, cookies }) => {
	// Check authentication
	const accessToken = cookies.get('access_token');
	const refreshToken = cookies.get('refresh_token');

	if (!accessToken && !refreshToken) {
		throw redirect(302, '/login?redirect=' + encodeURIComponent(url.pathname));
	}

	// Get query parameters
	const page = url.searchParams.get('page') || '1';
	const search = url.searchParams.get('search') || '';
	const page_size = url.searchParams.get('page_size') || '20';
	const statusFilter = url.searchParams.get('status') || 'all'; // 'all', 'Disabled', or 'Expired'

	try {
		// Build API URL with query parameters
		const params = new URLSearchParams({
			page,
			page_size,
			ordering: '-created_on'
		});

		// Filter for inactive jobs only (Disabled OR Expired)
		// Note: If API doesn't support filtering both at once, we get all and filter client-side
		if (statusFilter === 'Disabled' || statusFilter === 'Expired') {
			params.append('status', statusFilter);
		}
		// If 'all', don't add status filter - we'll filter after fetching

		if (search) {
			params.append('search', search);
		}

		// Make API request - fetch will use hooks.server.ts to add Authorization header
		const apiUrl = `http://localhost:8000/api/v1/recruiter/jobs/?${params.toString()}`;
		const response = await fetch(apiUrl);

		if (!response.ok) {
			if (response.status === 401) {
				// Clear invalid tokens and redirect to login
				cookies.delete('access_token', { path: '/' });
				cookies.delete('refresh_token', { path: '/' });
				throw redirect(302, '/login?redirect=' + encodeURIComponent(url.pathname));
			}
			throw error(response.status, `Failed to load inactive jobs: ${response.statusText}`);
		}

		const data: JobsListResponse = await response.json();

		// Filter to show only inactive jobs (Disabled or Expired)
		let filteredJobs = data.results;
		if (statusFilter === 'all' || !statusFilter) {
			// When showing all inactive, filter to only Disabled and Expired
			filteredJobs = data.results.filter(
				(job) => job.status === 'Disabled' || job.status === 'Expired'
			);
		}

		// Get counts for each status from all fetched jobs
		const disabledCount = data.results.filter((job) => job.status === 'Disabled').length;
		const expiredCount = data.results.filter((job) => job.status === 'Expired').length;

		return {
			jobs: filteredJobs,
			count: filteredJobs.length,
			next: data.next,
			previous: data.previous,
			currentPage: parseInt(page),
			filters: {
				status: statusFilter,
				search: search || ''
			},
			stats: {
				disabled: disabledCount,
				expired: expiredCount,
				total: disabledCount + expiredCount
			}
		};
	} catch (err: any) {
		console.error('Error loading inactive jobs:', err);

		// If it's already a redirect, re-throw it
		if (err.status === 302) {
			throw err;
		}

		throw error(500, err.message || 'Failed to load inactive jobs');
	}
};

export const actions: Actions = {
	/**
	 * Re-enable a disabled or expired job
	 */
	reactivate: async ({ request, fetch, cookies }) => {
		const formData = await request.formData();
		const jobId = formData.get('jobId');

		if (!jobId) {
			return { success: false, error: 'Job ID is required' };
		}

		try {
			const response = await fetch(`http://localhost:8000/api/v1/recruiter/jobs/${jobId}/update/`, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					status: 'Draft' // Reactivate as draft for review before publishing
				})
			});

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				return {
					success: false,
					error: errorData.error || 'Failed to reactivate job'
				};
			}

			return { success: true, message: 'Job reactivated as draft' };
		} catch (err: any) {
			return { success: false, error: err.message || 'Failed to reactivate job' };
		}
	},

	/**
	 * Permanently delete an inactive job
	 */
	delete: async ({ request, fetch }) => {
		const formData = await request.formData();
		const jobId = formData.get('jobId');

		if (!jobId) {
			return { success: false, error: 'Job ID is required' };
		}

		try {
			const response = await fetch(
				`http://localhost:8000/api/v1/recruiter/jobs/${jobId}/delete/?force=true`,
				{
					method: 'DELETE'
				}
			);

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				return {
					success: false,
					error: errorData.error || 'Failed to delete job'
				};
			}

			return { success: true, message: 'Job deleted successfully' };
		} catch (err: any) {
			return { success: false, error: err.message || 'Failed to delete job' };
		}
	}
};
