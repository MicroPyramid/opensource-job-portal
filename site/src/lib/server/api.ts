/**
 * Server-side Django API helper.
 *
 * Used from `+page.server.ts` load functions and form actions. Pass the
 * request-scoped `fetch` that SvelteKit hands you — `hooks.server.ts` has
 * already wrapped it to attach the JWT from the HttpOnly cookie, so nothing
 * here deals with tokens.
 *
 * This replaces the old browser-side `$lib/api/client.ts`, which read the JWT
 * out of localStorage and called Django directly from the page.
 */

import { API_BASE_URL } from '$lib/config/env';
import { formatApiError } from '$lib/utils/error-formatter';

type Fetch = typeof fetch;

export class ApiRequestError extends Error {
	constructor(
		message: string,
		readonly status: number,
		readonly data: unknown = null
	) {
		super(message);
		this.name = 'ApiRequestError';
	}
}

async function parse(response: Response): Promise<unknown> {
	if (response.status === 204) return null;
	return response.json().catch(() => null);
}

async function request<T>(
	fetchFn: Fetch,
	path: string,
	init: RequestInit = {}
): Promise<T> {
	const response = await fetchFn(`${API_BASE_URL}${path}`, init);
	const data = await parse(response);

	if (!response.ok) {
		throw new ApiRequestError(
			formatApiError(data ?? { detail: response.statusText }),
			response.status,
			data
		);
	}

	return data as T;
}

function json(method: string, body?: unknown): RequestInit {
	return {
		method,
		headers: { 'Content-Type': 'application/json' },
		body: body === undefined ? undefined : JSON.stringify(body)
	};
}

export function apiGet<T>(fetchFn: Fetch, path: string): Promise<T> {
	return request<T>(fetchFn, path, { method: 'GET' });
}

export function apiPost<T>(fetchFn: Fetch, path: string, body?: unknown): Promise<T> {
	return request<T>(fetchFn, path, json('POST', body));
}

export function apiPatch<T>(fetchFn: Fetch, path: string, body?: unknown): Promise<T> {
	return request<T>(fetchFn, path, json('PATCH', body));
}

export function apiPut<T>(fetchFn: Fetch, path: string, body?: unknown): Promise<T> {
	return request<T>(fetchFn, path, json('PUT', body));
}

export function apiDelete<T>(fetchFn: Fetch, path: string): Promise<T> {
	return request<T>(fetchFn, path, { method: 'DELETE' });
}

/** Multipart upload — let fetch set the boundary, so no Content-Type here. */
export function apiUpload<T>(fetchFn: Fetch, path: string, body: FormData): Promise<T> {
	return request<T>(fetchFn, path, { method: 'POST', body });
}

/**
 * Run a load-time fetch that should degrade to a fallback rather than blow up
 * the whole page (e.g. a sidebar widget when Django is flaky).
 */
export async function apiGetOr<T>(fetchFn: Fetch, path: string, fallback: T): Promise<T> {
	try {
		return await apiGet<T>(fetchFn, path);
	} catch {
		return fallback;
	}
}

/**
 * Forward a browser request to Django, one explicit route at a time.
 *
 * Used by the `+server.ts` endpoints under `src/routes/api/`. The browser
 * calls this app's own origin with its HttpOnly cookie; `hooks.server.ts` has
 * already wrapped `event.fetch` to turn that cookie into an
 * `Authorization: Bearer` header, so the token never reaches the page.
 *
 * These are deliberately per-resource routes rather than a catch-all
 * passthrough — only the paths listed under `src/routes/api/` are reachable.
 */
export async function forward(
	event: { request: Request; fetch: Fetch; url: URL },
	path: string,
	options: { method?: string; search?: boolean } = {}
): Promise<Response> {
	const method = options.method ?? event.request.method;
	const search = options.search === false ? '' : event.url.search;

	const init: RequestInit = { method };

	if (method !== 'GET' && method !== 'DELETE') {
		const contentType = event.request.headers.get('content-type') ?? '';

		if (contentType.includes('multipart/form-data')) {
			// Pass the parsed form straight through; fetch re-encodes it with a
			// fresh boundary, which is what Django needs.
			init.body = await event.request.formData();
		} else {
			init.headers = { 'Content-Type': 'application/json' };
			init.body = await event.request.text();
		}
	}

	const response = await event.fetch(`${API_BASE_URL}${path}${search}`, init);
	const body = await response.text();

	return new Response(body, {
		status: response.status,
		headers: {
			'Content-Type': response.headers.get('content-type') ?? 'application/json'
		}
	});
}
