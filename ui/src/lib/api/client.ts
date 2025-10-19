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
		skipAuth = false,
		isFormData = false
	): Promise<T> {
		const url = `${API_BASE}${endpoint}`;

		const headers: HeadersInit = {
			// Only set Content-Type for JSON, let browser set it for FormData
			...(isFormData ? {} : { 'Content-Type': 'application/json' }),
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

	static get<T>(endpoint: string, params?: Record<string, any>, skipAuth = false): Promise<T> {
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
