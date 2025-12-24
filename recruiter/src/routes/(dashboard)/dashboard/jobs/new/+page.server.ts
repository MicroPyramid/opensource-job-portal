/**
 * SSR Load Function and Form Actions for Job Posting Page
 *
 * This file handles server-side rendering and form submission for job posting.
 * Following CLAUDE.md guidelines for SSR-only architecture.
 */

import { error, redirect, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import type { JobCreateData, JobFormMetadata } from '$lib/types';

/**
 * Load function - runs on server before page renders
 * Fetches all form metadata needed for job posting
 * Supports copying from existing job via ?copy_from=<job_id> parameter
 */
export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
	// Check authentication
	const accessToken = cookies.get('access_token');
	const refreshToken = cookies.get('refresh_token');

	if (!accessToken && !refreshToken) {
		throw redirect(302, '/login?redirect=' + encodeURIComponent(url.pathname));
	}

	try {
		// Fetch form metadata (countries, states, cities, skills, etc.)
		// The fetch function here is enhanced by hooks.server.ts to add Authorization header
		const apiUrl = 'http://localhost:8000/api/v1/recruiter/jobs/metadata/';
		const response = await fetch(apiUrl);

		if (!response.ok) {
			if (response.status === 401) {
				// Clear invalid tokens and redirect to login
				cookies.delete('access_token', { path: '/' });
				cookies.delete('refresh_token', { path: '/' });
				throw redirect(302, '/login?redirect=' + encodeURIComponent(url.pathname));
			}
			throw error(response.status, `Failed to load form metadata: ${response.statusText}`);
		}

		const metadata: JobFormMetadata = await response.json();

		// Check if copying from existing job
		const copyFromJobId = url.searchParams.get('copy_from');
		let jobToCopy = null;

		if (copyFromJobId) {
			try {
				const jobResponse = await fetch(`http://localhost:8000/api/v1/recruiter/jobs/${copyFromJobId}/`);

				if (jobResponse.ok) {
					jobToCopy = await jobResponse.json();
					// Modify the copied job data
					jobToCopy.title = `Copy of ${jobToCopy.title}`;
					// Remove fields that shouldn't be copied
					delete jobToCopy.id;
					delete jobToCopy.slug;
					delete jobToCopy.created_on;
					delete jobToCopy.published_on;
					delete jobToCopy.status; // Will default to Draft
					delete jobToCopy.applicants_count;
					delete jobToCopy.views_count;
				}
			} catch (err) {
				console.error('Error fetching job to copy:', err);
				// Continue without copy data if fetch fails
			}
		}

		return {
			metadata,
			jobToCopy,
			isCopying: !!copyFromJobId
		};
	} catch (err: any) {
		console.error('Error loading job form metadata:', err);

		// If it's already a redirect, re-throw it
		if (err.status === 302) {
			throw err;
		}

		throw error(500, err.message || 'Failed to load form data');
	}
};

/**
 * Form Actions for job posting
 * These handle form submissions server-side
 */
export const actions: Actions = {
	/**
	 * Save job as draft
	 */
	saveDraft: async ({ request, cookies, fetch }) => {
		const formData = await request.formData();

		try {
			const jobData = extractJobDataFromForm(formData);

			// Log the data being sent for debugging
			console.log('Sending job data:', JSON.stringify(jobData, null, 2));

			// Create job with status 'Draft' (default in API)
			const response = await fetch('http://localhost:8000/api/v1/recruiter/jobs/create/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(jobData)
			});

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				console.error('API Error Response:', errorData);

				// Format error message
				let errorMessage = 'Failed to save draft';
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

			// Return success with job ID for redirect
			return {
				success: true,
				message: result.message || 'Job saved as draft successfully',
				jobId: result.job.id
			};
		} catch (err: any) {
			console.error('Error saving draft:', err);
			return fail(400, {
				error: err.message || 'Failed to save draft',
				values: Object.fromEntries(formData)
			});
		}
	},

	/**
	 * Publish job immediately
	 */
	publish: async ({ request, cookies, fetch }) => {
		const formData = await request.formData();

		try {
			const jobData = extractJobDataFromForm(formData);

			// Step 1: Create job (will be created as Draft by default)
			const createResponse = await fetch('http://localhost:8000/api/v1/recruiter/jobs/create/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(jobData)
			});

			if (!createResponse.ok) {
				const errorData = await createResponse.json().catch(() => ({}));
				return fail(400, {
					error: errorData.error || errorData.detail || 'Failed to create job',
					values: Object.fromEntries(formData)
				});
			}

			const createResult = await createResponse.json();
			const jobId = createResult.job.id;

			// Step 2: Publish the job
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
				// Job was created but publish failed
				// Still return success but with a warning
				return {
					success: true,
					warning: 'Job created as draft. Failed to publish automatically.',
					jobId: jobId
				};
			}

			return {
				success: true,
				message: 'Job published successfully',
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
function extractJobDataFromForm(formData: FormData): JobCreateData {
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
	// For required fields, we keep empty strings; for optional fields, we use undefined
	const title = formData.get('title')?.toString() || '';
	const job_role = formData.get('job_role')?.toString() || formData.get('department')?.toString() || '';
	const description = formData.get('description')?.toString() || '';
	const company_name = formData.get('company_name')?.toString() || '';

	const jobData: JobCreateData = {
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
		application_method: (getString('application_method') || 'portal') as any,
		application_url: getString('application_url'),
		benefits: getStringArray('benefits'),
		language_requirements: getJSON('language_requirements'),
		required_certifications: getString('required_certifications'),
		preferred_certifications: getString('preferred_certifications'),
		relocation_required: getBoolean('relocation_required'),
		travel_percentage: getString('travel_percentage'),
		hiring_timeline: getString('hiring_timeline') as any,
		hiring_priority: (getString('hiring_priority') || 'Normal') as any,

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
