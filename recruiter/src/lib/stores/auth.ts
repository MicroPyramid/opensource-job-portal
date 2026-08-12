/**
 * Authentication state for the recruiter dashboard.
 *
 * Derived from server-loaded page data. The previous version mirrored the user
 * in localStorage and set `isAuthenticated` purely from that key's presence —
 * so anything that could write localStorage could render the dashboard shell
 * as signed-in, and a stale entry survived the session it belonged to.
 *
 * `(dashboard)/+layout.server.ts` resolves the user from the HttpOnly cookie on
 * every request, which is the only source of truth. To change auth state, hit a
 * server action (`/logout`) and let the invalidation flow back through here.
 */

import { derived } from 'svelte/store';
import { page } from '$app/stores';
import type { User } from '$lib/types';

export interface AuthState {
	user: User | null;
	isAuthenticated: boolean;
	/** Kept so existing components compile; SSR means auth is never pending. */
	isLoading: boolean;
}

export const authStore = derived<typeof page, AuthState>(page, ($page) => {
	const user = ($page.data?.user as User | null) ?? null;

	return {
		user,
		isAuthenticated: Boolean(user),
		isLoading: false
	};
});
