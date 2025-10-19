/**
 * Authentication API
 * Google OAuth and JWT token management
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

export interface TokenResponse {
	access: string;
	refresh: string;
	user: User;
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
 */
export async function googleAuthCallback(
	code: string,
	redirectUri: string
): Promise<TokenResponse> {
	return ApiClient.post<TokenResponse>('/auth/google/callback/', {
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
 * Refresh access token using refresh token
 */
export async function refreshAccessToken(refreshToken: string): Promise<{ access: string; refresh: string }> {
	return ApiClient.post<{ access: string; refresh: string }>('/auth/token/refresh/', {
		refresh: refreshToken
	});
}

/**
 * Logout - blacklist refresh token
 */
export async function logout(refreshToken: string): Promise<void> {
	await ApiClient.post('/auth/logout/', {
		refresh: refreshToken
	}, true); // Skip auth - uses refresh token in body
}

/**
 * Disconnect Google account
 */
export async function disconnectGoogle(): Promise<void> {
	await ApiClient.post('/auth/google/disconnect/', {});
}
