/**
 * /<skill>-fresher-jobs/ — entry-level jobs for one skill
 *
 * Replaces `pjob.views.skill_fresher_jobs`.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage, resolveFacetName } from '$lib/server/landing';

export const load: PageServerLoad = async ({ params, url, fetch }) => {
	const page = parsePage(url.searchParams);

	const [data, skillName] = await Promise.all([
		fetchLandingJobs(fetch, { max_experience: '0', skills: params.skill }, page),
		resolveFacetName(fetch, 'skills', params.skill)
	]);

	return {
		...data,
		seo: buildSeo({
			heading: `${skillName} Fresher Jobs`,
			subject: `fresher and entry-level ${skillName} jobs`,
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/${params.skill}-fresher-jobs/`,
		breadcrumb: { label: `${skillName} Fresher Jobs`, href: `/${params.skill}-fresher-jobs/` }
	};
};
