/**
 * /full-time-jobs/ — all full-time roles
 *
 * Replaces `pjob.views.full_time_jobs`.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage } from '$lib/server/landing';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const page = parsePage(url.searchParams);
	const data = await fetchLandingJobs(fetch, { job_type: 'full-time' }, page);

	return {
		...data,
		seo: buildSeo({
			heading: 'Full Time Jobs',
			subject: 'full-time job openings across India',
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/full-time-jobs/`,
		breadcrumb: { label: 'Full Time', href: '/full-time-jobs/' }
	};
};
