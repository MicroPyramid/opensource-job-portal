# Authentication

This is the part of PeelJobs most likely to trip you up, because the token
lives in two different places depending on which side of the SvelteKit server
you are on.

## The split

| Component | Holds | Sends |
| --- | --- | --- |
| Browser | Nothing. Only an opaque `HttpOnly` cookie it cannot read. | Cookie, to the SvelteKit server only |
| SvelteKit server | Reads the JWT out of the cookie | `Authorization: Bearer <JWT>` to Django |
| Django API | Nothing. Stateless. | — |

**The Django API accepts JWTs in the `Authorization` header only. It does not
read cookies.** Conversely, the browser never sees a token — only a cookie set
by the SvelteKit server, which Django knows nothing about.

## Login flow

```
1. Browser  ──POST /login/ (form)──▶  SvelteKit server
2. SvelteKit ──POST /api/v1/auth/login/──▶  Django
3. Django   ──{ access, refresh }──▶  SvelteKit
4. SvelteKit sets HttpOnly cookies, redirects
5. Browser  ──cookie──▶  SvelteKit  ──Bearer──▶  Django
```

The token crosses from Django to SvelteKit in a response body, and from
SvelteKit to Django in a header. It never crosses into JavaScript.

## Cookies

Set by `src/lib/server/auth.ts` in each app:

| Cookie | Lifetime |
| --- | --- |
| `access_token` | 1 hour |
| `refresh_token` | 7 days |

```ts
{
  httpOnly: true,
  secure: !dev,        // on outside development
  sameSite: 'lax',
  path: '/',
  maxAge
}
```

Cookie lifetimes deliberately mirror `SIMPLE_JWT` in `jobsp/settings.py`. A
cookie shorter than its token just forces needless refreshes; a cookie longer
than its token means presenting one Django has already rejected.

## Token settings

`SIMPLE_JWT`, in `backend/jobsp/settings.py`:

| Setting | Value |
| --- | --- |
| `ACCESS_TOKEN_LIFETIME` | 1 hour |
| `REFRESH_TOKEN_LIFETIME` | 7 days |
| `ROTATE_REFRESH_TOKENS` | `True` |
| `BLACKLIST_AFTER_ROTATION` | `True` |
| `UPDATE_LAST_LOGIN` | `True` |
| `ALGORITHM` | `HS256`, signed with `SECRET_KEY` |
| `AUTH_HEADER_TYPES` | `Bearer` |

!!! warning "Refresh tokens are single-use"

    With `ROTATE_REFRESH_TOKENS` and `BLACKLIST_AFTER_ROTATION` both on, every
    refresh issues a *new* refresh token and blacklists the old one. Code that
    refreshes and then reuses the original refresh token gets a `401` — the
    replacement must be stored.

    Changing `SECRET_KEY` invalidates every issued token, since it is the
    signing key.

## Automatic refresh

`hooks.server.ts` runs on every request. If the access token is missing or
expired but a refresh token is present, it exchanges it, writes the new pair
back to the cookies, and continues. If the exchange fails it clears both
cookies.

This is why nothing in a `load()` function has to think about token expiry.

It also intercepts SvelteKit's `fetch` and attaches the bearer header:

```ts
headers.set('Authorization', `Bearer ${event.locals.accessToken}`);
```

That interception applies to the `fetch` handed to `load` and `actions`. Using
the global `fetch` bypasses it and sends an unauthenticated request — a common
and confusing bug.

## Endpoints

Under `/api/v1/auth/`:

| Path | Purpose |
| --- | --- |
| `login/` | Exchange credentials for tokens |
| `register/` | Create an account |
| `verify-email/` | Confirm an address |
| `resend-verification/` | Re-send the confirmation |
| `forgot-password/` | Start a reset |
| `reset-password/` | Complete a reset |
| `change-password/` | Change while authenticated |
| `change-email/` · `verify-email-change/` | Change an address |
| `google/url/` · `google/callback/` · `google/disconnect/` | Google OAuth |
| `token/refresh/` | Rotate the token pair |
| `token/verify/` | Validate a token |
| `me/` | Current user |
| `logout/` | Blacklist the refresh token |

## Roles

`user_type` is `JS` (Job Seeker) or `EM` (Employer). Employer sub-roles come
from company membership rather than the type:

| Effective role | Shape |
| --- | --- |
| Company Admin | `EM`, `is_admin=True`, owns a company |
| Recruiter | `EM`, `is_admin=False`, belongs to that company |
| Individual recruiter | `EM`, no company |

Platform staff are `is_staff` / `is_superuser` and use the Django dashboard, not
the SvelteKit apps.

## Using the API directly

Outside the frontends — a script, or an integration — talk to Django the same
way SvelteKit does:

```bash
# 1. Obtain tokens
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"email": "you@example.com", "password": "..."}'

# 2. Use the access token
curl http://localhost:8000/api/v1/auth/me/ \
  -H 'Authorization: Bearer <access_token>'

# 3. Refresh before it expires (returns a new refresh token too)
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H 'Content-Type: application/json' \
  -d '{"refresh": "<refresh_token>"}'
```

There is no cookie-based path into the API. Sending a session cookie to
`/api/v1/` authenticates nothing.
