/**
 * SvelteKit Server Hooks
 * Handles authentication guards and JWT token management
 */

import type { Handle } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';

/**
 * API request handler - adds JWT token to Django API requests
 * Reads JWT from cookies and adds Authorization header
 */
const apiHandler: Handle = async ({ event, resolve }) => {
	// Enhance event.fetch to automatically add Authorization header for Django API calls
	const originalFetch = event.fetch;

	event.fetch = async (input, init) => {
		const url = typeof input === 'string' ? input : (input instanceof Request ? input.url : input.toString());

		// If this is a request to our Django API
		if (url.includes('/api/v1/')) {
			// Get access token from cookies
			const accessToken = event.cookies.get('access_token');

			if (accessToken) {
				// Add Authorization header with JWT
				const headers = new Headers(init?.headers);
				headers.set('Authorization', `Bearer ${accessToken}`);

				init = {
					...init,
					headers
				};
			}
		}

		return originalFetch(input, init);
	};

	return resolve(event);
};

/**
 * Authentication hook
 * Protects dashboard routes and redirects unauthenticated users to login
 */
const authGuard: Handle = async ({ event, resolve }) => {
	const { url, cookies } = event;

	// Get tokens from HttpOnly cookies
	// Check for refresh_token (7 days) as well as access_token (15 mins)
	const accessToken = cookies.get('access_token');
	const refreshToken = cookies.get('refresh_token');
	const hasValidAuth = accessToken || refreshToken;

	// Public routes that don't require authentication
	const publicRoutes = [
		'/login',
		'/signup',
		'/forgot-password',
		'/reset-password',
		'/verify-email',
		'/onboarding'
	];

	// Check if current route is public
	const isPublicRoute = publicRoutes.some((route) => url.pathname.startsWith(route));

	// If accessing dashboard without any auth tokens, redirect to login
	if (url.pathname.startsWith('/dashboard') && !hasValidAuth) {
		return new Response(null, {
			status: 302,
			headers: {
				location: '/login?redirect=' + encodeURIComponent(url.pathname)
			}
		});
	}

	// If accessing auth pages while authenticated, redirect to dashboard
	if (isPublicRoute && hasValidAuth) {
		return new Response(null, {
			status: 302,
			headers: {
				location: '/dashboard'
			}
		});
	}

	return resolve(event);
};

/**
 * CORS handler for API requests
 */
const corsHandler: Handle = async ({ event, resolve }) => {
	if (event.request.method === 'OPTIONS') {
		return new Response(null, {
			headers: {
				'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
				'Access-Control-Allow-Origin': '*',
				'Access-Control-Allow-Headers': '*'
			}
		});
	}

	const response = await resolve(event);
	return response;
};

// Combine hooks in sequence
// apiHandler MUST come before authGuard so it can modify fetch before auth checks
export const handle = sequence(corsHandler, apiHandler, authGuard);
