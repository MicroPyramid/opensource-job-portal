/**
 * /<industry>-industry-jobs/ — industry landing page.
 *
 * Replaces `pjob.views.job_industries`.
 *
 * Note this route and `[skill]-jobs` both match a URL like
 * `/it-software-industry-jobs/`. SvelteKit resolves that by specificity — this
 * route has more static text (`-industry-jobs` vs `-jobs`), so it wins. No
 * skill slug in the corpus ends in `-industry`, so nothing legitimate is
 * shadowed.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage, resolveFacetName } from '$lib/server/landing';

export const load: PageServerLoad = async ({ params, url, fetch }) => {
	const page = parsePage(url.searchParams);

	const [data, facetName] = await Promise.all([
		fetchLandingJobs(fetch, { industry: params.industry }, page),
		resolveFacetName(fetch, 'industry', params.industry)
	]);

	return {
		...data,
		seo: buildSeo({
			heading: `${facetName} Industry Jobs`,
			subject: `jobs in the ${facetName} industry`,
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/${params.industry}-industry-jobs/`,
		breadcrumb: { label: facetName, href: `/${params.industry}-industry-jobs/` }
	};
};
