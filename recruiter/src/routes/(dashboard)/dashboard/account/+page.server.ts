/**
 * Account Page Server Load & Actions
 * Handles profile viewing and updating
 */

import type { PageServerLoad, Actions } from './$types';
import { fail } from '@sveltejs/kit';
import { getApiBaseUrl } from '$lib/config/env';
import { formatApiError } from '$lib/utils/error-formatter';

export const load: PageServerLoad = async ({ parent }) => {
	// Get user data from parent layout
	const { user } = await parent();

	return {
		user
	};
};

export const actions: Actions = {
	/**
	 * Update profile information
	 */
	updateProfile: async ({ request, cookies, fetch }) => {
		const formData = await request.formData();

		// Build update payload
		const updates: Record<string, string> = {};
		const firstName = formData.get('first_name');
		const lastName = formData.get('last_name');
		const jobTitle = formData.get('job_title');
		const mobile = formData.get('mobile');

		if (firstName) updates.first_name = firstName.toString();
		if (lastName) updates.last_name = lastName.toString();
		if (jobTitle) updates.job_title = jobTitle.toString();
		if (mobile) updates.mobile = mobile.toString();

		try {
			// Call Django API using enhanced fetch (adds Authorization header automatically)
			const response = await fetch(`${getApiBaseUrl()}/recruiter/profile/update/`, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(updates)
			});

			const result = await response.json();

			if (!response.ok) {
				return fail(response.status, {
					error: result.error || result.detail || 'Failed to update profile',
					values: updates
				});
			}

			return {
				success: true,
				message: result.message || 'Profile updated successfully',
				user: result.user
			};
		} catch (error: any) {
			return fail(500, {
				error: error.message || 'Network error occurred',
				values: updates
			});
		}
	},

	/**
	 * Change password.
	 *
	 * Django validates the current password and runs the project's password
	 * validators, so the only checks worth repeating here are the ones that
	 * save a round trip.
	 */
	changePassword: async ({ request, fetch }) => {
		const formData = await request.formData();

		const oldPassword = formData.get('old_password')?.toString() ?? '';
		const newPassword = formData.get('new_password')?.toString() ?? '';
		const confirmPassword = formData.get('confirm_password')?.toString() ?? '';

		if (!oldPassword || !newPassword || !confirmPassword) {
			return fail(400, { passwordError: 'Please fill in all password fields' });
		}

		if (newPassword !== confirmPassword) {
			return fail(400, { passwordError: 'New passwords do not match' });
		}

		try {
			const response = await fetch(`${getApiBaseUrl()}/recruiter/auth/change-password/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					old_password: oldPassword,
					new_password: newPassword,
					confirm_password: confirmPassword
				})
			});

			const result = await response.json();

			if (!response.ok) {
				// DRF answers with {field: [msg]}; formatApiError turns that into
				// "Current password: …" rather than a raw object. Its field-name
				// table already covers old_password/new_password/confirm_password.
				return fail(response.status, { passwordError: formatApiError(result) });
			}

			return {
				passwordSuccess: true,
				passwordMessage: result.message || 'Password changed successfully'
			};
		} catch (error: any) {
			return fail(500, {
				passwordError: error.message || 'Network error occurred'
			});
		}
	},

	/**
	 * Upload profile picture
	 */
	uploadPicture: async ({ request, cookies, fetch }) => {
		const formData = await request.formData();
		const file = formData.get('profile_pic');

		if (!file || !(file instanceof File)) {
			return fail(400, {
				error: 'Please provide a profile picture'
			});
		}

		// Validate file type
		const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
		if (!allowedTypes.includes(file.type)) {
			return fail(400, {
				error: 'Invalid file type. Please upload a JPEG or PNG image'
			});
		}

		// Validate file size (max 2MB)
		const maxSize = 2 * 1024 * 1024;
		if (file.size > maxSize) {
			return fail(400, {
				error: 'File too large. Maximum size is 2MB'
			});
		}

		try {
			// Forward the FormData to Django
			const response = await fetch(`${getApiBaseUrl()}/recruiter/profile/picture/`, {
				method: 'POST',
				body: formData
			});

			const result = await response.json();

			if (!response.ok) {
				return fail(response.status, {
					error: result.error || result.detail || 'Failed to upload profile picture'
				});
			}

			return {
				success: true,
				message: result.message || 'Profile picture uploaded successfully',
				user: result.user
			};
		} catch (error: any) {
			return fail(500, {
				error: error.message || 'Network error occurred'
			});
		}
	}
};
