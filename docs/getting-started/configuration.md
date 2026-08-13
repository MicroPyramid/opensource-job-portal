# Configuration

## Settings modules

PeelJobs has three settings modules, selected only through
`DJANGO_SETTINGS_MODULE`. Nothing imports another module implicitly.

| Module | Used by | Purpose |
| --- | --- | --- |
| `jobsp.settings` | — | Shared base. Production-safe on its own. |
| `jobsp.settings_local` | `manage.py` | Development. `DEBUG=True`, console email, verbose logging, local file storage. |
| `jobsp.settings_server` | `manage_server.py`, `wsgi.py` | Production. `DEBUG=False`, HSTS, SSL redirect, S3. |

So `uv run manage.py runserver` gets development settings and
`uv run manage_server.py runserver` gets production settings, without you
setting anything.

!!! danger "Do not import `settings_local` from `settings`"

    `jobsp/settings.py` must never end with `from .settings_local import *`. It
    did once. Because `settings_local.py` is tracked in git it ships to
    production, and `settings_server` does `from .settings import *` — so every
    development override leaked into production, including replacing the SES
    email backend with the console backend. Production printed mail to stdout
    instead of sending it.

## Environment variables

Variables are read from `backend/.env` via python-dotenv.
`backend/.env.example` is the full list.

### Required

| Variable | Notes |
| --- | --- |
| `SECRET_KEY` | No default. Django will not start without it. |
| `DB_NAME` | |
| `DB_USER` | |
| `DB_PASSWORD` | |
| `DB_HOST` | e.g. `127.0.0.1` |
| `DB_PORT` | e.g. `5432` |

!!! warning "There is no `DATABASE_URL`"

    The five `DB_*` variables are read individually in
    `jobsp/settings.py`. `DATABASE_URL` is not parsed anywhere in the project;
    setting it does nothing and Django will fail with an empty database name.

### Commonly set

| Variable | Default | Purpose |
| --- | --- | --- |
| `DEBUG` | `True` | Forced to `False` by `settings_server`. |
| `PEEL_URL` | `http://peeljobs.com/` | Base URL used in generated links and emails. |
| `DEFAULT_FROM_EMAIL` | `peeljobs@micropyramid.com` | Envelope sender. |
| `SITE_FRONTEND_URL` | `http://localhost:5173` | Where the job seeker app is served. |
| `RECRUITER_FRONTEND_URL` | `http://localhost:5174` | Where the recruiter app is served. |
| `SITE_DOMAIN` | `peeljobs.com` | Bare domain, used for canonical URLs. |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Redis connection. **Not** `REDIS_URL`. |
| `CELERY_RESULT_BACKEND` | unset | Optional result store. |
| `SENTRY_DSN` | unset | Error reporting. Leave unset locally. |

`ALLOWED_HOSTS` is **not** an environment variable — it is a literal list in
`jobsp/settings.py` (`peeljobs.com`, `test.peeljobs.com`, `localhost`,
`127.0.0.1`). Self-hosting under a different domain means editing that list.

### Optional integrations

Leave these unset unless you are using the feature.

=== "OAuth"

    | Variable | Purpose |
    | --- | --- |
    | `GOOGLE_CLIENT_ID` | Google sign-in |
    | `GOOGLE_CLIENT_SECRET` | Google sign-in |
    | `GOOGLE_LOGIN_HOST` | OAuth callback host, e.g. `http://localhost:8000` |
    | `GITAPPID` / `GITAPPSECRET` | GitHub sign-in |
    | `FACEBOOK_APP_ID` / `FACEBOOK_APP_SECRET` | Facebook sign-in |

=== "AWS"

    | Variable | Purpose |
    | --- | --- |
    | `AWS_ACCESS_KEY` / `AWS_SECRET_KEY` | Credentials |
    | `AWS_STORAGE_BUCKET_NAME` | S3 bucket for media |
    | `AWS_SES_REGION_NAME` | e.g. `eu-west-1` |
    | `AWS_SES_REGION_ENDPOINT` | e.g. `email.eu-west-1.amazonaws.com` |

    The base settings set `EMAIL_BACKEND = "django_ses.SESBackend"`, so
    production sends through SES. Development overrides this to the console
    backend, which is why local email appears in your terminal.

=== "Other"

    | Variable | Purpose |
    | --- | --- |
    | `RECAPTCHA_SITE_KEY` / `RECAPTCHA_SECRET_KEY` | Form spam protection |
    | `CELERY_MONITOR_URL` / `MP_CELERY_MONITOR_KEY` | Celery monitoring endpoint |

!!! note "Two known drifts in `.env.example`"

    `backend/.env.example` has not fully caught up with the code:

    - It spells the reCAPTCHA keys `RECAPTCHAPUBLICKEY` and
      `RECAPTCHAPRIVATEKEY`. The code reads `RECAPTCHA_SITE_KEY` and
      `RECAPTCHA_SECRET_KEY`. Use the names in this table.
    - It still declares `HAYSTACKURL`. Elasticsearch was removed when search
      moved to PostgreSQL; the variable is dead. See
      [Search](../architecture/search.md).

## Frontend configuration

Both SvelteKit apps read `PUBLIC_*` variables from their own `.env`. Copying
`.env.example` is enough for local development.

### `site/.env`

```ini
PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
PUBLIC_SITE_URL=http://localhost:5173
PUBLIC_RECRUITER_URL=http://localhost:5174
```

### `recruiter/.env`

```ini
PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
PUBLIC_SITE_URL=http://localhost:5174
PUBLIC_JOBSEEKER_URL=http://localhost:5173
```

Despite the `PUBLIC_` prefix — a SvelteKit convention meaning "safe to expose to
the browser" — the API base URL is used by server-side load functions and form
actions. See [Authentication](../architecture/authentication.md) for why the
browser never calls Django directly.
