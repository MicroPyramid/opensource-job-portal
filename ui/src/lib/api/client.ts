/**
 * Base API Client for PeelJobs
 * Handles all HTTP requests to Django backend
 */

const API_BASE = '/api/v1';

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
	 * Make authenticated request with JWT token
	 */
	private static async request<T>(
		endpoint: string,
		options: RequestInit = {},
		skipAuth = false,
		isFormData = false,
		retryCount = 0
	): Promise<T> {
		const url = `${API_BASE}${endpoint}`;

		const headers = new Headers(options.headers ?? undefined);

		// Only set Content-Type for JSON, let browser set it for FormData
		if (!isFormData && !headers.has('Content-Type')) {
			headers.set('Content-Type', 'application/json');
		}

		// Add auth token if available (skip for public endpoints)
		if (!skipAuth && typeof window !== 'undefined') {
			const token = localStorage.getItem('access_token');
			if (token) {
				headers.set('Authorization', `Bearer ${token}`);
			}
		}

		const response = await fetch(url, {
			...options,
			headers
		});

		// Handle 401 Unauthorized - try to refresh token
		if (response.status === 401 && !skipAuth && retryCount === 0) {
			const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null;

			if (refreshToken) {
				try {
					if (!isRefreshing) {
						isRefreshing = true;

						// Try to refresh the token
						const refreshResponse = await fetch(`${API_BASE}/auth/token/refresh/`, {
							method: 'POST',
							headers: { 'Content-Type': 'application/json' },
							body: JSON.stringify({ refresh: refreshToken })
						});

						if (refreshResponse.ok) {
							const { access, refresh } = await refreshResponse.json();

							// Update localStorage
							if (typeof window !== 'undefined') {
								localStorage.setItem('access_token', access);
								localStorage.setItem('refresh_token', refresh);
							}

							isRefreshing = false;
							onTokenRefreshed(access);

							// Retry the original request with new token
							return this.request<T>(endpoint, options, skipAuth, isFormData, 1);
						} else {
							// Refresh failed, clear auth and redirect to login
							isRefreshing = false;
							if (typeof window !== 'undefined') {
								localStorage.removeItem('user');
								localStorage.removeItem('access_token');
								localStorage.removeItem('refresh_token');
								window.location.href = '/login';
							}
							throw new Error('Session expired. Please login again.');
						}
					} else {
						// Wait for the ongoing refresh to complete
						return new Promise((resolve, reject) => {
							subscribeTokenRefresh((token: string) => {
								// Retry request with new token
								this.request<T>(endpoint, options, skipAuth, isFormData, 1)
									.then(resolve)
									.catch(reject);
							});
						});
					}
				} catch (error) {
					isRefreshing = false;
					throw error;
				}
			} else {
				// No refresh token, clear everything and redirect to login
				if (typeof window !== 'undefined') {
					localStorage.removeItem('user');
					localStorage.removeItem('access_token');
					localStorage.removeItem('refresh_token');
					window.location.href = '/login';
				}
				throw new Error('Session expired. Please login again.');
			}
		}

		// Handle other errors
		if (!response.ok) {
			const error: ApiError = await response.json().catch(() => ({
				error: 'Request failed',
				detail: response.statusText
			}));

			// If there are field-specific errors, include them in the message
			const errorData = error as any;
			if (errorData && typeof errorData === 'object' && !errorData.error && !errorData.detail) {
				// DRF validation errors format: { field_name: ["error message"] }
				const fieldErrors = Object.entries(errorData)
					.map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
					.join('; ');
				throw new Error(fieldErrors || 'Validation failed');
			}

			throw new Error(error.error || error.detail || 'Request failed');
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
