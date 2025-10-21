/**
 * Authentication API for Recruiters
 * Handles registration, login, email verification, password reset, and Google OAuth
 *
 * SECURITY NOTE:
 * - Tokens are NOT returned in API responses
 * - Tokens are set by the server in HttpOnly cookies
 * - This protects against XSS attacks stealing authentication tokens
 */

import { ApiClient } from './client';
import type {
	User,
	RegisterData,
	LoginData,
	AuthResponse,
	GoogleAuthUrlResponse,
	GoogleCallbackResponse,
	GoogleCompleteData,
	VerifyEmailData,
	ForgotPasswordData,
	ResetPasswordData,
	ChangePasswordData,
	AcceptInvitationData,
	ApiResponse
} from '$lib/types';

// ===== Registration & Login =====

/**
 * Register new recruiter or company account
 */
export async function register(data: RegisterData): Promise<ApiResponse<{ user: User; company: any }>> {
	return ApiClient.post('/recruiter/auth/register/', data, true);
}

/**
 * Login with email and password
 * NOTE: Tokens are set by server in HttpOnly cookies
 */
export async function login(data: LoginData): Promise<AuthResponse> {
	return ApiClient.post('/recruiter/auth/login/', data, true);
}

/**
 * Logout - blacklist refresh token and clear HttpOnly cookies
 */
export async function logout(): Promise<ApiResponse> {
	return ApiClient.post('/recruiter/auth/logout/', {});
}

// ===== Email Verification =====

/**
 * Verify email address with token
 */
export async function verifyEmail(data: VerifyEmailData): Promise<AuthResponse> {
	return ApiClient.post('/recruiter/auth/verify-email/', data, true);
}

/**
 * Resend verification email
 */
export async function resendVerification(email: string): Promise<ApiResponse> {
	return ApiClient.post('/recruiter/auth/resend-verification/', { email }, true);
}

// ===== Password Management =====

/**
 * Request password reset email
 */
export async function forgotPassword(data: ForgotPasswordData): Promise<ApiResponse> {
	return ApiClient.post('/recruiter/auth/forgot-password/', data, true);
}

/**
 * Reset password with token
 */
export async function resetPassword(data: ResetPasswordData): Promise<ApiResponse> {
	return ApiClient.post('/recruiter/auth/reset-password/', data, true);
}

/**
 * Change password for authenticated user
 */
export async function changePassword(data: ChangePasswordData): Promise<ApiResponse> {
	return ApiClient.post('/recruiter/auth/change-password/', data);
}

// ===== Team Invitation =====

/**
 * Accept team invitation and create account
 */
export async function acceptInvitation(data: AcceptInvitationData): Promise<AuthResponse> {
	return ApiClient.post('/recruiter/auth/accept-invitation/', data, true);
}

// ===== User Info =====

/**
 * Get current authenticated user
 */
export async function getCurrentUser(): Promise<User> {
	return ApiClient.get('/recruiter/auth/me/');
}

// ===== Google OAuth =====

/**
 * Get Google OAuth URL for frontend to redirect to
 */
export async function getGoogleAuthUrl(
	redirectUri: string,
	accountType: 'company' | 'recruiter'
): Promise<GoogleAuthUrlResponse> {
	const endpoint = `/recruiter/auth/google/url/?redirect_uri=${encodeURIComponent(redirectUri)}&account_type=${accountType}`;
	return ApiClient.get<GoogleAuthUrlResponse>(endpoint, true);
}

/**
 * Exchange Google authorization code for JWT tokens
 * NOTE: Tokens are set by server in HttpOnly cookies
 */
export async function googleAuthCallback(
	code: string,
	redirectUri: string,
	accountType: 'company' | 'recruiter'
): Promise<GoogleCallbackResponse> {
	return ApiClient.post<GoogleCallbackResponse>(
		'/recruiter/auth/google/callback/',
		{
			code,
			redirect_uri: redirectUri,
			account_type: accountType
		},
		true
	);
}

/**
 * Complete Google OAuth registration with additional info
 */
export async function googleCompleteRegistration(data: GoogleCompleteData): Promise<AuthResponse> {
	return ApiClient.post<AuthResponse>('/recruiter/auth/google/complete/', data, true);
}
