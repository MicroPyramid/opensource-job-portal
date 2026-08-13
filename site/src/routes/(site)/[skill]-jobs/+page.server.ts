/**
 * /<skill>-jobs/ — skill landing page.
 *
 * Replaces `pjob.views.job_skills`. This is the widest of the landing families
 * — 866 skills — so it is the main long-tail surface.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage, resolveFacetName } from '$lib/server/landing';

export const load: PageServerLoad = async ({ params, url, fetch }) => {
	const page = parsePage(url.searchParams);

	const [data, facetName] = await Promise.all([
		fetchLandingJobs(fetch, { skills: params.skill }, page),
		resolveFacetName(fetch, 'skills', params.skill)
	]);

	return {
		...data,
		seo: buildSeo({
			heading: `${facetName} Jobs`,
			subject: `${facetName} job openings`,
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/${params.skill}-jobs/`,
		breadcrumb: { label: facetName, href: `/${params.skill}-jobs/` }
	};
};
