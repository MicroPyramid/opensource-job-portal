/**
 * My applications.
 *
 * Guarded by `hooks.server.ts`, so reaching the load means there is a session.
 */

import type { PageServerLoad } from './$types';
import { apiGet, ApiRequestError } from '$lib/server/api';
import type { AppliedJob } from '$lib/types/jobs';

export const load: PageServerLoad = async ({ fetch }) => {
	try {
		return { applications: await apiGet<AppliedJob[]>(fetch, '/jobs/applied/') };
	} catch (err) {
		return {
			applications: [] as AppliedJob[],
			loadError:
				err instanceof ApiRequestError ? err.message : 'Could not load your applications.'
		};
	}
};
