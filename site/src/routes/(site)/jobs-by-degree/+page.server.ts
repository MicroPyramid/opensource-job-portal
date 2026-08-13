/**
 * /jobs-by-degree/ — every qualification with live jobs
 *
 * Replaces `pjob.views.jobs_by_degree`. This is an internal-linking hub: it enumerates
 * every qualification that has live jobs, which is how crawlers reach the
 * per-qualification landing pages.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchFacetDirectory } from '$lib/server/landing';

export const load: PageServerLoad = async ({ fetch }) => {
	const { groups, total, totalJobs } = await fetchFacetDirectory(fetch, 'education');

	return {
		groups,
		total,
		seo: {
			...buildSeo({
				heading: 'Jobs by Qualification',
				subject: 'job openings across every qualification',
				totalJobs,
				page: 1
			}),
			intro: `Browse ${total.toLocaleString('en-IN')} qualifications with ${totalJobs.toLocaleString(
				'en-IN'
			)} live openings between them.`
		},
		canonical: `${SITE_URL}/jobs-by-degree/`,
		breadcrumb: { label: 'By Qualification' }
	};
};
