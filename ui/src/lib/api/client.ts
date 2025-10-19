/**
 * Base API Client for PeelJobs
 * Handles all HTTP requests to Django backend
 */

const API_BASE = '/api/v1';

export interface ApiError {
	error: string;
	detail?: string;
}

export class ApiClient {
	/**
	 * Make authenticated request with JWT token
	 */
	private static async request<T>(
		endpoint: string,
		options: RequestInit = {},
		skipAuth = false
	): Promise<T> {
		const url = `${API_BASE}${endpoint}`;

		const headers: HeadersInit = {
			'Content-Type': 'application/json',
			...options.headers
		};

		// Add auth token if available (skip for public endpoints)
		if (!skipAuth && typeof window !== 'undefined') {
			const token = localStorage.getItem('access_token');
			if (token) {
				headers['Authorization'] = `Bearer ${token}`;
			}
		}

		const response = await fetch(url, {
			...options,
			headers
		});

		// Handle errors
		if (!response.ok) {
			const error: ApiError = await response.json().catch(() => ({
				error: 'Request failed',
				detail: response.statusText
			}));
			throw new Error(error.error || error.detail || 'Request failed');
		}

		return response.json();
	}

	static get<T>(endpoint: string, skipAuth = false): Promise<T> {
		return this.request<T>(endpoint, { method: 'GET' }, skipAuth);
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

	static delete<T>(endpoint: string): Promise<T> {
		return this.request<T>(endpoint, { method: 'DELETE' });
	}
}
