/**
 * Type Definitions for Recruiter UI
 */

// ===== User & Company Types =====

/**
 * Company as embedded in /recruiter/auth/me/ and team responses.
 *
 * Verified against a live backend. The SvelteKit type also declared `logo`,
 * `industry` and `profile`: `logo` is really `logo_url` and only exists on the
 * full profile below, `industry` is never returned by any recruiter endpoint,
 * and `profile` likewise belongs to the full shape. Nothing read them off an API
 * response — the UI hits with those names are all local form state.
 */
export interface Company {
	id: number;
	name: string;
	slug: string;
	profile_pic?: string;
	website?: string;
	size?: string;
	company_type?: string;
}

/**
 * Full company record from /recruiter/company/profile/, which returns more than
 * the embedded shape above.
 */
export interface CompanyProfile extends Company {
	address?: string;
	profile?: string;
	phone_number?: string;
	email?: string | null;
	logo_url?: string;
	registered_date?: string;
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
	/** Returned by /recruiter/team/ but absent from the SvelteKit type. */
	profile_pic?: string | null;
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
export type JobType = 'full-time' | 'permanent' | 'contract' | 'internship' | 'part-time' | 'freelance' | 'walk-in' | 'government' | 'fresher';
export type WorkMode = 'in-office' | 'remote' | 'hybrid';
export type SalaryType = 'Month' | 'Year';
export type SeniorityLevel = 'intern' | 'junior' | 'mid' | 'senior' | 'lead' | 'manager';
export type ApplicationMethod = 'portal' | 'external' | 'email';
export type LanguageProficiency = 'basic' | 'conversational' | 'fluent';
export type HiringTimeline = '1-3days' | '1-2weeks' | '1month' | '1-3months';
export type HiringPriority = 'Low' | 'Normal' | 'High';

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
	time_ago: string;
	days_until_expiry?: number;
	is_expiring_soon: boolean;
	accepts_applications: boolean;
}

export interface LanguageRequirement {
	language: string;
	proficiency: LanguageProficiency;
}

export interface JobDetail extends JobListItem {
	description: string;
	job_role: string;
	locations: Location[];
	skills: Skill[];
	industries: Industry[];
	qualifications: Qualification[];
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
	// New enhanced fields
	seniority_level?: SeniorityLevel;
	application_method: ApplicationMethod;
	application_url?: string;
	show_salary: boolean;
	benefits?: string[];
	language_requirements?: LanguageRequirement[];
	required_certifications?: string;
	preferred_certifications?: string;
	relocation_required: boolean;
	travel_percentage?: string;
	hiring_timeline?: HiringTimeline;
	hiring_priority: HiringPriority;
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
	min_salary?: number;
	max_salary?: number;
	salary_type?: SalaryType;
	min_year?: number;
	max_year?: number;
	min_month?: number;
	max_month?: number;
	fresher?: boolean;
	vacancies?: number;
	company_description?: string;
	company_address?: string;
	company_links?: string;
	company_emails?: string;
	// New enhanced fields
	seniority_level?: SeniorityLevel;
	application_method?: ApplicationMethod;
	application_url?: string;
	show_salary?: boolean;
	benefits?: string[];
	language_requirements?: LanguageRequirement[];
	required_certifications?: string;
	preferred_certifications?: string;
	relocation_required?: boolean;
	travel_percentage?: string;
	hiring_timeline?: HiringTimeline;
	hiring_priority?: HiringPriority;
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

export type JobUpdateData = Partial<JobCreateData>;

export interface JobsListResponse {
	count: number;
	/**
	 * DRF pagination sends `null` on the first/last page — the key is always
	 * present, so `?: string` (meaning "may be absent") was wrong. Verified
	 * against a paginated response.
	 */
	next: string | null;
	previous: string | null;
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

/**
 * Verified against GET /recruiter/dashboard/stats/ on a live backend.
 *
 * The SvelteKit copy declared a `total_views` field that the API has never
 * returned (it appears nowhere in api/v1/recruiter/), and omitted the three
 * fields below that it does return.
 */
export interface DashboardStats {
	total_jobs: number;
	live_jobs: number;
	draft_jobs: number;
	closed_jobs: number;
	expired_jobs: number;
	total_applicants: number;
	new_applicants: number;
	/** Pre-formatted by Django, e.g. "N/A" or "+12%" — display only, not a number. */
	applicants_trend: string;
	avg_applications_per_job: number;
}

export interface ApplicantPipeline {
	pending: number;
	shortlisted: number;
	hired: number;
	rejected: number;
	conversion_rate: number;
}

/**
 * `recent_jobs` entries are `JobListItem` enriched with two counters that the
 * plain /recruiter/jobs/ list does not return. The dashboard page reads both, but
 * the SvelteKit type had them as bare `JobListItem` — the page only got away with
 * it by mapping over `(job: any)`.
 */
export interface DashboardRecentJob extends JobListItem {
	new_applicants: number;
	pending_review: number;
}

export interface DashboardStatsResponse {
	stats: DashboardStats;
	/** Used throughout the dashboard page but absent from the original type. */
	pipeline: ApplicantPipeline;
	recent_jobs: DashboardRecentJob[];
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
}

// ===== API Response Types =====

/**
 * The envelope Django actually returns from recruiter mutations: flat, with any
 * extra payload as a sibling key rather than nested.
 *
 *   { "success": true, "message": "…", "invitation": { … } }
 *
 * Compose with `&` for those extras, e.g. `MutationResponse & { user: TeamMember }`.
 */
export interface MutationResponse {
	success: boolean;
	message: string;
}

/**
 * Generic envelope with a nested `data` payload.
 *
 * NOTE: no recruiter endpoint audited so far actually returns this shape — the
 * SvelteKit app annotated its auth and team calls with `ApiResponse<{ user }>`
 * and `ApiResponse<{ invitation }>`, which would have made `res.data.user`
 * type-check while being `undefined` at runtime. Prefer `MutationResponse`
 * unless you have confirmed the endpoint really nests under `data`.
 */
export interface ApiResponse<T = unknown> {
	success: boolean;
	message?: string;
	data?: T;
}

// The `ApiError` interface that lived here was unused in both apps, and would now
// shadow the ApiError *class* exported from lib/api/client.ts. Removed rather than
// carried over — use `ApiError` / `UnauthorizedError` from lib/api/client.ts.
