/**
 * /jobs-for-<skill>/ — legacy alternate spelling of /<skill>-jobs/.
 *
 * Both URLs pointed at `pjob.views.job_skills`, so the old site served the
 * same listing at two addresses. Duplicating it here would split ranking
 * signals between them, so this 301s to the canonical form instead.
 */

import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, url }) => {
	const query = url.searchParams.toString();
	throw redirect(301, `/${params.skill}-jobs/${query ? `?${query}` : ''}`);
};
