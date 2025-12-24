/**
 * Server-side layout loader for (site) routes
 *
 * Note: JWT tokens are stored in localStorage (client-side only)
 * Auth state is managed by the client-side authStore
 * This file just returns empty data for SSR compatibility
 */

import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async () => {
	// Auth is handled client-side via localStorage tokens
	// Return null for SSR, client will hydrate with actual auth state
	return {
		user: null,
		isAuthenticated: false
	};
};
