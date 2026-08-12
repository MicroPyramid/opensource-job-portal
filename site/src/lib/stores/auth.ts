/**
 * Authentication state.
 *
 * Derived from the server-loaded page data — the JWT lives in an HttpOnly
 * cookie that JavaScript cannot read, so there is nothing to keep in sync on
 * the client. `(site)/+layout.server.ts` resolves the user on every request.
 *
 * To change auth state, hit a server action (`/logout`, the OAuth callback)
 * and let the resulting invalidation flow back through here.
 */

import { derived } from 'svelte/store';
import { page } from '$app/stores';
import type { User } from '$lib/types/auth';

export interface AuthState {
	user: User | null;
	isAuthenticated: boolean;
	/** Kept so existing components compile; SSR means auth is never pending. */
	isLoading: boolean;
}

export const authStore = derived<typeof page, AuthState>(page, ($page) => ({
	user: ($page.data?.user as User | null) ?? null,
	isAuthenticated: Boolean($page.data?.isAuthenticated),
	isLoading: false
}));
