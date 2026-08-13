# Getting Started

Four pages, in the order you need them:

1. **[Installation](installation.md)** — system dependencies, the backend, and
   both frontends.
2. **[Configuration](configuration.md)** — environment variables. Only a handful
   are required; the rest enable optional integrations.
3. **[Test Data](test-data.md)** — fixtures, seeded users, and bulk sample data.
4. **[Running the Stack](running.md)** — the processes to start, and what
   listens where.

## What you are installing

PeelJobs is not a single process. A complete development environment is:

| Process | Port | Required |
| --- | --- | --- |
| Django API | 8000 | Yes |
| PostgreSQL | 5432 | Yes |
| Job seeker site (SvelteKit) | 5173 | Only to use the job seeker UI |
| Recruiter dashboard (SvelteKit) | 5174 | Only to use the recruiter UI |
| Redis | 6379 | Only for background jobs |
| Celery worker | — | Only for background jobs |
| Celery beat | — | Only for scheduled jobs |

You can develop against the API alone with just PostgreSQL and Django. Redis,
Celery, and the frontends are additive — start with the backend and add what
you need.
