/**
 * /verify-email-change/ — redeem the token mailed to a user's new address
 *
 * Distinct from /verify-email/, which activates a brand-new account and signs
 * it in. This one changes the email on an existing account and deliberately
 * does **not** touch the session cookies: the link is opened from an inbox,
 * which may be a different browser to the one holding the session, and issuing
 * tokens here would be a way to mint a session from a mailbox alone.
 */

import type { PageServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config/env';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const token = url.searchParams.get('token');

	if (!token) {
		return {
			status: 'error' as const,
			message: 'This link is missing its confirmation code.'
		};
	}

	try {
		const response = await fetch(`${API_BASE_URL}/auth/verify-email-change/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ token })
		});

		const data = await response.json().catch(() => null);

		if (response.ok) {
			return {
				status: 'success' as const,
				message: data?.message ?? 'Your email address has been updated.'
			};
		}

		return {
			status: 'error' as const,
			message: data?.error ?? 'This link is invalid or has already been used.'
		};
	} catch (error) {
		console.error('Email change verification error:', error);
		return {
			status: 'error' as const,
			message: 'We could not reach the server. Please try again.'
		};
	}
};
