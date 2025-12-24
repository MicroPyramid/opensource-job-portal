/**
 * Authentication API
 * Google OAuth and JWT token management
 *
 * JWT tokens are stored in localStorage for cross-platform compatibility (web + mobile)
 * Tokens are sent via Authorization header with each API request
 */

import { ApiClient } from './client';

// Types (will be replaced with auto-generated types later)
export interface User {
	id: number;
	email: string;
	username: string;
	first_name: string;
	last_name: string;
	user_type: string;
	profile_completion_percentage: number;
	is_gp_connected: boolean;
	photo?: string;
	profile_pic?: string;
	mobile?: string;
	gender?: string;
	is_active: boolean;
	date_joined: string;
}

export interface AuthResponse {
	user: User;
	access: string;
	refresh: string;
	requires_profile_completion: boolean;
	redirect_to: string;
	is_new_user: boolean;
}

export interface GoogleAuthUrlResponse {
	auth_url: string;
	user_type: string;
}

/**
 * Get Google OAuth URL for frontend to redirect to
 */
export async function getGoogleAuthUrl(redirectUri: string): Promise<GoogleAuthUrlResponse> {
	const endpoint = `/auth/google/url/?redirect_uri=${encodeURIComponent(redirectUri)}`;
	return ApiClient.get<GoogleAuthUrlResponse>(endpoint, true); // Skip auth - public endpoint
}

/**
 * Exchange Google authorization code for JWT tokens
 * Returns access and refresh tokens in response body
 */
export async function googleAuthCallback(
	code: string,
	redirectUri: string
): Promise<AuthResponse> {
	return ApiClient.post<AuthResponse>('/auth/google/callback/', {
		code,
		redirect_uri: redirectUri
	}, true); // Skip auth - public endpoint
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser(): Promise<User> {
	return ApiClient.get<User>('/auth/me/');
}

/**
 * Logout - blacklist refresh token
 */
export async function logout(): Promise<void> {
	const { getRefreshToken } = await import('$lib/utils/token-storage');
	const refreshToken = getRefreshToken();
	await ApiClient.post('/auth/logout/', { refresh: refreshToken });
}

/**
 * Disconnect Google account
 */
export async function disconnectGoogle(): Promise<void> {
	await ApiClient.post('/auth/google/disconnect/', {});
}
