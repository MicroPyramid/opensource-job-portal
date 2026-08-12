/**
 * Finish a Google signup.
 *
 * Google gave us a verified identity but not a company, so an account cannot
 * exist yet. This is the gap between `auth/google/callback/` and
 * `auth/google/complete/`.
 *
 * Deliberately not folded into /signup/: that page is a multi-step wizard
 * built around choosing an account type and setting a password, and none of
 * that applies here. Everything Google already told us is off the form —
 * including the email, which is read from the signed token rather than posted,
 * so a hand-edited field cannot claim someone else's address.
 */

import { redirect, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { getApiBaseUrl } from '$lib/config/env';
import { setAuthCookies } from '$lib/server/auth';
import { clearPendingGoogleSignup, readPendingGoogleSignup } from '$lib/server/google';
import { formatApiError } from '$lib/utils/error-formatter';

export const load: PageServerLoad = async ({ cookies }) => {
	const pending = readPendingGoogleSignup(cookies);

	// No cookie means someone opened this URL directly, or sat on it past the
	// token's 30 minutes. Either way there is nothing to complete.
	if (!pending) {
		throw redirect(303, '/login/?error=signup_expired');
	}

	// Only the display fields cross to the browser; the token stays server-side
	// and is re-read from the cookie on submit.
	return {
		email: pending.email,
		firstName: pending.first_name,
		lastName: pending.last_name
	};
};

export const actions: Actions = {
	default: async ({ request, cookies, fetch }) => {
		const formData = await request.formData();

		const pending = readPendingGoogleSignup(cookies);
		if (!pending) {
			throw redirect(303, '/login/?error=signup_expired');
		}

		const accountType = formData.get('account_type')?.toString() || 'company';
		const companyName = formData.get('company_name')?.toString().trim() || '';
		const companyWebsite = formData.get('company_website')?.toString().trim() || '';

		if (accountType === 'company') {
			// Django requires both, and a round trip to be told so is wasteful.
			if (!companyName) {
				return fail(400, { error: 'Company name is required', values: Object.fromEntries(formData) });
			}
			if (!companyWebsite) {
				return fail(400, {
					error: 'Company website is required',
					values: Object.fromEntries(formData)
				});
			}
		}

		if (formData.get('agree_to_terms') !== 'on') {
			return fail(400, {
				error: 'Please accept the terms to continue',
				values: Object.fromEntries(formData)
			});
		}

		const requestData: Record<string, unknown> = {
			session_token: pending.token,
			account_type: accountType,
			agree_to_terms: true
		};

		const phone = formData.get('phone')?.toString().trim() || '';
		const jobTitle = formData.get('job_title')?.toString().trim() || '';
		if (phone) requestData.phone = phone;
		if (jobTitle) requestData.job_title = jobTitle;

		if (accountType === 'company') {
			requestData.company_name = companyName;
			requestData.company_website = companyWebsite;

			const companyIndustry = formData.get('company_industry')?.toString() || '';
			const companySize = formData.get('company_size')?.toString() || '';
			if (companyIndustry) requestData.company_industry = companyIndustry;
			if (companySize) requestData.company_size = companySize;
		}

		try {
			const response = await fetch(`${getApiBaseUrl()}/recruiter/auth/google/complete/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(requestData)
			});

			const data = await response.json();

			if (!response.ok) {
				// An expired or tampered token cannot be retried on this form —
				// the OAuth round trip has to start over.
				if (typeof data.error === 'string' && data.error.includes('session token')) {
					clearPendingGoogleSignup(cookies);
					throw redirect(303, '/login/?error=signup_expired');
				}

				return fail(400, {
					error: formatApiError(data),
					values: Object.fromEntries(formData)
				});
			}

			// Google already verified the address, so this skips the
			// email-verification step that a password signup ends on.
			clearPendingGoogleSignup(cookies);
			setAuthCookies(cookies, data.access, data.refresh);

			throw redirect(303, '/dashboard/');
		} catch (error) {
			if (error && typeof error === 'object' && 'status' in error && 'location' in error) {
				throw error;
			}

			console.error('Google signup error:', error);
			return fail(500, {
				error: 'An unexpected error occurred. Please try again.',
				values: Object.fromEntries(formData)
			});
		}
	}
};
