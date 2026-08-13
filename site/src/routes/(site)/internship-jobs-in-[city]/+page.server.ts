/**
 * /internship-jobs-in-<city>/ — internships in one city
 *
 * Replaces `pjob.views.city_internship_jobs`.
 */

import type { PageServerLoad } from './$types';
import { SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage, resolveFacetName } from '$lib/server/landing';

export const load: PageServerLoad = async ({ params, url, fetch }) => {
	const page = parsePage(url.searchParams);

	const [data, cityName] = await Promise.all([
		fetchLandingJobs(fetch, { job_type: 'internship', location: params.city }, page),
		resolveFacetName(fetch, 'location', params.city)
	]);

	return {
		...data,
		seo: buildSeo({
			heading: `Internship Jobs in ${cityName}`,
			subject: `internships in ${cityName}`,
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/internship-jobs-in-${params.city}/`,
		breadcrumb: { label: `Internships in ${cityName}`, href: `/internship-jobs-in-${params.city}/` }
	};
};
