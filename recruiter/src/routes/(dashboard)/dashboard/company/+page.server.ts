/**
 * Company Profile Page - Server Load
 * Restricts access to company admins and team members only
 * Independent recruiters (no company) are redirected to dashboard
 */

import type { PageServerLoad, Actions } from './$types';
import { redirect, fail } from '@sveltejs/kit';
import { API_BASE_URL } from '$lib/config/env';

export const load: PageServerLoad = async ({ parent, fetch }) => {
	// Get user data from parent layout
	const { user } = await parent();

	// Check if user is an independent recruiter (no company)
	// Independent recruiters should not access company profile page
	if (!user?.company) {
		throw redirect(302, '/dashboard/');
	}

	// Fetch company profile data from API
	try {
		const response = await fetch(`${API_BASE_URL}/recruiter/company/profile/`);

		if (response.ok) {
			const companyData = await response.json();
			return {
				user,
				company: companyData
			};
		} else {
			console.error('Failed to load company profile:', response.status);
			return {
				user,
				company: null,
				error: 'Failed to load company profile'
			};
		}
	} catch (error) {
		console.error('Error loading company profile:', error);
		return {
			user,
			company: null,
			error: 'Failed to load company profile'
		};
	}
};

export const actions: Actions = {
	updateCompany: async ({ request, fetch }) => {
		const formData = await request.formData();

		// Extract form data
		const updateData: Record<string, string> = {};

		const fields = ['name', 'website', 'address', 'profile', 'phone_number', 'email', 'size'];
		fields.forEach(field => {
			const value = formData.get(field);
			if (value && value.toString().trim() !== '') {
				updateData[field] = value.toString();
			}
		});

		try {
			const response = await fetch(`${API_BASE_URL}/recruiter/company/profile/update/`, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(updateData)
			});

			const result = await response.json();

			if (response.ok) {
				return {
					success: true,
					message: result.message || 'Company profile updated successfully',
					company: result.company
				};
			} else {
				return fail(400, {
					success: false,
					error: result.error || 'Failed to update company profile',
					errors: result
				});
			}
		} catch (error) {
			console.error('Error updating company:', error);
			return fail(500, {
				success: false,
				error: 'An error occurred while updating the company profile'
			});
		}
	},

	/**
	 * Upload company logo
	 *
	 * Forwarded as multipart to the same profile-update endpoint, which accepts
	 * profile_pic. Kept separate from updateCompany so selecting a file can
	 * submit on its own without touching the rest of the form.
	 */
	uploadLogo: async ({ request, fetch }) => {
		const formData = await request.formData();
		const file = formData.get('profile_pic');

		if (!file || !(file instanceof File)) {
			return fail(400, {
				action: 'uploadLogo',
				success: false,
				error: 'Please provide a logo image'
			});
		}

		const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
		if (!allowedTypes.includes(file.type)) {
			return fail(400, {
				action: 'uploadLogo',
				success: false,
				error: 'Invalid file type. Please upload a JPEG or PNG image'
			});
		}

		const maxSize = 2 * 1024 * 1024;
		if (file.size > maxSize) {
			return fail(400, {
				action: 'uploadLogo',
				success: false,
				error: 'File too large. Maximum size is 2MB'
			});
		}

		try {
			const response = await fetch(`${API_BASE_URL}/recruiter/company/profile/update/`, {
				method: 'PATCH',
				body: formData
			});

			const result = await response.json();

			if (response.ok) {
				return {
					action: 'uploadLogo',
					success: true,
					message: result.message || 'Company logo updated successfully',
					company: result.company
				};
			}

			return fail(response.status, {
				action: 'uploadLogo',
				success: false,
				error: result.error || result.detail || 'Failed to upload company logo'
			});
		} catch (error) {
			console.error('Error uploading company logo:', error);
			return fail(500, {
				action: 'uploadLogo',
				success: false,
				error: 'An error occurred while uploading the company logo'
			});
		}
	}
};
