# Running the Stack

## Processes

A full local environment is up to five processes. Start only what you need.

=== "Django API"

    ```bash
    cd backend
    uv run manage.py runserver
    ```

    <http://localhost:8000> — uses `jobsp.settings_local`.

=== "Job seeker site"

    ```bash
    cd site
    pnpm dev
    ```

    <http://localhost:5173> — requires the API to be running.

=== "Recruiter dashboard"

    ```bash
    cd recruiter
    pnpm dev
    ```

    <http://localhost:5174> — requires the API to be running.

=== "Celery worker"

    ```bash
    cd backend
    DJANGO_SETTINGS_MODULE=jobsp.settings_local \
      uv run celery -A jobsp worker --loglevel=info
    ```

    Requires Redis.

=== "Celery beat"

    ```bash
    cd backend
    DJANGO_SETTINGS_MODULE=jobsp.settings_local \
      uv run celery -A jobsp beat --loglevel=info
    ```

    Scheduler. Requires the worker to actually execute anything.

Celery needs `DJANGO_SETTINGS_MODULE` set explicitly because it is not launched
through `manage.py`, which is what would otherwise select the development
settings module.

## Ports

| Service | URL |
| --- | --- |
| Django API | <http://localhost:8000/api/v1/> |
| API docs (Swagger) | <http://localhost:8000/api/docs/> |
| API docs (ReDoc) | <http://localhost:8000/api/redoc/> |
| OpenAPI schema | <http://localhost:8000/api/schema/> |
| Django admin | <http://localhost:8000/admin/> |
| Platform dashboard | <http://localhost:8000/dashboard/> |
| Job seeker site | <http://localhost:5173> |
| Recruiter dashboard | <http://localhost:5174> |

## Common commands

```bash
cd backend

uv run manage.py check              # configuration sanity
uv run manage.py test               # full test suite
uv run manage.py makemigrations
uv run manage.py migrate
uv run manage.py collectstatic
uv run manage.py shell
```

Frontend, in either `site/` or `recruiter/`:

```bash
pnpm check          # svelte-check type checking
pnpm build          # production build
pnpm start          # serve the build (adapter-node)
```

## Development vs production entry points

| | Development | Production |
| --- | --- | --- |
| Command | `uv run manage.py` | `uv run manage_server.py` |
| Settings | `jobsp.settings_local` | `jobsp.settings_server` |
| `DEBUG` | `True` | `False` |
| Email | console | Amazon SES |
| Media storage | local filesystem | S3 |

## Troubleshooting

**Django will not start — `SECRET_KEY` error.**
`SECRET_KEY` has no default. Set it in `backend/.env`.

**Django cannot connect to the database.**
Check the five `DB_*` variables. `DATABASE_URL` is not supported and will be
ignored — see [Configuration](configuration.md).

**Migration `0079_pg_trgm_extension` fails.**
`CREATE EXTENSION` needs a PostgreSQL superuser:

```bash
psql -d peeljobs -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

**Frontend loads but every page is empty.**
The API is probably not running, or `PUBLIC_API_BASE_URL` is wrong. Because
both apps are server-rendered, a failed API call shows up in the terminal
running `pnpm dev`, not in the browser console.

**Emails do not arrive locally.**
They are not meant to. `settings_local` uses the console email backend, so mail
is printed to the Django terminal.

**A scheduled task never runs.**
Check [Background Jobs](../architecture/background-jobs.md) first — several
Celery tasks are currently disabled in the source and return immediately.

**Redis connection refused.**
Only Celery needs Redis. If you are not working on background jobs, do not
start the worker or beat.
