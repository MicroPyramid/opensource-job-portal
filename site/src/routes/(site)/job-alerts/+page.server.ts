/**
 * /job-alerts/ — subscribe to an email job alert
 *
 * Replaces the six authenticated `candidate/alert/*` routes with one public
 * form. `JobAlert` has no user foreign key — it is keyed on an email address —
 * so alerts were always an anonymous subscription, not a profile feature.
 */

import type { PageServerLoad, Actions } from './$types';
import { fail } from '@sveltejs/kit';
import { API_BASE_URL, SITE_URL } from '$lib/config/env';

export const load: PageServerLoad = async ({ fetch }) => {
	// Populate the pickers from facets that actually have live jobs, so nobody
	// can subscribe to an alert that can never fire.
	let skills: Array<{ name: string; slug: string }> = [];
	let locations: Array<{ name: string; slug: string }> = [];

	try {
		const response = await fetch(`${API_BASE_URL}/jobs/filter-options/?limit=0`);
		if (response.ok) {
			const data = await response.json();
			skills = data.skills ?? [];
			locations = data.locations ?? [];
		}
	} catch (error) {
		console.error('Could not load alert options:', error);
	}

	return {
		skills,
		locations,
		canonical: `${SITE_URL}/job-alerts/`
	};
};

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const form = await request.formData();

		const payload = {
			email: form.get('email')?.toString() ?? '',
			name: form.get('name')?.toString() ?? '',
			skills: form.getAll('skills').map(String),
			locations: form.getAll('locations').map(String),
			min_year: form.get('min_year') ? Number(form.get('min_year')) : null,
			max_year: form.get('max_year') ? Number(form.get('max_year')) : null
		};

		try {
			const response = await fetch(`${API_BASE_URL}/alerts/subscribe/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});

			const data = await response.json().catch(() => null);

			if (!response.ok) {
				return fail(response.status, {
					message: flattenError(data) ?? 'Could not create your job alert.',
					values: payload
				});
			}

			return { success: true, email: data.email };
		} catch (error) {
			console.error('Job alert subscribe error:', error);
			return fail(500, {
				message: 'Unable to reach the server. Please try again.',
				values: payload
			});
		}
	}
};

/** Flatten DRF's `{field: [msg]}` / `{non_field_errors: [msg]}` into one line. */
function flattenError(body: unknown): string | null {
	if (!body || typeof body !== 'object') return null;

	for (const value of Object.values(body as Record<string, unknown>)) {
		if (typeof value === 'string') return value;
		if (Array.isArray(value) && typeof value[0] === 'string') return value[0];
	}
	return null;
}
