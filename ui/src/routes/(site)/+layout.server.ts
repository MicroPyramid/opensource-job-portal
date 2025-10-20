/**
 * Server-side layout loader for (site) routes
 * Loads auth state from localStorage to prevent hydration mismatch
 *
 * SECURITY NOTE:
 * - JWT tokens are in HttpOnly cookies (not accessible to JavaScript)
 * - We only read user profile data for SSR rendering
 * - Tokens are automatically sent with API requests via cookies
 */

import type { LayoutServerLoad } from './$types';
import type { User } from '$lib/api/auth';
import { getApiBaseUrl } from '$lib/config/env';

export const load: LayoutServerLoad = async ({ cookies, fetch }) => {
	// Check if user has access token cookie (HttpOnly, can't read value)
	const hasAccessToken = cookies.get('access_token') !== undefined;

	// If no access token, user is not authenticated
	if (!hasAccessToken) {
		return {
			user: null,
			isAuthenticated: false
		};
	}

	// Fetch user data from API (cookies sent automatically)
	try {
		const response = await fetch(`${getApiBaseUrl()}/auth/me/`, {
			credentials: 'include'  // Send HttpOnly cookies
		});

		if (!response.ok) {
			// Token invalid or expired, clear cookies
			cookies.delete('access_token', { path: '/' });
			cookies.delete('refresh_token', { path: '/' });
			return {
				user: null,
				isAuthenticated: false
			};
		}

		const user: User = await response.json();

		// Return auth state (user data only, tokens stay in HttpOnly cookies)
		return {
			user,
			isAuthenticated: true
		};
	} catch (error) {
		console.error('Failed to fetch user data:', error);
		return {
			user: null,
			isAuthenticated: false
		};
	}
};
