/**
 * Job-seeker profile
 *
 * Thin forwarder to Django. The browser calls this same-origin route with its
 * HttpOnly cookie; hooks.server.ts turns that into the Bearer header.
 */
import type { RequestHandler } from './$types';
import { forward } from '$lib/server/api';

// The client calls these with a trailing slash, matching Django. Endpoints
// do not inherit trailingSlash from +layout.js, so set it here or every
// request pays a 308 redirect.
export const trailingSlash = 'always';

export const GET: RequestHandler = async ({ request, fetch, url }) =>
	forward({ request, fetch, url }, '/profile/');

export const PATCH: RequestHandler = async ({ request, fetch, url }) =>
	forward({ request, fetch, url }, '/profile/');

export const PUT: RequestHandler = async ({ request, fetch, url }) =>
	forward({ request, fetch, url }, '/profile/');
