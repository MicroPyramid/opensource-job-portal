/**
 * Team Member Detail Page - Server Load
 * Shows detailed profile, job history, and stats for a team member
 */

import type { PageServerLoad } from './$types';
import { error, redirect } from '@sveltejs/kit';
import { API_BASE_URL } from '$lib/config/env';

export const load: PageServerLoad = async ({ params, parent, fetch }) => {
	const memberId = params.id;

	// Get user data from parent layout
	const { user } = await parent();

	// Check if user is part of a company and has admin access
	if (!user?.company) {
		throw redirect(302, '/dashboard/');
	}

	if (!user?.is_admin) {
		throw error(403, 'You do not have permission to view team member details');
	}

	try {
		// Fetch team member details
		const response = await fetch(`${API_BASE_URL}/recruiter/team/${memberId}/`);

		if (!response.ok) {
			if (response.status === 404) {
				throw error(404, 'Team member not found');
			}
			if (response.status === 403) {
				throw error(403, 'You do not have permission to view this team member');
			}
			throw error(response.status, 'Failed to load team member details');
		}

		const memberData = await response.json();

		return {
			member: memberData,
			user
		};
	} catch (err: any) {
		console.error('Error loading team member details:', err);

		// Re-throw known errors
		if (err.status) {
			throw err;
		}

		throw error(500, err.message || 'Failed to load team member details');
	}
};
