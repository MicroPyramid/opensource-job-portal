/**
 * Saved jobs.
 *
 * `hooks.server.ts` guards this route, so reaching the load means there is a
 * session. Unsaving is a form action rather than a browser fetch — the JWT is
 * in an HttpOnly cookie the page cannot read.
 */

import { fail, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { apiDelete, apiGet, ApiRequestError } from '$lib/server/api';
import type { Job } from '$lib/types/jobs';

export const load: PageServerLoad = async ({ fetch }) => {
	try {
		return { savedJobs: await apiGet<Job[]>(fetch, '/jobs/saved/') };
	} catch (err) {
		return {
			savedJobs: [] as Job[],
			loadError:
				err instanceof ApiRequestError ? err.message : 'Could not load your saved jobs.'
		};
	}
};

export const actions: Actions = {
	unsave: async ({ request, fetch }) => {
		const data = await request.formData();
		const jobId = data.get('jobId');

		if (!jobId) {
			return fail(400, { error: 'Missing job id' });
		}

		try {
			await apiDelete(fetch, `/jobs/${jobId}/saved/`);
		} catch (err) {
			const message =
				err instanceof ApiRequestError ? err.message : 'Could not remove that job.';
			return fail(err instanceof ApiRequestError ? err.status : 500, { error: message });
		}

		return { success: true };
	}
};
