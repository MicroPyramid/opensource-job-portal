/**
 * Server-side load function for jobs page
 * Handles data fetching with proper authentication
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
	const status = url.searchParams.get('status') || '';
	const search = url.searchParams.get('search') || '';
	const page_size = url.searchParams.get('page_size') || '20';

	try {
		// Build API URL with query parameters
		const params = new URLSearchParams({
			page,
			page_size,
			ordering: '-created_on'
		});

		if (status && status !== 'all') {
			params.append('status', status);
		}

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
			throw error(response.status, `Failed to load jobs: ${response.statusText}`);
		}

		const data: JobsListResponse = await response.json();

		return {
			jobs: data.results,
			count: data.count,
			next: data.next,
			previous: data.previous,
			currentPage: parseInt(page),
			filters: {
				status: status || 'all',
				search: search || ''
			}
		};
	} catch (err: any) {
		console.error('Error loading jobs:', err);

		// If it's already a redirect, re-throw it
		if (err.status === 302) {
			throw err;
		}

		throw error(500, err.message || 'Failed to load jobs');
	}
};

export const actions: Actions = {
	/**
	 * Publish a draft job
	 */
	publish: async ({ request, fetch, cookies }) => {
		const formData = await request.formData();
		const jobId = formData.get('jobId');

		if (!jobId) {
			return { success: false, error: 'Job ID is required' };
		}

		try {
			const response = await fetch(`http://localhost:8000/api/v1/recruiter/jobs/${jobId}/publish/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				return {
					success: false,
					error: errorData.error || 'Failed to publish job'
				};
			}

			return { success: true };
		} catch (err: any) {
			return { success: false, error: err.message || 'Failed to publish job' };
		}
	},

	/**
	 * Close an active job
	 */
	close: async ({ request, fetch }) => {
		const formData = await request.formData();
		const jobId = formData.get('jobId');

		if (!jobId) {
			return { success: false, error: 'Job ID is required' };
		}

		try {
			const response = await fetch(`http://localhost:8000/api/v1/recruiter/jobs/${jobId}/close/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				return {
					success: false,
					error: errorData.error || 'Failed to close job'
				};
			}

			return { success: true };
		} catch (err: any) {
			return { success: false, error: err.message || 'Failed to close job' };
		}
	},

	/**
	 * Delete a job
	 */
	delete: async ({ request, fetch }) => {
		const formData = await request.formData();
		const jobId = formData.get('jobId');

		if (!jobId) {
			return { success: false, error: 'Job ID is required' };
		}

		try {
			const response = await fetch(`http://localhost:8000/api/v1/recruiter/jobs/${jobId}/delete/?force=true`, {
				method: 'DELETE'
			});

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				return {
					success: false,
					error: errorData.error || 'Failed to delete job'
				};
			}

			return { success: true };
		} catch (err: any) {
			return { success: false, error: err.message || 'Failed to delete job' };
		}
	}
};
