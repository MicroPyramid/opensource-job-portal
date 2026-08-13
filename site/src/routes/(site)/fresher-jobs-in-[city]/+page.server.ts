/**
 * /fresher-jobs-in-<city>/ — entry-level jobs in one city
 *
 * Replaces `pjob.views.location_fresher_jobs`.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage, resolveFacetName } from '$lib/server/landing';

export const load: PageServerLoad = async ({ params, url, fetch }) => {
	const page = parsePage(url.searchParams);

	const [data, cityName] = await Promise.all([
		fetchLandingJobs(fetch, { max_experience: '0', location: params.city }, page),
		resolveFacetName(fetch, 'location', params.city)
	]);

	return {
		...data,
		seo: buildSeo({
			heading: `Fresher Jobs in ${cityName}`,
			subject: `fresher and entry-level jobs in ${cityName}`,
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/fresher-jobs-in-${params.city}/`,
		breadcrumb: { label: `Fresher Jobs in ${cityName}`, href: `/fresher-jobs-in-${params.city}/` }
	};
};
