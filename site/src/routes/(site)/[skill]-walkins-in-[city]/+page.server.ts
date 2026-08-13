/**
 * /<skill>-walkins-in-<city>/ — walk-in drives for one skill in one city
 *
 * Replaces `search.views.custom_walkins`. Like its sibling
 * `custome_search`, the legacy view lived in the search app but ran on the ORM
 * via `pjob.refine_search.refined_search`, never on Elasticsearch.
 *
 * 1,128 skill x city pairs currently have a live walk-in.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage, resolveFacetName } from '$lib/server/landing';

export const load: PageServerLoad = async ({ params, url, fetch }) => {
	const page = parsePage(url.searchParams);

	const [data, [skillName, cityName]] = await Promise.all([
		fetchLandingJobs(
			fetch,
			{ job_type: 'walk-in', skills: params.skill, location: params.city },
			page
		),
		Promise.all([
			resolveFacetName(fetch, 'skills', params.skill),
			resolveFacetName(fetch, 'location', params.city)
		])
	]);

	return {
		...data,
		seo: buildSeo({
			heading: `${skillName} Walk-in Jobs in ${cityName}`,
			subject: `${skillName} walk-in interviews and drives in ${cityName}`,
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/${params.skill}-walkins-in-${params.city}/`,
		breadcrumb: {
			label: `${skillName} Walk-ins in ${cityName}`,
			href: `/${params.skill}-walkins-in-${params.city}/`
		}
	};
};
