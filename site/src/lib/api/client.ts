/**
 * Browser API client for PUBLIC Django endpoints only.
 *
 * Authenticated requests no longer belong here: the JWT lives in an HttpOnly
 * cookie that JavaScript cannot read, so anything needing a token must go
 * through a `+page.server.ts` load or form action and `$lib/server/api.ts`.
 *
 * Calling a protected endpoint through this client will 401.
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

export class ApiClient {
	/** Make an unauthenticated request to a public endpoint. */
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

		const response = await fetch(url, {
			...options,
			headers
		});

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
