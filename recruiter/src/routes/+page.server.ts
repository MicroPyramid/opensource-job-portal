import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies }) => {
	// Check for auth tokens
	const accessToken = cookies.get('access_token');
	const refreshToken = cookies.get('refresh_token');
	const hasValidAuth = accessToken || refreshToken;

	if (hasValidAuth) {
		throw redirect(302, '/dashboard/');
	} else {
		throw redirect(302, '/login/');
	}
};
