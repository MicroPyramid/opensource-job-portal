/**
 * Profile API
 * Job seeker profile management
 */

import { ApiClient } from './client';

// Location types
export interface City {
	id: number;
	name: string;
	slug: string;
	state_name: string;
	country_name: string;
}

export interface State {
	id: number;
	name: string;
	slug: string;
	country_name: string;
}

export interface Country {
	id: number;
	name: string;
	slug: string;
}

// Skill types
export interface Skill {
	id: number;
	name: string;
	slug: string;
	skill_type: string;
}

export interface TechnicalSkill {
	id: number;
	skill: Skill;
	year?: number;
	month?: number;
	last_used?: string;
	version?: string;
	proficiency?: string;
	is_major: boolean;
}

// Employment history
export interface EmploymentHistory {
	id: number;
	company: string;
	designation: string;
	from_date: string;
	to_date?: string;
	current_job: boolean;
	job_profile: string;
}

// Education
export interface EducationDetails {
	id: number;
	institute_name: string;
	degree_name: string;
	specialization: string;
	from_date: string;
	to_date?: string;
	score: string;
	current_education: boolean;
}

// Project
export interface Project {
	id: number;
	name: string;
	from_date?: string;
	to_date?: string;
	skills: Skill[];
	description: string;
	location?: City;
	role?: string;
	size?: number;
}

// Certification
export interface Certification {
	id: number;
	name: string;
	organization: string;
	credential_id?: string;
	credential_url?: string;
	issued_date?: string;
	expiry_date?: string;
	does_not_expire: boolean;
	description?: string;
	created_at: string;
	updated_at: string;
}

// Complete user profile
export interface UserProfile {
	// Basic Info
	id: number;
	email: string;
	username: string;
	first_name: string;
	last_name: string;
	user_type: string;
	user_type_display: string;
	profile_completion_percentage: number;

	// Profile Picture & Photo
	profile_pic?: string;
	profile_pic_url?: string;
	photo?: string;

	// Contact Info
	mobile?: string;
	alternate_mobile?: number;
	show_email: boolean;

	// Personal Info
	gender?: string;
	dob?: string;
	marital_status?: string;
	nationality?: string;

	// Location Info
	address?: string;
	permanent_address?: string;
	pincode?: number;
	city?: City;
	state?: State;
	country?: Country;
	current_city?: City;
	preferred_city: City[];

	// Professional Info
	job_role: string;
	profile_description: string;
	year?: string;
	month?: string;
	current_salary?: string;
	expected_salary?: string;
	notice_period?: string;
	relocation: boolean;
	is_looking_for_job: boolean;
	is_open_to_offers: boolean;

	// Resume
	resume?: string;
	resume_url?: string;
	resume_title?: string;
	resume_text?: string;

	// Related Data
	skills: TechnicalSkill[];
	employment_history: EmploymentHistory[];
	education: EducationDetails[];
	project: Project[];
	certifications: Certification[];

	// Account Status
	is_active: boolean;
	email_verified: boolean;
	mobile_verified: boolean;
	is_gp_connected: boolean;
	date_joined: string;
	profile_updated: string;

	// Email Preferences
	email_notifications: boolean;
	is_unsubscribe: boolean;
}

// Update profile request
export interface ProfileUpdateRequest {
	first_name?: string;
	last_name?: string;
	mobile?: string;
	gender?: string;
	dob?: string;
	marital_status?: string;
	nationality?: string;
	address?: string;
	permanent_address?: string;
	pincode?: number;
	city_id?: number;
	state_id?: number;
	country_id?: number;
	current_city_id?: number;
	preferred_city_ids?: number[];
	job_role?: string;
	profile_description?: string;
	year?: string;
	month?: string;
	current_salary?: string;
	expected_salary?: string;
	notice_period?: string;
	relocation?: boolean;
	is_looking_for_job?: boolean;
	is_open_to_offers?: boolean;
	resume_title?: string;
	email_notifications?: boolean;
	show_email?: boolean;
}

/**
 * Get current user's profile
 */
export async function getProfile(): Promise<UserProfile> {
	return ApiClient.get<UserProfile>('/profile/');
}

/**
 * Update user profile (full update)
 */
export async function updateProfile(data: ProfileUpdateRequest): Promise<UserProfile> {
	return ApiClient.put<UserProfile>('/profile/', data);
}

/**
 * Partially update user profile
 */
export async function patchProfile(data: Partial<ProfileUpdateRequest>): Promise<UserProfile> {
	return ApiClient.patch<UserProfile>('/profile/', data);
}

/**
 * Upload profile picture
 */
export async function uploadProfilePicture(file: File): Promise<{ message: string; profile_pic_url: string }> {
	const formData = new FormData();
	formData.append('profile_pic', file);
	formData.append('file_type', 'profile_pic');

	return ApiClient.postFormData<{ message: string; profile_pic_url: string }>(
		'/profile/upload/',
		formData
	);
}

/**
 * Upload resume
 */
export async function uploadResume(file: File): Promise<{ message: string; resume_url: string }> {
	const formData = new FormData();
	formData.append('resume', file);
	formData.append('file_type', 'resume');

	return ApiClient.postFormData<{ message: string; resume_url: string }>(
		'/profile/upload/',
		formData
	);
}
