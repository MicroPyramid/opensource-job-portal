/**
 * Authentication Store
 * Manages user authentication state across the app
 *
 * JWT tokens are stored in localStorage for cross-platform compatibility (web + mobile)
 * Tokens are sent via Authorization header with each API request
 */

import { writable } from 'svelte/store';
import { goto } from '$app/navigation';
import type { User } from '$lib/api/auth';
import { logout as apiLogout } from '$lib/api/auth';
import {
	getAccessToken,
	setTokens,
	clearTokens
} from '$lib/utils/token-storage';

// Re-export for convenience
export { getAccessToken, getRefreshToken, setTokens, clearTokens } from '$lib/utils/token-storage';

interface AuthState {
	user: User | null;
	isAuthenticated: boolean;
	isLoading: boolean;
}

const USER_KEY = 'user';

function createAuthStore() {
	// Initialize from localStorage if available
	const initialState: AuthState = {
		user: null,
		isAuthenticated: false,
		isLoading: true
	};

	const { subscribe, set, update } = writable<AuthState>(initialState);

	// Load user data from localStorage on client side
	if (typeof window !== 'undefined') {
		const storedUser = localStorage.getItem(USER_KEY);
		const accessToken = getAccessToken();

		if (storedUser && accessToken) {
			try {
				set({
					user: JSON.parse(storedUser),
					isAuthenticated: true,
					isLoading: false
				});
			} catch (error) {
				// Invalid stored data, clear everything
				console.error('Error parsing stored user data:', error);
				localStorage.removeItem(USER_KEY);
				clearTokens();
				update(state => ({ ...state, isLoading: false }));
			}
		} else {
			update(state => ({ ...state, isLoading: false }));
		}
	}

	return {
		subscribe,

		/**
		 * Login with user data and tokens
		 */
		login: (user: User, accessToken: string, refreshToken: string) => {
			if (typeof window !== 'undefined') {
				// Store tokens
				setTokens(accessToken, refreshToken);
				// Store user data
				localStorage.setItem(USER_KEY, JSON.stringify(user));
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
		 */
		logout: async () => {
			// Call API to blacklist token
			try {
				await apiLogout();
			} catch (error) {
				console.error('Logout API error:', error);
			}

			// Clear localStorage
			if (typeof window !== 'undefined') {
				localStorage.removeItem(USER_KEY);
				clearTokens();
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
				localStorage.setItem(USER_KEY, JSON.stringify(user));
			}

			update(state => ({
				...state,
				user
			}));
		},

		/**
		 * Update access token (after refresh)
		 */
		updateAccessToken: (accessToken: string) => {
			if (typeof window !== 'undefined') {
				localStorage.setItem('access_token', accessToken);
			}
		},

		/**
		 * Check if user is authenticated
		 */
		checkAuth: () => {
			update(state => ({ ...state, isLoading: false }));
		},

		/**
		 * Clear auth state (used when token refresh fails)
		 */
		clearAuth: () => {
			if (typeof window !== 'undefined') {
				localStorage.removeItem(USER_KEY);
				clearTokens();
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
