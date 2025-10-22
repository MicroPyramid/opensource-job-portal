/**
 * SSR Load Function and Form Actions for Job Edit Page
 *
 * This file handles server-side rendering and form submission for editing existing jobs.
 * Following CLAUDE.md guidelines for SSR-only architecture.
 */

import { error, redirect, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import type { JobUpdateData, JobFormMetadata, JobDetail } from '$lib/types';

/**
 * Load function - runs on server before page renders
 * Fetches job details and form metadata
 */
export const load: PageServerLoad = async ({ params, cookies, fetch, url }) => {
	// Check authentication
	const accessToken = cookies.get('access_token');
	const refreshToken = cookies.get('refresh_token');

	if (!accessToken && !refreshToken) {
		throw redirect(302, '/login?redirect=' + encodeURIComponent(url.pathname));
	}

	const jobId = params.id;

	try {
		// Fetch job details and form metadata in parallel
		const [jobResponse, metadataResponse] = await Promise.all([
			fetch(`http://localhost:8000/api/v1/recruiter/jobs/${jobId}/`),
			fetch('http://localhost:8000/api/v1/recruiter/jobs/metadata/')
		]);

		// Handle job fetch errors
		if (!jobResponse.ok) {
			if (jobResponse.status === 401) {
				cookies.delete('access_token', { path: '/' });
				cookies.delete('refresh_token', { path: '/' });
				throw redirect(302, '/login?redirect=' + encodeURIComponent(url.pathname));
			}
			if (jobResponse.status === 404) {
				throw error(404, 'Job not found');
			}
			throw error(jobResponse.status, `Failed to load job: ${jobResponse.statusText}`);
		}

		// Handle metadata fetch errors
		if (!metadataResponse.ok) {
			if (metadataResponse.status === 401) {
				cookies.delete('access_token', { path: '/' });
				cookies.delete('refresh_token', { path: '/' });
				throw redirect(302, '/login?redirect=' + encodeURIComponent(url.pathname));
			}
			throw error(metadataResponse.status, `Failed to load form metadata: ${metadataResponse.statusText}`);
		}

		const job: JobDetail = await jobResponse.json();
		const metadata: JobFormMetadata = await metadataResponse.json();

		return {
			job,
			metadata
		};
	} catch (err: any) {
		console.error('Error loading job edit page:', err);

		// If it's already a redirect or error, re-throw it
		if (err.status === 302 || err.status === 404) {
			throw err;
		}

		throw error(500, err.message || 'Failed to load job data');
	}
};

/**
 * Form Actions for job editing
 */
export const actions: Actions = {
	/**
	 * Save job changes as draft
	 */
	saveDraft: async ({ params, request, cookies, fetch }) => {
		const jobId = params.id;
		const formData = await request.formData();

		try {
			const jobData = extractJobDataFromForm(formData);

			console.log('Updating job data:', JSON.stringify(jobData, null, 2));

			// Update job
			const response = await fetch(`http://localhost:8000/api/v1/recruiter/jobs/${jobId}/update/`, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(jobData)
			});

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				console.error('API Error Response:', errorData);

				// Format error message
				let errorMessage = 'Failed to save changes';
				if (errorData.error) {
					errorMessage = errorData.error;
				} else if (errorData.detail) {
					errorMessage = errorData.detail;
				} else if (typeof errorData === 'object') {
					// Django validation errors format
					const errors = Object.entries(errorData)
						.map(([field, msgs]) => {
							const messages = Array.isArray(msgs) ? msgs.join(', ') : msgs;
							return `${field}: ${messages}`;
						})
						.join('; ');
					if (errors) errorMessage = errors;
				}

				return fail(400, {
					error: errorMessage,
					values: Object.fromEntries(formData)
				});
			}

			const result = await response.json();

			return {
				success: true,
				message: result.message || 'Job updated successfully',
				jobId: result.job.id
			};
		} catch (err: any) {
			console.error('Error updating job:', err);
			return fail(400, {
				error: err.message || 'Failed to update job',
				values: Object.fromEntries(formData)
			});
		}
	},

	/**
	 * Update and publish job
	 */
	publish: async ({ params, request, cookies, fetch }) => {
		const jobId = params.id;
		const formData = await request.formData();

		try {
			const jobData = extractJobDataFromForm(formData);

			// Step 1: Update job
			const updateResponse = await fetch(`http://localhost:8000/api/v1/recruiter/jobs/${jobId}/update/`, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(jobData)
			});

			if (!updateResponse.ok) {
				const errorData = await updateResponse.json().catch(() => ({}));
				return fail(400, {
					error: errorData.error || errorData.detail || 'Failed to update job',
					values: Object.fromEntries(formData)
				});
			}

			const updateResult = await updateResponse.json();

			// Step 2: Publish the job if it's not already published
			if (updateResult.job.status !== 'Live') {
				const publishResponse = await fetch(
					`http://localhost:8000/api/v1/recruiter/jobs/${jobId}/publish/`,
					{
						method: 'POST',
						headers: {
							'Content-Type': 'application/json'
						}
					}
				);

				if (!publishResponse.ok) {
					// Job was updated but publish failed
					return {
						success: true,
						warning: 'Job updated successfully but failed to publish.',
						jobId: jobId
					};
				}
			}

			return {
				success: true,
				message: 'Job updated and published successfully',
				jobId: jobId
			};
		} catch (err: any) {
			console.error('Error publishing job:', err);
			return fail(400, {
				error: err.message || 'Failed to publish job',
				values: Object.fromEntries(formData)
			});
		}
	}
};

/**
 * Helper function to extract job data from FormData
 */
function extractJobDataFromForm(formData: FormData): JobUpdateData {
	// Helper to get array values from FormData
	const getArray = (key: string): number[] => {
		const values = formData.getAll(key);
		return values
			.map((v) => parseInt(v.toString()))
			.filter((v) => !isNaN(v));
	};

	// Helper to get number value
	const getNumber = (key: string): number | undefined => {
		const value = formData.get(key);
		if (!value || value === '') return undefined;
		const num = parseInt(value.toString());
		return isNaN(num) ? undefined : num;
	};

	// Helper to get string value
	const getString = (key: string): string | undefined => {
		const value = formData.get(key);
		if (!value) return undefined;
		const strValue = value.toString().trim();
		return strValue === '' ? undefined : strValue;
	};

	// Helper to get boolean value
	const getBoolean = (key: string): boolean => {
		return formData.get(key) === 'true' || formData.get(key) === 'on';
	};

	// Extract basic fields
	const title = formData.get('title')?.toString() || '';
	const job_role = formData.get('job_role')?.toString() || formData.get('department')?.toString() || '';
	const description = formData.get('description')?.toString() || '';
	const company_name = formData.get('company_name')?.toString() || '';

	const jobData: JobUpdateData = {
		title,
		job_role,
		description,
		company_name,
		job_type: (getString('job_type') || 'full-time') as any,
		work_mode: (getString('work_mode') || 'in-office') as any,

		// Location IDs (from city selections)
		location_ids: getArray('location_ids'),

		// Skills, Industries, etc.
		skill_ids: getArray('skill_ids'),
		industry_ids: getArray('industry_ids'),
		qualification_ids: getArray('qualification_ids'),
		functional_area_ids: getArray('functional_area_ids'),

		// Salary
		min_salary: getNumber('min_salary'),
		max_salary: getNumber('max_salary'),
		salary_type: (getString('salary_type') || 'Year') as any,

		// Experience
		min_year: getNumber('min_year'),
		max_year: getNumber('max_year'),
		min_month: getNumber('min_month'),
		max_month: getNumber('max_month'),
		fresher: getBoolean('fresher'),

		// Other fields
		vacancies: getNumber('vacancies') || 1,
		last_date: getString('last_date'),

		// Company details
		company_description: getString('company_description'),
		company_address: getString('company_address'),
		company_links: getString('company_links'),
		company_emails: getString('company_emails'),

		// Walk-in fields
		walkin_contactinfo: getString('walkin_contactinfo'),
		walkin_show_contact_info: getBoolean('walkin_show_contact_info'),
		walkin_from_date: getString('walkin_from_date'),
		walkin_to_date: getString('walkin_to_date'),
		walkin_time: getString('walkin_time'),

		// Government job fields
		govt_job_type: getString('govt_job_type'),
		application_fee: getString('application_fee'),
		selection_process: getString('selection_process'),
		how_to_apply: getString('how_to_apply'),
		important_dates: getString('important_dates'),
		govt_from_date: getString('govt_from_date'),
		govt_to_date: getString('govt_to_date'),
		govt_exam_date: getString('govt_exam_date'),
		age_relaxation: getString('age_relaxation'),
	};

	return jobData;
}
