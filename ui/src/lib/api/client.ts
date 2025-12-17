/**
 * Base API Client for PeelJobs
 * Handles all HTTP requests to Django backend
 *
 * SECURITY: This client uses HttpOnly cookies for authentication
 * - JWT tokens are stored in HttpOnly cookies (NOT localStorage)
 * - Cookies are automatically sent with every request (credentials: 'include')
 * - Tokens are never accessible to JavaScript (XSS protection)
 */

import { getApiBasePath, getApiBaseUrl } from '$lib/config/env';
import { browser } from '$app/environment';
import { formatApiError } from '$lib/utils/error-formatter';

// Use full URL for server-side, proxy path for client-side
const getApiBase = () => browser ? getApiBasePath() : getApiBaseUrl();

export interface ApiError {
	error: string;
	detail?: string;
}

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function subscribeTokenRefresh(callback: (token: string) => void) {
	refreshSubscribers.push(callback);
}

function onTokenRefreshed(token: string) {
	refreshSubscribers.forEach(callback => callback(token));
	refreshSubscribers = [];
}

export class ApiClient {
	/**
	 * Make authenticated request with JWT token from HttpOnly cookies
	 */
	private static async request<T>(
		endpoint: string,
		options: RequestInit = {},
		skipAuth = false,
		isFormData = false,
		retryCount = 0
	): Promise<T> {
		const url = `${getApiBase()}${endpoint}`;

		const headers = new Headers(options.headers ?? undefined);

		// Only set Content-Type for JSON, let browser set it for FormData
		if (!isFormData && !headers.has('Content-Type')) {
			headers.set('Content-Type', 'application/json');
		}

		// NOTE: We no longer add Authorization header - tokens are in HttpOnly cookies
		// The browser automatically sends cookies with credentials: 'include'

		const response = await fetch(url, {
			...options,
			headers,
			credentials: 'include'  // Send HttpOnly cookies with request
		});

		// Handle 401 Unauthorized - try to refresh token
		if (response.status === 401 && !skipAuth && retryCount === 0) {
			try {
				if (!isRefreshing) {
					isRefreshing = true;

					// Try to refresh the token (cookies sent automatically)
					const refreshResponse = await fetch(`${getApiBase()}/auth/token/refresh/`, {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						credentials: 'include'  // Send refresh token cookie
					});

					if (refreshResponse.ok) {
						// New tokens are set in HttpOnly cookies by the server
						isRefreshing = false;
						onTokenRefreshed('refreshed');

						// Retry the original request with new token from cookie
						return this.request<T>(endpoint, options, skipAuth, isFormData, 1);
					} else {
						// Refresh failed, clear auth and redirect to login
						isRefreshing = false;
						if (typeof window !== 'undefined') {
							localStorage.removeItem('user');  // Clear user data
							window.location.href = '/login';
						}
						throw new Error('Session expired. Please login again.');
					}
				} else {
					// Wait for the ongoing refresh to complete
					return new Promise((resolve, reject) => {
						subscribeTokenRefresh(() => {
							// Retry request with new token from cookie
							this.request<T>(endpoint, options, skipAuth, isFormData, 1)
								.then(resolve)
								.catch(reject);
						});
					});
				}
			} catch (error) {
				isRefreshing = false;
				// Clear user data and redirect to login
				if (typeof window !== 'undefined') {
					localStorage.removeItem('user');
					window.location.href = '/login';
				}
				throw error;
			}
		}

		// Handle other errors
		if (!response.ok) {
			const errorData = await response.json().catch(() => ({
				error: 'Request failed',
				detail: response.statusText
			}));

			// Format error using centralized error formatter
			const errorMessage = formatApiError(errorData);
			throw new Error(errorMessage);
		}

		return response.json();
	}

	static get<T>(
		endpoint: string,
		paramsOrSkipAuth?: Record<string, any> | boolean,
		skipAuth = false
	): Promise<T> {
		let params: Record<string, any> | undefined;

		if (typeof paramsOrSkipAuth === 'boolean') {
			skipAuth = paramsOrSkipAuth;
		} else if (paramsOrSkipAuth) {
			params = paramsOrSkipAuth;
		}

		// Build query string from params
		let url = endpoint;
		if (params) {
			const queryString = new URLSearchParams(
				Object.entries(params)
					.filter(([_, value]) => value !== undefined && value !== null)
					.map(([key, value]) => [key, String(value)])
			).toString();
			if (queryString) {
				url = `${endpoint}?${queryString}`;
			}
		}
		return this.request<T>(url, { method: 'GET' }, skipAuth);
	}

	static post<T>(endpoint: string, data?: unknown, skipAuth = false): Promise<T> {
		return this.request<T>(endpoint, {
			method: 'POST',
			body: data ? JSON.stringify(data) : undefined
		}, skipAuth);
	}

	static put<T>(endpoint: string, data?: unknown): Promise<T> {
		return this.request<T>(endpoint, {
			method: 'PUT',
			body: data ? JSON.stringify(data) : undefined
		});
	}

	static patch<T>(endpoint: string, data?: unknown): Promise<T> {
		return this.request<T>(endpoint, {
			method: 'PATCH',
			body: data ? JSON.stringify(data) : undefined
		});
	}

	static delete<T>(endpoint: string): Promise<T> {
		return this.request<T>(endpoint, { method: 'DELETE' });
	}

	/**
	 * POST request with FormData (for file uploads)
	 */
	static postFormData<T>(endpoint: string, formData: FormData, skipAuth = false): Promise<T> {
		return this.request<T>(
			endpoint,
			{
				method: 'POST',
				body: formData
			},
			skipAuth,
			true // isFormData flag
		);
	}
}

// Export singleton instance for convenience
export const apiClient = ApiClient;
