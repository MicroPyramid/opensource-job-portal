import { ApiClient } from './client';

export interface Qualification {
	id: number;
	name: string;
	slug: string;
}

export interface Degree {
	id: number;
	qualification: Qualification;
	degree_type: 'Permanent' | 'PartTime';
	specialization: string;
}

export interface EducationInstitute {
	id: number;
	name: string;
	address: string;
	city_name: string;
}

export interface EducationDetails {
	id: number;
	institute_id?: number;
	institute_name: string;
	institute_address: string;
	degree_id?: number;
	degree_name: string;
	degree_type: string;
	specialization: string;
	from_date: string;
	to_date?: string;
	score: string;
	current_education: boolean;
}

export interface EducationDetailsCreateUpdate {
	institute_id: number;
	degree_id: number;
	from_date: string;
	to_date?: string;
	score: string;
	current_education: boolean;
}

/**
 * Get all education entries for the authenticated user
 * Sorted by most recent first
 */
export async function getMyEducation(): Promise<EducationDetails[]> {
	return ApiClient.get<EducationDetails[]>('/profile/education/');
}

/**
 * Get a specific education entry
 */
export async function getEducationById(educationId: number): Promise<EducationDetails> {
	return ApiClient.get<EducationDetails>(`/profile/education/${educationId}/`);
}

/**
 * Add a new education entry
 */
export async function addEducation(
	data: EducationDetailsCreateUpdate
): Promise<EducationDetails> {
	return ApiClient.post<EducationDetails>('/profile/education/', data);
}

/**
 * Update an existing education entry (full update)
 */
export async function updateEducation(
	educationId: number,
	data: EducationDetailsCreateUpdate
): Promise<EducationDetails> {
	return ApiClient.put<EducationDetails>(`/profile/education/${educationId}/`, data);
}

/**
 * Partially update an education entry
 */
export async function patchEducation(
	educationId: number,
	data: Partial<EducationDetailsCreateUpdate>
): Promise<EducationDetails> {
	return ApiClient.patch<EducationDetails>(`/profile/education/${educationId}/`, data);
}

/**
 * Delete an education entry
 */
export async function deleteEducation(educationId: number): Promise<void> {
	return ApiClient.delete(`/profile/education/${educationId}/`);
}

/**
 * Get all active qualifications (degree types)
 * For populating qualification dropdowns
 */
export async function getQualifications(): Promise<Qualification[]> {
	return ApiClient.get<Qualification[]>('/profile/education-lookups/qualifications/');
}

/**
 * Get all degrees, optionally filtered by qualification or search term
 */
export async function getDegrees(params?: {
	qualification_id?: number;
	search?: string;
}): Promise<Degree[]> {
	return ApiClient.get<Degree[]>('/profile/education-lookups/degrees/', params);
}

/**
 * Search education institutes by name
 */
export async function searchInstitutes(params?: {
	search?: string;
	limit?: number;
}): Promise<EducationInstitute[]> {
	return ApiClient.get<EducationInstitute[]>('/profile/education-lookups/institutes/', params);
}
