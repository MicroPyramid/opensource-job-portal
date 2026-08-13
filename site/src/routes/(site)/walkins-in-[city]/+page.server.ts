/**
 * /walkins-in-<city>/ — walk-in drives in one city
 *
 * Replaces `pjob.views.skill_location_walkin_jobs`.
 *
 * The legacy view names its parameter `skill_name` for both this and
 * `/<skill>-walkins/`, resolving the slug as either a skill or a location. The
 * `-in-` form is the location one.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage, resolveFacetName } from '$lib/server/landing';

export const load: PageServerLoad = async ({ params, url, fetch }) => {
	const page = parsePage(url.searchParams);

	const [data, cityName] = await Promise.all([
		fetchLandingJobs(fetch, { job_type: 'walk-in', location: params.city }, page),
		resolveFacetName(fetch, 'location', params.city)
	]);

	return {
		...data,
		seo: buildSeo({
			heading: `Walk-in Jobs in ${cityName}`,
			subject: `walk-in interviews and drives in ${cityName}`,
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/walkins-in-${params.city}/`,
		breadcrumb: { label: `Walk-ins in ${cityName}`, href: `/walkins-in-${params.city}/` }
	};
};
