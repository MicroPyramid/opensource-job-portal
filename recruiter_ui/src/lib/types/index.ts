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

// ===== Job Management Types =====

export type JobStatus = 'Draft' | 'Live' | 'Disabled' | 'Expired' | 'Pending' | 'Published' | 'Hired' | 'Process';
export type JobType = 'full-time' | 'internship' | 'walk-in' | 'government' | 'Fresher';
export type WorkMode = 'in-office' | 'remote' | 'hybrid';
export type SalaryType = 'Month' | 'Year';

export interface Location {
	id: number;
	name: string;
	slug: string;
	state?: string;
	state_slug?: string;
}

export interface Skill {
	id: number;
	name: string;
	slug: string;
}

export interface Industry {
	id: number;
	name: string;
	slug: string;
}

export interface Qualification {
	id: number;
	name: string;
	slug: string;
}

export interface FunctionalArea {
	id: number;
	name: string;
}

export interface JobListItem {
	id: number;
	title: string;
	slug: string;
	company_name: string;
	job_type: JobType;
	work_mode: WorkMode;
	status: JobStatus;
	location_display: string;
	applicants_count: number;
	views_count: number;
	vacancies: number;
	created_on: string;
	published_on?: string;
	last_date?: string;
	time_ago: string;
	days_until_expiry?: number;
	is_expiring_soon: boolean;
}

export interface JobDetail extends JobListItem {
	description: string;
	job_role: string;
	locations: Location[];
	skills: Skill[];
	industries: Industry[];
	qualifications: Qualification[];
	functional_areas: FunctionalArea[];
	min_salary: number;
	max_salary: number;
	salary_type: SalaryType;
	min_year: number;
	max_year: number;
	min_month: number;
	max_month: number;
	fresher: boolean;
	company_description?: string;
	company_address?: string;
	company_links?: string;
	company_emails?: string;
	// Walk-in fields
	walkin_contactinfo?: string;
	walkin_show_contact_info?: boolean;
	walkin_from_date?: string;
	walkin_to_date?: string;
	walkin_time?: string;
	// Government job fields
	govt_job_type?: string;
	application_fee?: string;
	selection_process?: string;
	how_to_apply?: string;
	important_dates?: string;
	govt_from_date?: string;
	govt_to_date?: string;
	govt_exam_date?: string;
	age_relaxation?: string;
}

export interface JobCreateData {
	title: string;
	job_role: string;
	description: string;
	company_name: string;
	job_type: JobType;
	work_mode?: WorkMode;
	location_ids?: number[];
	skill_ids?: number[];
	industry_ids?: number[];
	qualification_ids?: number[];
	functional_area_ids?: number[];
	min_salary?: number;
	max_salary?: number;
	salary_type?: SalaryType;
	min_year?: number;
	max_year?: number;
	min_month?: number;
	max_month?: number;
	fresher?: boolean;
	vacancies?: number;
	last_date?: string;
	company_description?: string;
	company_address?: string;
	company_links?: string;
	company_emails?: string;
	// Walk-in fields
	walkin_contactinfo?: string;
	walkin_show_contact_info?: boolean;
	walkin_from_date?: string;
	walkin_to_date?: string;
	walkin_time?: string;
	// Government job fields
	govt_job_type?: string;
	application_fee?: string;
	selection_process?: string;
	how_to_apply?: string;
	important_dates?: string;
	govt_from_date?: string;
	govt_to_date?: string;
	govt_exam_date?: string;
	age_relaxation?: string;
}

export interface JobUpdateData extends Partial<JobCreateData> {}

export interface JobsListResponse {
	count: number;
	next?: string;
	previous?: string;
	results: JobListItem[];
}

export interface JobApplicant {
	id: number;
	name: string;
	email: string;
	profile_pic?: string;
}

export interface JobApplication {
	id: number;
	applicant: JobApplicant;
	status: 'Pending' | 'Shortlisted' | 'Selected' | 'Rejected';
	applied_on: string;
	applied_time_ago: string;
}

export interface JobApplicantsResponse {
	job: {
		id: number;
		title: string;
		status: JobStatus;
	};
	applications: JobApplication[];
	total_applicants: number;
	stats: {
		pending: number;
		shortlisted: number;
		selected: number;
		rejected: number;
	};
}

export interface DashboardStats {
	total_jobs: number;
	live_jobs: number;
	draft_jobs: number;
	closed_jobs: number;
	expired_jobs: number;
	total_applicants: number;
	total_views: number;
}

export interface DashboardStatsResponse {
	stats: DashboardStats;
	recent_jobs: JobListItem[];
}

export interface JobFilters {
	status?: JobStatus;
	search?: string;
	ordering?: string;
	page?: number;
	page_size?: number;
}

// ===== Job Form Metadata Types =====

export interface Country {
	id: number;
	name: string;
	slug: string;
}

export interface State {
	id: number;
	name: string;
	slug: string;
	country_id: number;
}

export interface City {
	id: number;
	name: string;
	slug: string;
	state?: {
		id: number;
		name: string;
	};
}

export interface JobFormMetadata {
	countries: Country[];
	states: State[];
	cities: City[];
	skills: Skill[];
	industries: Industry[];
	qualifications: Qualification[];
	functional_areas: FunctionalArea[];
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
