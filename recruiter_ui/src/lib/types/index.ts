/**
 * Type Definitions for Recruiter UI
 */

// ===== User & Company Types =====

export interface Company {
	id: number;
	name: string;
	slug: string;
	logo?: string;
	profile_pic?: string;
	website?: string;
	size?: string;
	industry?: string;
	profile?: string;
}

export interface User {
	id: number;
	email: string;
	first_name: string;
	last_name: string;
	username: string;
	user_type: 'EM' | 'JS';
	is_active: boolean;
	email_verified: boolean;
	company: Company | null;
	is_admin: boolean;
	job_title: string;
	mobile?: string;
	profile_pic?: string;
	date_joined: string;
	last_login?: string;
	permissions: UserPermissions;
}

export interface UserPermissions {
	can_post_jobs: boolean;
	can_manage_team: boolean;
	can_edit_company: boolean;
	is_company_admin: boolean;
	is_company_member: boolean;
	is_independent_recruiter: boolean;
}

// ===== Authentication Types =====

export interface RegisterData {
	account_type: 'company' | 'recruiter';
	// Company fields (required if account_type='company')
	company_name?: string;
	company_website?: string;
	company_industry?: string;
	company_size?: '1-10' | '11-20' | '21-50' | '50-200' | '200+';
	// Personal fields
	first_name: string;
	last_name: string;
	email: string;
	phone?: string;
	job_title?: string;
	// Security
	password: string;
	confirm_password: string;
	agree_to_terms: boolean;
}

export interface LoginData {
	email: string;
	password: string;
	remember_me?: boolean;
}

export interface AuthResponse {
	access: string;
	refresh: string;
	user: User;
}

export interface GoogleAuthUrlResponse {
	auth_url: string;
	account_type: 'company' | 'recruiter';
}

export interface GoogleCallbackResponse {
	status: 'authenticated' | 'additional_info_required';
	access?: string;
	refresh?: string;
	user?: User;
	google_data?: {
		email: string;
		first_name: string;
		last_name: string;
		picture?: string;
	};
	session_token?: string;
}

export interface GoogleCompleteData {
	session_token: string;
	account_type: 'company' | 'recruiter';
	company_name?: string;
	company_website?: string;
	company_industry?: string;
	company_size?: string;
	phone?: string;
	job_title?: string;
	agree_to_terms: boolean;
}

export interface VerifyEmailData {
	token: string;
}

export interface ForgotPasswordData {
	email: string;
}

export interface ResetPasswordData {
	token: string;
	password: string;
	confirm_password: string;
}

export interface ChangePasswordData {
	old_password: string;
	new_password: string;
	confirm_password: string;
}

export interface AcceptInvitationData {
	token: string;
	first_name: string;
	last_name: string;
	password: string;
	confirm_password: string;
}

// ===== Team Management Types =====

export interface TeamMemberStats {
	jobs_posted: number;
	active_jobs: number;
	total_applicants: number;
}

export interface TeamMember {
	id: number;
	email: string;
	first_name: string;
	last_name: string;
	job_title: string;
	is_admin: boolean;
	date_joined: string;
	last_login?: string;
	stats: TeamMemberStats;
}

export interface TeamMemberDetail extends TeamMember {
	recent_jobs: RecentJob[];
}

export interface RecentJob {
	id: string;
	title: string;
	status: string;
	posted_date: string;
	applicants_count: number;
}

export interface TeamListResponse {
	company: Company;
	members: TeamMember[];
	total_members: number;
}

export interface TeamInvitation {
	id: number;
	email: string;
	role_title: string;
	status: 'pending' | 'accepted' | 'expired' | 'cancelled';
	invited_by_name: string;
	invited_by_email: string;
	created_at: string;
	expires_at: string;
	days_remaining: number;
}

export interface InvitationsListResponse {
	invitations: TeamInvitation[];
	total: number;
	pending_count: number;
	expired_count: number;
}

export interface SendInvitationData {
	email: string;
	job_title: string;
	message?: string;
}

export interface UpdateTeamMemberData {
	job_title?: string;
	is_admin?: boolean;
}

// ===== API Response Types =====

export interface ApiResponse<T = any> {
	success: boolean;
	message?: string;
	data?: T;
}

export interface ApiError {
	error: string;
	detail?: string;
	[field: string]: any; // For field-specific validation errors
}
