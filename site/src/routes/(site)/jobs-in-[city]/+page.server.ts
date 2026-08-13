/**
 * /jobs-in-<city>/ — location landing page.
 *
 * Replaces `pjob.views.job_locations`.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage, resolveFacetName } from '$lib/server/landing';

export const load: PageServerLoad = async ({ params, url, fetch }) => {
	const page = parsePage(url.searchParams);

	// Both hit the API, and neither depends on the other.
	const [data, facetName] = await Promise.all([
		fetchLandingJobs(fetch, { location: params.city }, page),
		resolveFacetName(fetch, 'location', params.city)
	]);

	return {
		...data,
		seo: buildSeo({
			heading: `Jobs in ${facetName}`,
			subject: `job openings in ${facetName}`,
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/jobs-in-${params.city}/`,
		breadcrumb: { label: facetName, href: `/jobs-in-${params.city}/` }
	};
};
