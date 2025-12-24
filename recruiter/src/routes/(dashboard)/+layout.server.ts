/**
 * Dashboard Layout Server Load
 * Fetches user data on every page load (including reloads)
 * Uses JWT from HttpOnly cookies to authenticate with Django API
 */

import type { LayoutServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { getApiBaseUrl } from '$lib/config/env';

export const load: LayoutServerLoad = async ({ cookies, fetch }) => {
	// Check if user has auth cookies
	const accessToken = cookies.get('access_token');
	const refreshToken = cookies.get('refresh_token');

	// If no tokens, redirect to login (should be caught by hooks, but double-check)
	if (!accessToken && !refreshToken) {
		throw redirect(302, '/login/');
	}

	try {
		// Fetch current user from Django API
		// The apiHandler in hooks.server.ts will automatically add the Authorization header
		// Using event.fetch here ensures the enhanced fetch from hooks is used
		const response = await fetch(`${getApiBaseUrl()}/recruiter/auth/me/`);

		if (!response.ok) {
			throw new Error(`API request failed: ${response.status}`);
		}

		const user = await response.json();

		return {
			user
		};
	} catch (error) {
		console.error('Failed to load user:', error);

		// If API call fails (e.g., invalid/expired token), clear cookies and redirect to login
		cookies.delete('access_token', { path: '/' });
		cookies.delete('refresh_token', { path: '/' });

		throw redirect(302, '/login/');
	}
};
