/**
 * /<skill>-walkins/ — walk-in drives for one skill
 *
 * Replaces `pjob.views.skill_location_walkin_jobs`.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage, resolveFacetName } from '$lib/server/landing';

export const load: PageServerLoad = async ({ params, url, fetch }) => {
	const page = parsePage(url.searchParams);

	const [data, skillName] = await Promise.all([
		fetchLandingJobs(fetch, { job_type: 'walk-in', skills: params.skill }, page),
		resolveFacetName(fetch, 'skills', params.skill)
	]);

	return {
		...data,
		seo: buildSeo({
			heading: `${skillName} Walk-in Jobs`,
			subject: `${skillName} walk-in interviews and drives`,
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/${params.skill}-walkins/`,
		breadcrumb: { label: `${skillName} Walk-ins`, href: `/${params.skill}-walkins/` }
	};
};
