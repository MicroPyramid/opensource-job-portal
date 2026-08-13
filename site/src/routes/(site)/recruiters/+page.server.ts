/**
 * /recruiters/ — public recruiter directory
 *
 * Replaces `pjob.views.recruiters`. Listed in
 * `psite.sitemaps.StaticPagesSitemap`, so it is crawler-facing: server
 * rendered, real <a> pagination, and the A–Z filter is a query param rather
 * than the legacy POST so each bucket is its own crawlable URL.
 */

import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import { API_BASE_URL, SITE_URL } from '$lib/config/env';
import { parsePage } from '$lib/server/landing';

const PAGE_SIZE = 45;

export interface RecruiterRow {
	username: string;
	name: string;
	profile_pic: string;
	company_name: string;
	company_slug: string;
	company_logo: string;
	job_count: number;
}

export const load: PageServerLoad = async ({ url, fetch }) => {
	const page = parsePage(url.searchParams);
	const letter = (url.searchParams.get('letter') ?? '').slice(0, 1).toUpperCase();

	const query = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE) });
	if (letter) query.set('letter', letter);

	let response: Response;
	try {
		response = await fetch(`${API_BASE_URL}/recruiters/?${query}`);
	} catch {
		throw error(503, 'The recruiter directory is temporarily unavailable.');
	}

	// DRF answers an out-of-range page with 404 "Invalid page"; that URL does
	// not exist and must hard-404 rather than render an empty directory.
	if (response.status === 404) throw error(404, 'Not found');
	if (!response.ok) throw error(502, 'Could not load the recruiter directory.');

	const data = await response.json();
	const total: number = data.count ?? 0;

	const suffix = page > 1 ? ` - Page ${page}` : '';
	const scope = letter ? ` starting with ${letter}` : '';

	return {
		recruiters: (data.results ?? []) as RecruiterRow[],
		total,
		totalPages: Math.ceil(total / PAGE_SIZE),
		currentPage: page,
		letter,
		letters: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''),
		canonical: `${SITE_URL}/recruiters/`,
		seo: {
			title: `Recruiters${scope}${suffix} | PeelJobs`,
			description: `Browse ${total.toLocaleString('en-IN')} recruiters${scope} hiring on PeelJobs. See their live job openings and apply online.`
		}
	};
};
