/**
 * Resume API Client
 * Handles resume operations for job seekers (single resume per user)
 */
import { ApiClient } from './client';

/**
 * Upload resume file
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

/**
 * Delete resume file
 */
export async function deleteResume(): Promise<{ message: string }> {
	return ApiClient.delete<{ message: string }>('/profile/resume/delete/');
}
