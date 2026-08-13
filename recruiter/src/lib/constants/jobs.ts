/**
 * Job form constants shared by the create and edit forms.
 *
 * These lists used to be declared inline in each form and had drifted: create
 * offered six employment types, edit offered four, and neither offered
 * `walk-in` — which is the second most common type in the data (1,973 posts)
 * and has its own landing pages on the job seeker site. A job whose type was
 * missing from the edit list rendered an unselected `required` select, so it
 * could not be saved without changing its type.
 *
 * `peeldb.models.JOB_TYPE` is the source of truth. `fresher` is deliberately
 * left out: it duplicates the experience range, has zero rows, and the site's
 * fresher landing pages key off `max_experience = 0` rather than the type.
 */

import type { JobTypeSpecificFields } from '$lib/types';

export const EMPLOYMENT_TYPES = [
	{ value: 'full-time', label: 'Full-time' },
	{ value: 'permanent', label: 'Permanent' },
	{ value: 'contract', label: 'Contract' },
	{ value: 'part-time', label: 'Part-time' },
	{ value: 'internship', label: 'Internship' },
	{ value: 'freelance', label: 'Freelance' },
	{ value: 'walk-in', label: 'Walk-in' },
	{ value: 'government', label: 'Government' }
] as const;

/** `peeldb.models.GOV_JOB_TYPE`. */
export const GOVERNMENT_JOB_TYPES = [
	{ value: 'Central', label: 'Central' },
	{ value: 'State', label: 'State' }
] as const;

/** Employment types that carry their own extra fields. */
export function hasTypeSpecificFields(jobType: string): boolean {
	return jobType === 'walk-in' || jobType === 'government';
}

/** Blank values for every type-specific field, for initialising form state. */
export function emptyJobTypeFields(): JobTypeSpecificFields {
	return {
		walkin_contactinfo: '',
		walkin_show_contact_info: false,
		walkin_from_date: '',
		walkin_to_date: '',
		walkin_time: '',
		// Matches the model default; the field has no blank choice, so an empty
		// string is rejected by the serializer.
		govt_job_type: 'Central',
		application_fee: '',
		selection_process: '',
		how_to_apply: '',
		important_dates: '',
		govt_from_date: '',
		govt_to_date: '',
		govt_exam_date: '',
		age_relaxation: ''
	};
}

/**
 * Pull the type-specific fields off a job loaded from the API, so copy and
 * edit start from what is stored rather than from blanks.
 */
export function jobTypeFieldsFrom(job: Partial<JobTypeSpecificFields> | null | undefined): JobTypeSpecificFields {
	const empty = emptyJobTypeFields();
	if (!job) return empty;

	return Object.fromEntries(
		Object.entries(empty).map(([key, blank]) => {
			const value = (job as Record<string, unknown>)[key];
			return [key, value === null || value === undefined ? blank : value];
		})
	) as JobTypeSpecificFields;
}
