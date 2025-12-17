/**
 * Profile API Client
 * Handles recruiter profile operations
 */

import { apiClient } from './client';

export interface UpdateProfileData {
	first_name?: string;
	last_name?: string;
	job_title?: string;
	mobile?: string;
}

export interface UpdateProfileResponse {
	success: boolean;
	user: any;
	message: string;
}

export interface UploadProfilePictureResponse {
	success: boolean;
	user: any;
	message: string;
}

/**
 * Update recruiter profile
 */
export async function updateProfile(data: UpdateProfileData): Promise<UpdateProfileResponse> {
	return apiClient.patch<UpdateProfileResponse>('/recruiter/profile/update/', data);
}

/**
 * Upload profile picture
 */
export async function uploadProfilePicture(file: File): Promise<UploadProfilePictureResponse> {
	const formData = new FormData();
	formData.append('profile_pic', file);

	return apiClient.postFormData<UploadProfilePictureResponse>(
		'/recruiter/profile/picture/',
		formData
	);
}
