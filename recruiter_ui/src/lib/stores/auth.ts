/**
 * Authentication Store for Recruiters
 * Manages user authentication state across the app
 *
 * SECURITY NOTE:
 * - JWT tokens are stored in HttpOnly cookies (NOT accessible to JavaScript)
 * - Only user profile data is stored in localStorage (non-sensitive)
 * - This protects against XSS attacks stealing authentication tokens
 */

import { writable } from 'svelte/store';
import { goto } from '$app/navigation';
import type { User } from '$lib/types';
import { logout as apiLogout } from '$lib/api/auth';

interface AuthState {
	user: User | null;
	isAuthenticated: boolean;
	isLoading: boolean;
}

function createAuthStore() {
	// Initialize from localStorage if available
	const initialState: AuthState = {
		user: null,
		isAuthenticated: false,
		isLoading: true
	};

	const { subscribe, set, update } = writable<AuthState>(initialState);

	// Load user data from localStorage on client side
	// NOTE: Tokens are in HttpOnly cookies, not accessible to JavaScript
	if (typeof window !== 'undefined') {
		const storedUser = localStorage.getItem('recruiter_user');

		if (storedUser) {
			try {
				set({
					user: JSON.parse(storedUser),
					isAuthenticated: true,
					isLoading: false
				});
			} catch (error) {
				// Invalid stored data, clear everything
				console.error('Error parsing stored user data:', error);
				localStorage.removeItem('recruiter_user');
				update((state) => ({ ...state, isLoading: false }));
			}
		} else {
			update((state) => ({ ...state, isLoading: false }));
		}
	}

	return {
		subscribe,

		/**
		 * Login with user data and JWT tokens
		 * Tokens are stored in HttpOnly cookies via SvelteKit server endpoint
		 */
		login: async (user: User, access?: string, refresh?: string) => {
			// Store only user data in localStorage (non-sensitive)
			if (typeof window !== 'undefined') {
				localStorage.setItem('recruiter_user', JSON.stringify(user));

				// Store tokens in HttpOnly cookies via server endpoint
				if (access && refresh) {
					try {
						await fetch('/api/auth/set-cookies', {
							method: 'POST',
							headers: { 'Content-Type': 'application/json' },
							body: JSON.stringify({ access, refresh })
						});
					} catch (err) {
						console.error('Failed to set auth cookies:', err);
					}
				}
			}

			// Update store
			set({
				user,
				isAuthenticated: true,
				isLoading: false
			});
		},

		/**
		 * Logout and clear all data
		 * Clears HttpOnly cookies via SvelteKit server endpoint
		 */
		logout: async () => {
			// Clear localStorage
			if (typeof window !== 'undefined') {
				localStorage.removeItem('recruiter_user');
			}

			// Reset store
			set({
				user: null,
				isAuthenticated: false,
				isLoading: false
			});

			// Clear HttpOnly cookies via SvelteKit server endpoint
			if (typeof window !== 'undefined') {
				try {
					await fetch('/api/auth/clear-cookies', {
						method: 'POST'
					});
				} catch (error) {
					console.log('Failed to clear cookies:', error);
				}
			}

			// Optionally call Django logout endpoint (for token blacklisting, etc.)
			try {
				await apiLogout();
			} catch (error) {
				console.log('Logout API call failed:', error);
			}

			// Redirect to login page
			goto('/login');
		},

		/**
		 * Update user data
		 */
		updateUser: (user: User) => {
			if (typeof window !== 'undefined') {
				localStorage.setItem('recruiter_user', JSON.stringify(user));
			}

			update((state) => ({
				...state,
				user
			}));
		},

		/**
		 * Check if user is authenticated
		 */
		checkAuth: () => {
			update((state) => ({ ...state, isLoading: false }));
		},

		/**
		 * Clear authentication state (for errors)
		 */
		clearAuth: () => {
			if (typeof window !== 'undefined') {
				localStorage.removeItem('recruiter_user');
			}

			set({
				user: null,
				isAuthenticated: false,
				isLoading: false
			});
		}
	};
}

export const authStore = createAuthStore();
