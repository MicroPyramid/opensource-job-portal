/**
 * /jobs-by-skill/ — every skill with live jobs
 *
 * Replaces `pjob.views.jobs_by_skill`. This is an internal-linking hub: it enumerates
 * every skill that has live jobs, which is how crawlers reach the
 * per-skill landing pages.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchFacetDirectory } from '$lib/server/landing';

export const load: PageServerLoad = async ({ fetch }) => {
	const { groups, total, totalJobs } = await fetchFacetDirectory(fetch, 'skills');

	return {
		groups,
		total,
		seo: {
			...buildSeo({
				heading: 'Jobs by Skill',
				subject: 'job openings across every skill',
				totalJobs,
				page: 1
			}),
			intro: `Browse ${total.toLocaleString('en-IN')} skills with ${totalJobs.toLocaleString(
				'en-IN'
			)} live openings between them.`
		},
		canonical: `${SITE_URL}/jobs-by-skill/`,
		breadcrumb: { label: 'By Skill' }
	};
};
