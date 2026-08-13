/**
 * /walkin-jobs/ — all walk-in drives
 *
 * Replaces `pjob.views.walkin_jobs`.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage } from '$lib/server/landing';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const page = parsePage(url.searchParams);
	const data = await fetchLandingJobs(fetch, { job_type: 'walk-in' }, page);

	return {
		...data,
		seo: buildSeo({
			heading: 'Walk-in Jobs',
			subject: 'walk-in interviews and drives across India',
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/walkin-jobs/`,
		breadcrumb: { label: 'Walk-ins', href: '/walkin-jobs/' }
	};
};
