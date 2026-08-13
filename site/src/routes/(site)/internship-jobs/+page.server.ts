/**
 * /internship-jobs/ — all internships
 *
 * Replaces `pjob.views.internship_jobs`.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage } from '$lib/server/landing';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const page = parsePage(url.searchParams);
	const data = await fetchLandingJobs(fetch, { job_type: 'internship' }, page);

	return {
		...data,
		seo: buildSeo({
			heading: 'Internship Jobs',
			subject: 'internships across India',
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/internship-jobs/`,
		breadcrumb: { label: 'Internships', href: '/internship-jobs/' }
	};
};
