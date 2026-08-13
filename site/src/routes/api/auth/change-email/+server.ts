/**
 * Request a change of the signed-in user's email address
 *
 * Thin forwarder to Django. The address does not move here — Django mails a
 * confirmation link to the new inbox, redeemed at /verify-email-change/.
 */
import type { RequestHandler } from './$types';
import { forward } from '$lib/server/api';

export const trailingSlash = 'always';

export const POST: RequestHandler = async ({ request, fetch, url }) =>
	forward({ request, fetch, url }, '/auth/change-email/');
