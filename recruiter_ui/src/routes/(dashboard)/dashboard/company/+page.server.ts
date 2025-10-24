/**
 * Company Profile Page - Server Load
 * Restricts access to company admins and team members only
 * Independent recruiters (no company) are redirected to dashboard
 */

import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ parent }) => {
	// Get user data from parent layout
	const { user } = await parent();

	// Check if user is an independent recruiter (no company)
	// Independent recruiters should not access company profile page
	if (!user?.company) {
		throw redirect(302, '/dashboard/');
	}

	// User has a company - allow access
	return {
		user
	};
};
