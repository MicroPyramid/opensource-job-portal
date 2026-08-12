/**
 * Authentication types.
 *
 * These used to live in `$lib/api/auth.ts` alongside browser-side OAuth calls.
 * Those calls moved to server loads (`routes/login`, `routes/auth/google/
 * callback`), so only the shapes remain and they belong with the other types.
 */

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

/** Body returned by the Django Google OAuth callback. */
export interface AuthResponse {
	user: User;
	access: string;
	refresh: string;
	requires_profile_completion: boolean;
	redirect_to: string;
	is_new_user: boolean;
}
