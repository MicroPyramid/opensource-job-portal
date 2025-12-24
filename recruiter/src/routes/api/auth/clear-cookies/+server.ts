/**
 * Server endpoint to clear HttpOnly cookies
 * This is called during logout to remove JWT tokens from cookies
 *
 * Architecture: SvelteKit manages cookies, Django just validates JWT headers
 */
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ cookies }) => {
	// Clear HttpOnly cookies
	cookies.delete('access_token', { path: '/' });
	cookies.delete('refresh_token', { path: '/' });

	return json({ success: true });
};
