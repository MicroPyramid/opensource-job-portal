import { ApiClient } from './client';

export async function uploadResume(file: File): Promise<{ message: string; resume_url: string }> {
	const formData = new FormData();
	formData.append('resume', file);
	formData.append('file_type', 'resume');

	return ApiClient.postFormData<{ message: string; resume_url: string }>(
		'/profile/upload/',
		formData
	);
}

export async function deleteResume(): Promise<{ message: string }> {
	return ApiClient.delete<{ message: string }>('/profile/resume/delete/');
}
