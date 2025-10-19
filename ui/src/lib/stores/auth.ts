/**
 * Authentication Store
 * Manages user authentication state across the app
 */

import { writable } from 'svelte/store';
import { goto } from '$app/navigation';
import type { User } from '$lib/api/auth';
import { logout as apiLogout, refreshAccessToken } from '$lib/api/auth';

interface AuthState {
	user: User | null;
	accessToken: string | null;
	refreshToken: string | null;
	isAuthenticated: boolean;
	isLoading: boolean;
}

function createAuthStore() {
	// Initialize from localStorage if available
	const initialState: AuthState = {
		user: null,
		accessToken: null,
		refreshToken: null,
		isAuthenticated: false,
		isLoading: true
	};

	const { subscribe, set, update } = writable<AuthState>(initialState);

	// Load from localStorage on client side
	if (typeof window !== 'undefined') {
		const storedUser = localStorage.getItem('user');
		const storedAccessToken = localStorage.getItem('access_token');
		const storedRefreshToken = localStorage.getItem('refresh_token');

		if (storedUser && storedAccessToken && storedRefreshToken) {
			set({
				user: JSON.parse(storedUser),
				accessToken: storedAccessToken,
				refreshToken: storedRefreshToken,
				isAuthenticated: true,
				isLoading: false
			});
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
			// Store in localStorage
			if (typeof window !== 'undefined') {
				localStorage.setItem('user', JSON.stringify(user));
				localStorage.setItem('access_token', accessToken);
				localStorage.setItem('refresh_token', refreshToken);
			}

			// Update store
			set({
				user,
				accessToken,
				refreshToken,
				isAuthenticated: true,
				isLoading: false
			});
		},

		/**
		 * Logout and clear all data
		 */
		logout: async () => {
			// Get refresh token before clearing
			const currentState = { ...initialState };
			update(state => {
				currentState.refreshToken = state.refreshToken;
				return state;
			});

			// Call API to blacklist token
			if (currentState.refreshToken) {
				try {
					await apiLogout(currentState.refreshToken);
				} catch (error) {
					console.error('Logout API error:', error);
				}
			}

			// Clear localStorage
			if (typeof window !== 'undefined') {
				localStorage.removeItem('user');
				localStorage.removeItem('access_token');
				localStorage.removeItem('refresh_token');
			}

			// Reset store
			set({
				user: null,
				accessToken: null,
				refreshToken: null,
				isAuthenticated: false,
				isLoading: false
			});

			// Redirect to login
			goto('/login');
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
		 * Refresh access token
		 */
		refreshToken: async () => {
			let currentRefreshToken: string | null = null;

			update(state => {
				currentRefreshToken = state.refreshToken;
				return state;
			});

			if (!currentRefreshToken) {
				throw new Error('No refresh token available');
			}

			try {
				const { access, refresh } = await refreshAccessToken(currentRefreshToken);

				// Update tokens
				if (typeof window !== 'undefined') {
					localStorage.setItem('access_token', access);
					localStorage.setItem('refresh_token', refresh);
				}

				update(state => ({
					...state,
					accessToken: access,
					refreshToken: refresh
				}));

				return access;
			} catch (error) {
				// Refresh failed, logout user
				console.error('Token refresh failed:', error);
				authStore.logout();
				throw error;
			}
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
