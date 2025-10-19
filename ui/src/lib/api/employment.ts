import { ApiClient } from './client';

export interface EmploymentHistory {
	id: number;
	company: string;
	designation: string;
	from_date: string;
	to_date?: string;
	current_job: boolean;
	job_profile: string;
	duration?: string; // Calculated field from backend
}

export interface EmploymentHistoryCreateUpdate {
	company: string;
	designation: string;
	from_date: string;
	to_date?: string;
	current_job: boolean;
	job_profile: string;
}

/**
 * Get user's employment history (ordered by most recent first)
 */
export async function getMyEmploymentHistory(): Promise<EmploymentHistory[]> {
	return ApiClient.get<EmploymentHistory[]>('/employment/my-history/');
}

/**
 * Add a new employment record
 */
export async function addEmploymentHistory(
	data: EmploymentHistoryCreateUpdate
): Promise<EmploymentHistory> {
	return ApiClient.post<EmploymentHistory>('/employment/my-history/add/', data);
}

/**
 * Update an existing employment record
 */
export async function updateEmploymentHistory(
	employmentId: number,
	data: Partial<EmploymentHistoryCreateUpdate>
): Promise<EmploymentHistory> {
	return ApiClient.patch<EmploymentHistory>(`/employment/my-history/${employmentId}/`, data);
}

/**
 * Delete an employment record
 */
export async function deleteEmploymentHistory(employmentId: number): Promise<void> {
	return ApiClient.delete(`/employment/my-history/${employmentId}/`);
}
