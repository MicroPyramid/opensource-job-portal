/**
 * /job-alerts/verify/ — redeem the confirmation code for a job alert
 *
 * The weekly digest (`dashboard.tasks.applicants_job_notifications`) only
 * sends to alerts with `is_verified=True`, so this page is what actually turns
 * an alert on.
 */

import type { PageServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config/env';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const code = url.searchParams.get('code');

	if (!code) {
		return { status: 'error' as const, message: 'This link is missing its code.' };
	}

	try {
		const response = await fetch(`${API_BASE_URL}/alerts/verify/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ code })
		});

		const data = await response.json().catch(() => null);

		if (response.ok) {
			return {
				status: 'success' as const,
				message: 'Your job alert is active. New matching jobs are sent every Monday.',
				alert: data
			};
		}

		return {
			status: 'error' as const,
			message: data?.error ?? 'This link is invalid or has already been used.'
		};
	} catch (error) {
		console.error('Alert verification error:', error);
		return { status: 'error' as const, message: 'We could not reach the server.' };
	}
};
