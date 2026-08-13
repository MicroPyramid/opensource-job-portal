# PeelJobs

PeelJobs is an open-source job board. Recruiters post openings, job seekers
search and apply, and platform staff moderate what gets published. It is free
software under the MIT License, and it is built to be self-hosted.

The platform is three deployable pieces:

| Component | Directory | What it is |
| --- | --- | --- |
| Backend | `backend/` | Django + Django REST Framework, PostgreSQL, Celery. Serves the REST API at `/api/v1/`. |
| Job seeker site | `site/` | SvelteKit app. Public job search, applications, alerts. |
| Recruiter dashboard | `recruiter/` | SvelteKit app. Job posting and applicant management. |

The two SvelteKit apps never talk to the database. They call the Django API
server-side and render HTML, which keeps job listings indexable and keeps
authentication tokens out of the browser.

## Start here

<div class="grid cards" markdown>

- :material-download: **[Installation](getting-started/installation.md)**

    Get the backend and both frontends running locally.

- :material-cog: **[Configuration](getting-started/configuration.md)**

    Environment variables, and which ones you actually need.

- :material-sitemap: **[Architecture](architecture/index.md)**

    How the pieces fit, and why the API is called server-side.

- :material-source-pull: **[Contributing](contributing/index.md)**

    Branching, code standards, and running the test suite.

</div>

## Who it is for

**Self-hosters** want [Installation](getting-started/installation.md) and
[Deployment](deployment/production.md).

**Contributors** want [Architecture](architecture/index.md) — particularly
[Authentication](architecture/authentication.md), which is the part of the
system most likely to trip you up.

**API consumers** should read
[Authentication](architecture/authentication.md) for the token flow. PeelJobs
does not maintain a hand-written endpoint reference; the running server
publishes a live OpenAPI schema instead. See
[Consuming the API](architecture/backend.md#consuming-the-api).

**Job seekers and recruiters** using a hosted PeelJobs instance want the
[User Guides](guides/index.md).

## Project status

PeelJobs began as a Django application that rendered its own HTML templates.
It is partway through a migration to the split architecture above: the REST API
and both SvelteKit frontends are the actively developed surface, while the
remaining Django templates serve the platform-admin dashboard and are being
retired.

If you are contributing, that distinction matters — see
[Backend](architecture/backend.md#what-is-legacy) for what is current and what
is on its way out.
