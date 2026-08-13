# Backend

Django project rooted at `backend/`, with settings in `backend/jobsp/`.

## Apps

| Directory | Purpose | Status |
| --- | --- | --- |
| `peeldb/` | Core models — User, Company, JobPost, Skill, Location | Current |
| `api/` | REST API, versioned under `api/v1/` | Current |
| `dashboard/` | Platform-admin UI and Celery tasks | Django templates |
| `tickets/` | Support ticketing | Django templates |
| `social/` | OAuth authentication backend | Mixed |
| `psite/` | Site-wide pages | Django templates |
| `mpcomp/` | Shared helpers, imported by `dashboard` and `peeldb` | Current |
| `mp_celery_monitor/` | Celery health endpoint | Current |

## What is legacy

The API under `/api/v1/` is **not** legacy. It is what both frontends call and
it is actively maintained.

What is on its way out is `backend/templates/` — the server-rendered Django UI.
Job seeker and recruiter pages have already moved to SvelteKit; the
platform-admin dashboard is the largest remaining template surface.

!!! warning "Do not invest in `backend/templates/`"

    Styling fixes, markup cleanup and Bootstrap→Tailwind conversion in the
    Django templates is wasted work — those pages are replaced by rewriting them
    in SvelteKit, not by editing the template. New UI belongs in `site/` or
    `recruiter/`.

The apps that served the old job seeker and recruiter UIs — `pjob/`,
`candidate/`, `recruiter/`, `agency/` — have already been deleted from the
backend. `recruiter/` at the *repository* root is the new SvelteKit dashboard
and is unrelated.

## API layer

`api/v1/` is split by resource, each with its own URL module:

```
api/v1/
├── auth/          registration, login, token refresh, password reset
├── profile/       job seeker profile
├── jobs/          job listings, search, applications
├── alerts/        job alerts and subscriptions
├── skills/        skill lookup / autocomplete
├── locations/     country → state → city lookup
├── employment/    employment history
├── companies/     company profiles
├── recruiters/    public recruiter data
├── recruiter/     authenticated recruiter dashboard operations
├── contact/       contact form
├── webhooks/      inbound webhooks
└── common/        shared helpers (e.g. fuzzy_name_filter)
```

Note that `recruiters/` and `recruiter/` are different: the plural is public
read data, the singular is the authenticated dashboard surface.

## Consuming the API

PeelJobs does not maintain a hand-written endpoint reference. Keeping one
accurate across twelve modules is a losing battle, and a stale reference is
worse than none.

Instead the running server publishes its schema, generated from the actual
serializers and viewsets by drf-spectacular:

| | URL |
| --- | --- |
| Swagger UI | `/api/docs/` |
| ReDoc | `/api/redoc/` |
| OpenAPI 3 schema | `/api/schema/` |

Point a client generator at `/api/schema/` to get typed bindings.

Read [Authentication](authentication.md) first — every non-public endpoint
needs a bearer token, and obtaining one is the part a schema browser will not
explain.

## Data model

Defined in `peeldb/models.py`.

### User

A custom user model. `user_type` has two values:

| Value | Meaning |
| --- | --- |
| `JS` | Job Seeker |
| `EM` | Employer |

This was simplified from an earlier five-value scheme (`RR`, `RA`, `AA`, `AR`).
Employer sub-roles are now expressed through company membership and the
`is_admin` flag rather than distinct user types — a Company Admin is an `EM`
user with `is_admin=True` who owns a company; a Recruiter is an `EM` user in
the same company without it.

### JobPost

The central model. Status choices:

| Value | Meaning |
| --- | --- |
| `Draft` | Created, not submitted |
| `Pending` | Awaiting moderation |
| `Live` | Visible publicly |
| `Disabled` | Withdrawn |
| `Exprired` | Past its closing date |
| `Published` | Legacy — see below |
| `Hired` | Position filled |
| `Process` | In progress |

!!! bug "`Exprired` is spelled that way in the database"

    The choice value is `"Exprired"`, not `"Expired"` — only the human-readable
    label is spelled correctly. API consumers must match the misspelling.
    Correcting it requires a data migration.

`Published` is vestigial. The recruiter API creates jobs as `Draft` and
publishing sets `Live` directly, so nothing writes `Published` any more.

`job_type` covers `full-time`, `permanent`, `contract`, `internship`,
`part-time`, `freelance`, `walk-in`, `government` and `fresher`.

### Supporting models

| Model | Notes |
| --- | --- |
| `Company` | Profile, industry, size, location |
| `Skill` | Tagged onto job posts many-to-many |
| `Industry` | Job categorisation |
| `Qualification` / `Degree` | Education requirements |
| `Country` → `State` → `City` | Three-level location hierarchy |
| `JobAlert` / `Subscriber` | Email alert subscriptions |

## Conventions

- Business logic belongs in models and managers, not views.
- Use `select_related` and `prefetch_related`. Job list endpoints serialise
  related skills and locations; without prefetching they degrade badly.
- Environment configuration goes through python-dotenv — see
  [Configuration](../getting-started/configuration.md).
