import "server-only";
import { apiUrl } from "@/lib/config/env";
import { getAccessToken } from "@/lib/auth/session";
import { formatApiError } from "@/lib/utils/error-formatter";

/**
 * Server-side Django API client.
 *
 * Replaces recruiter/src/lib/api/client.ts. Two structural changes:
 *
 *  1. Server-only. The browser never calls Django, so there is no isomorphic
 *     branch and no `credentials: 'include'`. The JWT is read from the HttpOnly
 *     cookie here and sent as `Authorization: Bearer`.
 *
 *  2. No client-side refresh queue. The original carried `isRefreshing` /
 *     `refreshSubscribers` machinery that could not work: the tokens are
 *     HttpOnly, so browser JS could never read one to refresh it
 *     (MIGRATION.md debt #4). Refresh now happens in `proxy.ts`, which is the
 *     only place able to write cookies before a page renders.
 *
 * Caching: Next 16 makes fetch caching opt-in, so these requests are uncached by
 * default — correct for per-recruiter data. Pass `cache: 'force-cache'` per call
 * if something is genuinely shared and public.
 */

export class ApiError extends Error {
  readonly status: number;
  readonly payload: unknown;

  constructor(status: number, payload: unknown) {
    super(formatApiError(payload));
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

/**
 * Thrown on 401. During a page render this means "the access token is missing or
 * expired and proxy.ts could not renew it" — the caller should redirect to login.
 */
export class UnauthorizedError extends ApiError {
  constructor(payload: unknown) {
    super(401, payload);
    this.name = "UnauthorizedError";
  }
}

type FetchOptions = Omit<RequestInit, "body"> & {
  /** Skip the Authorization header (login, register, forgot-password …). */
  skipAuth?: boolean;
  body?: BodyInit | null;
};

/** Perform a Django API request and return the raw Response, unchecked. */
export async function rawFetch(
  endpoint: string,
  { skipAuth = false, ...options }: FetchOptions = {},
): Promise<Response> {
  const headers = new Headers(options.headers);

  if (!skipAuth) {
    const token = await getAccessToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  // Let fetch set the boundary for FormData; only default JSON otherwise.
  const isFormData = options.body instanceof FormData;
  if (!isFormData && options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  return fetch(apiUrl(endpoint), { ...options, headers });
}

/**
 * Perform a Django API request, throwing ApiError / UnauthorizedError on failure
 * and parsing the JSON body on success.
 */
export async function serverFetch<T>(
  endpoint: string,
  options: FetchOptions = {},
): Promise<T> {
  const response = await rawFetch(endpoint, options);

  if (!response.ok) {
    const payload = await response.json().catch(() => ({
      error: "Request failed",
      detail: response.statusText,
    }));

    if (response.status === 401) throw new UnauthorizedError(payload);
    throw new ApiError(response.status, payload);
  }

  // 204 No Content — several delete endpoints return an empty body.
  if (response.status === 204 || response.headers.get("content-length") === "0") {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

function withQuery(
  endpoint: string,
  params?: Record<string, unknown>,
): string {
  if (!params) return endpoint;

  const query = new URLSearchParams(
    Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== null && v !== "")
      .map(([k, v]) => [k, String(v)]),
  ).toString();

  return query ? `${endpoint}?${query}` : endpoint;
}

export const api = {
  get<T>(endpoint: string, params?: Record<string, unknown>, skipAuth = false) {
    return serverFetch<T>(withQuery(endpoint, params), {
      method: "GET",
      skipAuth,
    });
  },

  post<T>(endpoint: string, data?: unknown, skipAuth = false) {
    return serverFetch<T>(endpoint, {
      method: "POST",
      body: data === undefined ? undefined : JSON.stringify(data),
      skipAuth,
    });
  },

  put<T>(endpoint: string, data?: unknown) {
    return serverFetch<T>(endpoint, {
      method: "PUT",
      body: data === undefined ? undefined : JSON.stringify(data),
    });
  },

  patch<T>(endpoint: string, data?: unknown) {
    return serverFetch<T>(endpoint, {
      method: "PATCH",
      body: data === undefined ? undefined : JSON.stringify(data),
    });
  },

  delete<T>(endpoint: string, params?: Record<string, unknown>) {
    return serverFetch<T>(withQuery(endpoint, params), { method: "DELETE" });
  },

  /** Multipart upload — profile pictures, company logos, resumes. */
  postFormData<T>(endpoint: string, formData: FormData, skipAuth = false) {
    return serverFetch<T>(endpoint, {
      method: "POST",
      body: formData,
      skipAuth,
    });
  },
};
