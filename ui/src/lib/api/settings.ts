import { ApiClient } from './client';

export interface PasswordChangeData {
	old_password: string;
	new_password: string;
	confirm_password: string;
}

export interface NotificationSettings {
	email_notifications: boolean;
	is_unsubscribe: boolean;
}

export interface PrivacySettings {
	show_email: boolean;
	is_looking_for_job: boolean;
	is_open_to_offers: boolean;
}

export interface AccountSettings extends NotificationSettings, PrivacySettings {
	first_name: string;
	last_name: string;
	mobile: string;
	alternate_mobile?: string;
	gender?: string;
	dob?: string;
	marital_status?: string;
}

/**
 * Change password for authenticated user
 */
export async function changePassword(data: PasswordChangeData): Promise<{ message: string }> {
	return ApiClient.post<{ message: string }>('/auth/change-password/', data);
}

/**
 * Update notification settings
 */
export async function updateNotificationSettings(
	data: NotificationSettings
): Promise<{ message: string }> {
	return ApiClient.patch<{ message: string }>('/profile/', data);
}

/**
 * Update privacy settings
 */
export async function updatePrivacySettings(data: PrivacySettings): Promise<{ message: string }> {
	return ApiClient.patch<{ message: string }>('/profile/', data);
}

/**
 * Update account settings (basic info, notifications, privacy combined)
 */
export async function updateAccountSettings(
	data: Partial<AccountSettings>
): Promise<{ message: string }> {
	return ApiClient.patch<{ message: string }>('/profile/', data);
}
