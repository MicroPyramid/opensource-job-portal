/**
 * Shared loader for the SEO job-landing pages.
 *
 * These are the URLs the legacy Django site ranked on — /jobs-in-hyderabad/,
 * /java-jobs/, /it-software-industry-jobs/ and friends. Each is the same
 * query against `GET /api/v1/jobs/` with one filter pinned, wrapped in copy
 * that names the facet.
 *
 * Two things they must get right, because they are crawler-facing:
 *
 * 1. **An unknown facet is a hard 404, never an empty page.** Django answers a
 *    bogus slug with 400 ("Select a valid choice"), which maps cleanly to
 *    `error(404)`. Rendering "0 jobs found" instead would be a soft-404, and
 *    search engines penalise those.
 * 2. **They render on the server.** No `onMount` fetches — the markup a
 *    crawler sees has to be the finished page.
 *
 * The legacy meta machinery is not worth porting: `MetaData` (the table that
 * held the title/description templates) is empty, City's meta fields are empty
 * across all 113 rows, and only 76 of 866 skills have a `meta_title`. So titles
 * and descriptions are generated here from the facet name and the live job
 * count.
 */

import { error } from '@sveltejs/kit';
import { API_BASE_URL } from '$lib/config/env';

export const PAGE_SIZE = 20;

export interface LandingJob {
	id: number;
	slug: string;
	title: string;
	company_name: string;
	company_logo: string | null;
	location_display: string;
	salary_display: string;
	experience_display: string;
	job_type: string;
	time_ago: string;
	applicants_count: number;
	accepts_applications: boolean;
}

export interface LandingPageData {
	jobs: LandingJob[];
	totalJobs: number;
	totalPages: number;
	currentPage: number;
}

/**
 * Turn a slug into something readable: `new-delhi` -> `New Delhi`.
 *
 * Only a fallback. Prefer the real name from the API, which preserves casing
 * the slug destroys — `it-software` is "IT-Software", not "It Software".
 */
export function titleiseSlug(slug: string): string {
	return slug
		.split('-')
		.filter(Boolean)
		.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
		.join(' ');
}

/** `?page=2` -> 2. Anything junk or < 1 collapses to page 1. */
export function parsePage(searchParams: URLSearchParams): number {
	const raw = Number(searchParams.get('page'));
	return Number.isInteger(raw) && raw > 0 ? raw : 1;
}

/**
 * Filters that pin a landing page, as API query params.
 *
 * Note fresher pages use `max_experience=0`, **not** `fresher=true`. The
 * `fresher` boolean is set on exactly 1 of 12,770 live jobs — it was never
 * really adopted — whereas `max_experience=0` (jobs whose `min_year` is 0)
 * matches 6,936. Using the flag would ship four empty landing pages.
 */
export const FRESHER_FILTER = { max_experience: '0' } as const;
export const WALKIN_FILTER = { job_type: 'walk-in' } as const;

/**
 * Fetch one page of jobs for a pinned set of facets.
 *
 * `filters` are API query params, e.g. `{ skills: 'java', location: 'pune' }`.
 */
export async function fetchLandingJobs(
	fetchFn: typeof fetch,
	filters: Record<string, string>,
	page: number
): Promise<LandingPageData> {
	const query = new URLSearchParams();
	for (const [key, value] of Object.entries(filters)) {
		query.set(key, value);
	}
	query.set('page', String(page));
	query.set('page_size', String(PAGE_SIZE));

	let response: Response;
	try {
		response = await fetchFn(`${API_BASE_URL}/jobs/?${query}`);
	} catch {
		throw error(503, 'Job listings are temporarily unavailable.');
	}

	// 400 = the facet slug is not a valid choice; 404 = DRF pagination's
	// "Invalid page". Both mean this URL does not exist, and both must be a
	// hard 404 rather than a soft-404 empty page.
	if (response.status === 400 || response.status === 404) {
		throw error(404, 'Not found');
	}

	if (!response.ok) {
		throw error(502, 'Could not load job listings.');
	}

	const data = await response.json();
	const totalJobs = data.count ?? 0;

	// Page 1 of an empty facet is legitimate (a real city with no live jobs
	// right now); page 5 of a 2-page result is not.
	const totalPages = Math.ceil(totalJobs / PAGE_SIZE);
	if (page > 1 && page > totalPages) {
		throw error(404, 'Not found');
	}

	return {
		jobs: data.results ?? [],
		totalJobs,
		totalPages,
		currentPage: page
	};
}

/**
 * Resolve a slug to its proper display name via a lookup endpoint.
 *
 * Falls back to title-casing rather than failing: a facet with zero live jobs
 * still deserves a sensible heading, and `filter-options` only returns facets
 * that currently have jobs.
 */
export async function resolveFacetName(
	fetchFn: typeof fetch,
	kind: 'skills' | 'location' | 'industry',
	slug: string
): Promise<string> {
	const endpoint =
		kind === 'skills'
			? `${API_BASE_URL}/skills/?search=${encodeURIComponent(slug.replace(/-/g, ' '))}`
			: `${API_BASE_URL}/jobs/filter-options/`;

	try {
		const response = await fetchFn(endpoint);
		if (!response.ok) return titleiseSlug(slug);

		const data = await response.json();
		const candidates: Array<{ name?: string; slug?: string }> =
			kind === 'skills'
				? Array.isArray(data)
					? data
					: (data.results ?? [])
				: kind === 'location'
					? (data.locations ?? [])
					: (data.industries ?? []);

		const match = candidates.find((entry) => entry.slug === slug);
		return match?.name?.trim() || titleiseSlug(slug);
	} catch {
		return titleiseSlug(slug);
	}
}

export interface Facet {
	id: number;
	name: string;
	slug: string;
	count: number;
}

/** A directory's facets grouped under an initial, e.g. `{ letter: 'J', items: [...] }`. */
export interface FacetGroup {
	letter: string;
	items: Facet[];
}

/**
 * Every facet of one kind, with live job counts, grouped alphabetically.
 *
 * Backs the directory pages (/jobs-by-skill/ and friends). `limit=0` is what
 * lifts `filter-options`' default top-50 slice — these pages exist precisely to
 * enumerate the long tail, which is how a crawler discovers the several
 * hundred landing pages built on top of it.
 */
export async function fetchFacetDirectory(
	fetchFn: typeof fetch,
	kind: 'locations' | 'skills' | 'industries' | 'education'
): Promise<{ groups: FacetGroup[]; total: number; totalJobs: number }> {
	let response: Response;
	try {
		response = await fetchFn(`${API_BASE_URL}/jobs/filter-options/?limit=0`);
	} catch {
		throw error(503, 'Job categories are temporarily unavailable.');
	}

	if (!response.ok) {
		throw error(502, 'Could not load job categories.');
	}

	const data = await response.json();
	const facets: Facet[] = (data[kind] ?? [])
		.map((f: Facet) => ({ ...f, name: (f.name ?? '').trim() }))
		.filter((f: Facet) => f.name && f.slug);

	const byLetter = new Map<string, Facet[]>();
	for (const facet of facets) {
		// Anything not starting with A–Z buckets under '#' rather than
		// vanishing — ".NET" and "3D Modelling" are real entries here.
		const first = facet.name[0].toUpperCase();
		const letter = first >= 'A' && first <= 'Z' ? first : '#';
		const bucket = byLetter.get(letter);
		if (bucket) bucket.push(facet);
		else byLetter.set(letter, [facet]);
	}

	const groups = [...byLetter.entries()]
		.map(([letter, items]) => ({
			letter,
			items: items.sort((a, b) => a.name.localeCompare(b.name))
		}))
		// '#' last, letters in order.
		.sort((a, b) =>
			a.letter === '#' ? 1 : b.letter === '#' ? -1 : a.letter.localeCompare(b.letter)
		);

	return {
		groups,
		total: facets.length,
		totalJobs: facets.reduce((sum, f) => sum + (f.count ?? 0), 0)
	};
}

/**
 * Title/description/H1 for a landing page.
 *
 * `heading` is the H1 ("Walk-in Jobs in Hyderabad"); `subject` is the same
 * thing as a noun phrase for prose ("walk-in jobs in Hyderabad"). Each route
 * composes its own wording — the families phrase too differently to derive it
 * from an enum.
 */
export function buildSeo(params: {
	heading: string;
	subject: string;
	totalJobs: number;
	page: number;
}) {
	const { heading, subject, totalJobs, page } = params;
	const suffix = page > 1 ? ` - Page ${page}` : '';
	const count = totalJobs.toLocaleString('en-IN');

	return {
		title: `${heading}${suffix} | PeelJobs`,
		description: totalJobs
			? `Browse ${count} latest ${subject}. Apply online to vacancies across India on PeelJobs.`
			: `Latest ${subject} on PeelJobs. Browse job openings across India.`,
		heading,
		intro: totalJobs
			? `${count} ${totalJobs === 1 ? 'opening' : 'openings'} — ${subject}, updated daily.`
			: `No live ${subject} right now. New jobs are posted daily — check back soon.`
	};
}
