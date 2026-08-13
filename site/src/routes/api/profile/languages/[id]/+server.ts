/**
 * One language entry
 *
 * Thin forwarder to Django. The browser calls this same-origin route with its
 * HttpOnly cookie; hooks.server.ts turns that into the Bearer header.
 */
import type { RequestHandler } from './$types';
import { forward } from '$lib/server/api';

export const trailingSlash = 'always';

export const PATCH: RequestHandler = async ({ params, request, fetch, url }) =>
	forward({ request, fetch, url }, `/profile/languages/${params.id}/`);

export const DELETE: RequestHandler = async ({ params, request, fetch, url }) =>
	forward({ request, fetch, url }, `/profile/languages/${params.id}/`);
