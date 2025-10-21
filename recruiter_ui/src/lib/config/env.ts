/**
 * Environment Configuration
 * Centralized access to environment variables
 *
 * SvelteKit exposes environment variables through $env module.
 * Variables must be prefixed with PUBLIC_ to be accessible in client-side code.
 */

import { PUBLIC_API_BASE_URL, PUBLIC_SITE_URL } from '$env/static/public';

/**
 * API Base URL for backend requests
 * Default: http://localhost:8000/api/v1
 */
export const API_BASE_URL = PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Site URL for frontend
 * Default: http://localhost:5174
 */
export const SITE_URL = PUBLIC_SITE_URL || 'http://localhost:5174';

/**
 * Check if we're running in development mode
 */
export const isDevelopment = import.meta.env.DEV;

/**
 * Check if we're running in production mode
 */
export const isProduction = import.meta.env.PROD;

/**
 * Get the API base path (path only, without host)
 * DEPRECATED: No longer using Vite proxy - always use full URL
 * @deprecated Use getApiBaseUrl() instead
 */
export function getApiBasePath(): string {
	// Always return full URL (no proxy)
	return API_BASE_URL;
}

/**
 * Get the full API URL (with host)
 * This is used for all API calls (both client and server)
 */
export function getApiBaseUrl(): string {
	return API_BASE_URL;
}
