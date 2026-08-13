/**
 * /jobs-by-industry/ — every industry with live jobs
 *
 * Replaces `pjob.views.jobs_by_industry`. This is an internal-linking hub: it enumerates
 * every industry that has live jobs, which is how crawlers reach the
 * per-industry landing pages.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchFacetDirectory } from '$lib/server/landing';

export const load: PageServerLoad = async ({ fetch }) => {
	const { groups, total, totalJobs } = await fetchFacetDirectory(fetch, 'industries');

	return {
		groups,
		total,
		seo: {
			...buildSeo({
				heading: 'Jobs by Industry',
				subject: 'job openings across every industry',
				totalJobs,
				page: 1
			}),
			intro: `Browse ${total.toLocaleString('en-IN')} industries with ${totalJobs.toLocaleString(
				'en-IN'
			)} live openings between them.`
		},
		canonical: `${SITE_URL}/jobs-by-industry/`,
		breadcrumb: { label: 'By Industry' }
	};
};
