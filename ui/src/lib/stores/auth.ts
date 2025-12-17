/**
 * Authentication Store
 * Manages user authentication state across the app
 *
 * SECURITY NOTE:
 * - JWT tokens are stored in HttpOnly cookies (NOT accessible to JavaScript)
 * - Only user profile data is stored in localStorage (non-sensitive)
 * - This protects against XSS attacks stealing authentication tokens
 */

import { writable } from 'svelte/store';
import { goto } from '$app/navigation';
import type { User } from '$lib/api/auth';
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
		const storedUser = localStorage.getItem('user');

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
				localStorage.removeItem('user');
				update(state => ({ ...state, isLoading: false }));
			}
		} else {
			update(state => ({ ...state, isLoading: false }));
		}
	}

	return {
		subscribe,

		/**
		 * Login with user data
		 * NOTE: Tokens are set by the server in HttpOnly cookies
		 */
		login: (user: User) => {
			// Store only user data in localStorage (non-sensitive)
			if (typeof window !== 'undefined') {
				localStorage.setItem('user', JSON.stringify(user));
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
		 * NOTE: API call will clear HttpOnly cookies on the server
		 */
		logout: async () => {
			// Call API to blacklist token and clear cookies
			try {
				await apiLogout();
			} catch (error) {
				console.error('Logout API error:', error);
			}

			// Clear localStorage (user data only)
			if (typeof window !== 'undefined') {
				localStorage.removeItem('user');
			}

			// Reset store
			set({
				user: null,
				isAuthenticated: false,
				isLoading: false
			});

			// Redirect to home page
			goto('/');
		},

		/**
		 * Update user data
		 */
		updateUser: (user: User) => {
			if (typeof window !== 'undefined') {
				localStorage.setItem('user', JSON.stringify(user));
			}

			update(state => ({
				...state,
				user
			}));
		},

		/**
		 * Check if user is authenticated
		 */
		checkAuth: () => {
			update(state => ({ ...state, isLoading: false }));
		}
	};
}

export const authStore = createAuthStore();
