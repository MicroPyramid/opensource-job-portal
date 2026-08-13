/**
 * SSR Load Function and Form Actions for Job Edit Page
 *
 * This file handles server-side rendering and form submission for editing existing jobs.
 * Following CLAUDE.md guidelines for SSR-only architecture.
 */

import { error, redirect, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import type { JobUpdateData, JobFormMetadata, JobDetail } from '$lib/types';
import { API_BASE_URL } from '$lib/config/env';
import { clearAuthCookies } from '$lib/server/auth';

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
			fetch(`${API_BASE_URL}/recruiter/jobs/${jobId}/`),
			fetch(`${API_BASE_URL}/recruiter/jobs/metadata/`)
		]);

		// Handle job fetch errors
		if (!jobResponse.ok) {
			if (jobResponse.status === 401) {
				clearAuthCookies(cookies);
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
				clearAuthCookies(cookies);
				throw redirect(302, '/login?redirect=' + encodeURIComponent(url.pathname));
			}
			throw error(metadataResponse.status, `Failed to load form metadata: ${metadataResponse.statusText}`);
		}

		const job: JobDetail = await jobResponse.json();
		const metadata: JobFormMetadata = await metadataResponse.json();

		// Prevent editing published jobs - redirect to jobs list
		if (job.status === 'Live' || job.status === 'Disabled' || job.status === 'Expired') {
			throw redirect(302, '/dashboard/jobs/?error=' + encodeURIComponent(`Cannot edit a job with status '${job.status}'. Only Draft jobs can be edited.`));
		}

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
			const response = await fetch(`${API_BASE_URL}/recruiter/jobs/${jobId}/update/`, {
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
			const updateResponse = await fetch(`${API_BASE_URL}/recruiter/jobs/${jobId}/update/`, {
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
					`${API_BASE_URL}/recruiter/jobs/${jobId}/publish/`,
					{
						method: 'POST',
						headers: {
							'Content-Type': 'application/json'
						}
					}
				);

				if (!publishResponse.ok) {
					// Job was updated but publish failed - return error
					const errorData = await publishResponse.json().catch(() => ({}));
					return fail(400, {
						error: errorData.error || errorData.detail || 'Job was updated but failed to publish. Please try publishing from the job list.',
						values: Object.fromEntries(formData)
					});
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

	// Helper to get boolean value.
	//
	// Absent means "this form does not carry the field", not "false". The update
	// is a PATCH, so returning undefined leaves the stored value alone; the
	// previous `=== 'true'` collapsed absence to false and wrote it back. That
	// silently cleared show_salary — which defaults to *true* — on every save,
	// along with fresher and relocation_required, none of which this form
	// renders.
	//
	// A bare checkbox is also absent when unchecked, so any checkbox added here
	// needs a hidden `value="false"` companion to be readable as off.
	const getBoolean = (key: string): boolean | undefined => {
		if (!formData.has(key)) return undefined;
		const value = formData.get(key);
		return value === 'true' || value === 'on';
	};

	// Helper to parse JSON field
	const getJSON = (key: string): any | undefined => {
		const value = getString(key);
		if (!value) return undefined;
		try {
			return JSON.parse(value);
		} catch {
			return undefined;
		}
	};

	// Helper to get string array
	const getStringArray = (key: string): string[] | undefined => {
		const value = getString(key);
		if (!value) return undefined;
		return value.split(',').map(s => s.trim()).filter(s => s.length > 0);
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

		// Salary
		min_salary: getNumber('min_salary'),
		max_salary: getNumber('max_salary'),
		salary_type: (getString('salary_type') || 'Year') as any,
		show_salary: getBoolean('show_salary'),

		// Experience
		min_year: getNumber('min_year'),
		max_year: getNumber('max_year'),
		min_month: getNumber('min_month'),
		max_month: getNumber('max_month'),
		fresher: getBoolean('fresher'),

		// Other fields
		vacancies: getNumber('vacancies') || 1,

		// Company details
		company_description: getString('company_description'),
		company_address: getString('company_address'),
		company_links: getString('company_links'),
		company_emails: getString('company_emails'),

		// NEW ENHANCED FIELDS
		seniority_level: getString('seniority_level') as any,
		// No `|| 'portal'` fallback: this form does not render the field, so the
		// default was overwriting an external application flow on every save.
		application_method: getString('application_method') as any,
		application_url: getString('application_url'),
		benefits: getStringArray('benefits'),
		language_requirements: getJSON('language_requirements'),
		required_certifications: getString('required_certifications'),
		preferred_certifications: getString('preferred_certifications'),
		relocation_required: getBoolean('relocation_required'),
		travel_percentage: getString('travel_percentage'),
		hiring_timeline: getString('hiring_timeline') as any,
		// Likewise: unrendered here, so the fallback demoted every Urgent job
		hiring_priority: getString('hiring_priority') as any,

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
