/**
 * /<company>-job-openings/ — every live job at one company.
 *
 * Replaces `pjob.views.each_company_jobs`.
 *
 * Unlike the facet pages, a bad company slug does not make the jobs endpoint
 * 400 — `company_slug` is a plain char filter, so an unknown value just
 * returns zero results. So the company itself is fetched to tell "no such
 * company" (404) apart from "real company, nothing live right now" (a valid,
 * indexable page).
 */

import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { API_BASE_URL, SITE_URL } from '$lib/config/env';
import { buildSeo, fetchLandingJobs, parsePage } from '$lib/server/landing';

export const load: PageServerLoad = async ({ params, url, fetch }) => {
	const page = parsePage(url.searchParams);

	const companyResponse = await fetch(
		`${API_BASE_URL}/companies/${encodeURIComponent(params.company)}/`
	);
	if (companyResponse.status === 404) {
		throw error(404, 'Not found');
	}
	if (!companyResponse.ok) {
		throw error(502, 'Could not load this company.');
	}

	const company = await companyResponse.json();
	const data = await fetchLandingJobs(fetch, { company_slug: params.company }, page);
	const name = (company.name ?? '').trim() || params.company;

	return {
		...data,
		seo: buildSeo({
			heading: `Jobs at ${name}`,
			subject: `job openings at ${name}`,
			totalJobs: data.totalJobs,
			page
		}),
		canonical: `${SITE_URL}/${params.company}-job-openings/`,
		breadcrumb: { label: name, href: `/${params.company}-job-openings/` }
	};
};
