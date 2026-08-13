/**
 * /unsubscribe/ — honour an unsubscribe link from a sent email
 *
 * Replaces `candidate…applicant_email_unsubscribing`,
 * `candidate…applicant_unsubscribing` and `pjob.views.unsubscribe`.
 *
 * `?type=` mirrors the `email_type` segment of the legacy
 * `/unsubscribe_email/<email_type>/<message_id>/` links, which are sitting in
 * mail that has already been delivered — the values cannot change.
 *
 * The unsubscribe is applied on GET rather than behind a confirm button. A
 * one-click unsubscribe is what RFC 8058 and the bulk-sender rules expect, and
 * the alternative — a form nobody submits — is how a list ends up marked as
 * spam.
 */

import type { PageServerLoad, Actions } from './$types';
import { fail } from '@sveltejs/kit';
import { API_BASE_URL } from '$lib/config/env';

const TYPES = ['alert', 'subscriber', 'user'] as const;

export const load: PageServerLoad = async ({ url, fetch }) => {
	const code = url.searchParams.get('code') ?? '';
	const requested = url.searchParams.get('type') ?? 'user';
	const type = (TYPES as readonly string[]).includes(requested) ? requested : 'user';

	if (!code) {
		return { status: 'error' as const, message: 'This link is missing its code.', code, type };
	}

	try {
		const response = await fetch(`${API_BASE_URL}/alerts/unsubscribe/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ type, code })
		});

		const data = await response.json().catch(() => null);

		if (response.ok) {
			return { status: 'success' as const, message: data?.message ?? 'You are unsubscribed.', code, type };
		}

		return {
			status: 'error' as const,
			message: 'We could not process that unsubscribe link.',
			code,
			type
		};
	} catch (error) {
		console.error('Unsubscribe error:', error);
		return { status: 'error' as const, message: 'We could not reach the server.', code, type };
	}
};

export const actions: Actions = {
	// Optional follow-up: the legacy form demanded a reason before it would
	// unsubscribe anyone. Here the unsubscribe has already happened in load()
	// and the reason is a courtesy.
	reason: async ({ request, fetch }) => {
		const form = await request.formData();
		const payload = {
			type: form.get('type')?.toString() ?? 'user',
			code: form.get('code')?.toString() ?? '',
			reason: form.get('reason')?.toString() ?? ''
		};

		try {
			await fetch(`${API_BASE_URL}/alerts/unsubscribe/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});
			return { reasonSaved: true };
		} catch (error) {
			console.error('Unsubscribe reason error:', error);
			return fail(500, { reasonSaved: false });
		}
	}
};
