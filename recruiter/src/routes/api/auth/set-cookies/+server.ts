/**
 * Server endpoint to set HttpOnly cookies
 * This is called by the client after receiving JWT tokens from Django
 *
 * Architecture: Django returns JWT in response body → SvelteKit stores in HttpOnly cookies
 */
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, cookies }) => {
	const { access, refresh } = await request.json();

	if (!access || !refresh) {
		return json({ error: 'Missing tokens' }, { status: 400 });
	}

	// Set HttpOnly cookies
	cookies.set('access_token', access, {
		httpOnly: true,
		secure: false, // Set to true in production (HTTPS)
		sameSite: 'lax',
		path: '/',
		maxAge: 60 * 15 // 15 minutes
	});

	cookies.set('refresh_token', refresh, {
		httpOnly: true,
		secure: false, // Set to true in production
		sameSite: 'lax',
		path: '/',
		maxAge: 60 * 60 * 24 * 7 // 7 days
	});

	return json({ success: true });
};
