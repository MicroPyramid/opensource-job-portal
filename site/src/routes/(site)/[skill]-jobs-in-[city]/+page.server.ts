/**
 * /<skill>-jobs-in-<city>/ — jobs for one skill in one city
 *
 * Replaces `search.views.custome_search`. Despite living in the search app,
 * the legacy view never touched Elasticsearch — it ran through
 * `pjob.refine_search.refined_search`, which is plain ORM — so this is a
 * straight swap onto `GET /api/v1/jobs/?skills=&location=`.
 *
 * The highest-traffic landing family on the board: `SkillLocationSitemap`
 * advertises 5,924 of these, more than every other family combined.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage, resolveFacetName } from '$lib/server/landing';

export const load: PageServerLoad = async ({ params, url, fetch }) => {
	const page = parsePage(url.searchParams);

	const [data, [skillName, cityName]] = await Promise.all([
		fetchLandingJobs(fetch, { skills: params.skill, location: params.city }, page),
		Promise.all([
			resolveFacetName(fetch, 'skills', params.skill),
			resolveFacetName(fetch, 'location', params.city)
		])
	]);

	return {
		...data,
		seo: buildSeo({
			heading: `${skillName} Jobs in ${cityName}`,
			subject: `${skillName} jobs in ${cityName}`,
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/${params.skill}-jobs-in-${params.city}/`,
		breadcrumb: {
			label: `${skillName} Jobs in ${cityName}`,
			href: `/${params.skill}-jobs-in-${params.city}/`
		}
	};
};
