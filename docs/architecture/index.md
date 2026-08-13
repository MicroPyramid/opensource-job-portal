# Architecture

PeelJobs is one Django backend and two SvelteKit frontends. The frontends never
touch the database; they call the REST API from their own servers.

```
                    ┌──────────────┐        ┌──────────────┐
   job seeker  ───▶ │   site/      │        │  recruiter/  │ ◀─── recruiter
     browser        │  SvelteKit   │        │  SvelteKit   │        browser
                    │   :5173      │        │    :5174     │
                    └──────┬───────┘        └──────┬───────┘
                           │  Authorization: Bearer <JWT>
                           └───────────┬────────────┘
                                       ▼
                              ┌─────────────────┐
                              │    backend/     │
                              │  Django + DRF   │
                              │     :8000       │
                              └────────┬────────┘
                                       │
                     ┌─────────────────┼─────────────────┐
                     ▼                 ▼                 ▼
               ┌───────────┐    ┌───────────┐    ┌───────────┐
               │ PostgreSQL│    │   Redis   │    │  Celery   │
               │ + FTS     │    │  broker   │    │  workers  │
               └───────────┘    └───────────┘    └───────────┘
```

## The one rule

**The browser never calls the Django API directly.** Every request to
`/api/v1/` originates from a SvelteKit server process, which attaches an
`Authorization: Bearer` header.

This is not a style preference; three things depend on it:

- **JWTs stay out of JavaScript.** Tokens live in `HttpOnly` cookies that only
  the SvelteKit server can read, so an XSS bug cannot exfiltrate them.
- **Job listings stay indexable.** Pages render server-side with real content,
  not an empty shell that fills in after a client fetch.
- **Separate production domains work without third-party cookies.** Django never
  receives a cookie and the browser never receives a token, so
  `peeljobs.com` and `api.peeljobs.com` need no cross-site cookie handling.

[Authentication](authentication.md) covers the token flow in detail.

## Sections

| Page | Covers |
| --- | --- |
| [Backend](backend.md) | Django apps, the API layer, data model, what is legacy |
| [Frontends](frontends.md) | The two SvelteKit apps, SSR, routing conventions |
| [Authentication](authentication.md) | JWT cookie flow, refresh, roles |
| [Search](search.md) | PostgreSQL full-text search and trigram fallback |
| [Background Jobs](background-jobs.md) | Celery tasks and their current state |

## Technology

| Layer | Choice |
| --- | --- |
| API | Django 5.2 LTS, Django REST Framework |
| Database | PostgreSQL |
| Search | PostgreSQL `tsvector` + `pg_trgm` — no separate search service |
| Auth | `djangorestframework-simplejwt` |
| Queue | Celery + Redis |
| Frontends | SvelteKit (Svelte 5), TypeScript, Tailwind CSS 4 |
| Icons | Lucide (`@lucide/svelte`) |
| Python deps | uv |
| Node deps | pnpm |
| API schema | drf-spectacular (OpenAPI 3) |

Django is deliberately held on the 5.2 LTS series, supported to April 2028.
`django-celery-beat` caps Django below 6.1, and `django-storages` and
`django-schema-viewer` publish no 6.x classifier.
