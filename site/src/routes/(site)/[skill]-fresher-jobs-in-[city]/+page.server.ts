/**
 * /<skill>-fresher-jobs-in-<city>/ — entry-level jobs for one skill in one city
 *
 * Replaces `pjob.views.skill_location_wise_fresher_jobs`.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage, resolveFacetName } from '$lib/server/landing';

export const load: PageServerLoad = async ({ params, url, fetch }) => {
	const page = parsePage(url.searchParams);

	const [data, [skillName, cityName]] = await Promise.all([
		fetchLandingJobs(fetch, { max_experience: '0', skills: params.skill, location: params.city }, page),
		Promise.all([
			resolveFacetName(fetch, 'skills', params.skill),
			resolveFacetName(fetch, 'location', params.city)
		])
	]);

	return {
		...data,
		seo: buildSeo({
			heading: `${skillName} Fresher Jobs in ${cityName}`,
			subject: `fresher and entry-level ${skillName} jobs in ${cityName}`,
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/${params.skill}-fresher-jobs-in-${params.city}/`,
		breadcrumb: { label: `${skillName} Fresher Jobs in ${cityName}`, href: `/${params.skill}-fresher-jobs-in-${params.city}/` }
	};
};
