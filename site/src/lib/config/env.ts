/**
 * Environment Configuration
 * Centralized access to environment variables
 *
 * SvelteKit exposes environment variables through $env module.
 * Variables must be prefixed with PUBLIC_ to be accessible in client-side code.
 */

import { PUBLIC_API_BASE_URL, PUBLIC_SITE_URL, PUBLIC_RECRUITER_URL } from '$env/static/public';

/**
 * API Base URL for backend requests
 * Default: http://localhost:8000/api/v1
 */
export const API_BASE_URL = PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Site URL for frontend
 * Default: http://localhost:5173
 */
export const SITE_URL = PUBLIC_SITE_URL || 'http://localhost:5173';

/**
 * Recruiter Site URL for recruiter portal
 * Default: http://localhost:5174
 */
export const RECRUITER_URL = PUBLIC_RECRUITER_URL || 'http://localhost:5174';

/**
 * Check if we're running in development mode
 */
export const isDevelopment = import.meta.env.DEV;

/**
 * Check if we're running in production mode
 */
export const isProduction = import.meta.env.PROD;

/**
 * Base path for browser API calls.
 *
 * The browser never talks to Django directly any more — it calls this app's
 * own `/api/...` routes (src/routes/api), which read the HttpOnly cookie and
 * forward with a Bearer header. Same origin, so the cookie is first-party and
 * Django needs no CORS.
 */
export function getApiBasePath(): string {
  return '/api';
}

/**
 * Get the full API URL (with host)
 * This is used for server-side API calls
 */
export function getApiBaseUrl(): string {
  return API_BASE_URL;
}
