/**
 * /recruiters/<username>/ — one recruiter's public profile and live openings
 *
 * Replaces `pjob.views.recruiter_profile`. The username is matched
 * case-insensitively by the API, matching the legacy `username__iexact`, so
 * old inbound links keep working whatever casing they carry.
 */

import type { PageServerLoad } from './$types';
import { error, isHttpError } from '@sveltejs/kit';
import { API_BASE_URL, SITE_URL } from '$lib/config/env';
import { fetchLandingJobs, parsePage } from '$lib/server/landing';

export const load: PageServerLoad = async ({ params, url, fetch }) => {
	const page = parsePage(url.searchParams);

	try {
		const profileResponse = await fetch(
			`${API_BASE_URL}/recruiters/${encodeURIComponent(params.username)}/`
		);

		// The API only exposes recruiters that have at least one live job, so a
		// 404 here covers "no such user", "not a recruiter" and "nothing live".
		if (profileResponse.status === 404) throw error(404, 'Recruiter not found');
		if (!profileResponse.ok) throw error(502, 'Could not load this recruiter.');

		const recruiter = await profileResponse.json();
		const jobs = await fetchLandingJobs(fetch, { recruiter: params.username }, page);

		const heading = recruiter.company_name
			? `${recruiter.name} — ${recruiter.company_name}`
			: recruiter.name;
		const suffix = page > 1 ? ` - Page ${page}` : '';
		const count = jobs.totalJobs.toLocaleString('en-IN');

		return {
			recruiter,
			...jobs,
			canonical: `${SITE_URL}/recruiters/${params.username}/`,
			seo: {
				title: `${heading} — Job Openings${suffix} | PeelJobs`,
				description: `${count} live ${jobs.totalJobs === 1 ? 'opening' : 'openings'} posted by ${heading} on PeelJobs. Apply online.`,
				heading
			}
		};
	} catch (err) {
		// error() throws, and the 404 above is raised inside this try — without
		// the re-throw the catch would turn every unknown recruiter into a 500.
		if (isHttpError(err)) throw err;

		console.error('Error loading recruiter:', err);
		throw error(500, 'Failed to load recruiter');
	}
};
