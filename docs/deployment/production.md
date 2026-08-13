# Production Deployment

A production PeelJobs install is the Django API behind gunicorn, optionally the
two SvelteKit apps behind Node, plus PostgreSQL, Redis and Celery.

## Settings

Production uses `jobsp.settings_server` via `manage_server.py` and `wsgi.py`.
It sets `DEBUG = False`, HSTS, and `SECURE_SSL_REDIRECT`, and stores media on
S3.

| Task | Development | Production |
| --- | --- | --- |
| Management commands | `uv run manage.py` | `uv run manage_server.py` |
| Settings module | `jobsp.settings_local` | `jobsp.settings_server` |

## Environment

```ini
DEBUG=False
SECRET_KEY=<generated, kept out of git>

DB_NAME=peeljobs_prod
DB_USER=peeljobs
DB_PASSWORD=<secret>
DB_HOST=127.0.0.1
DB_PORT=5432

CELERY_BROKER_URL=redis://localhost:6379/1

PEEL_URL=https://yourdomain.com/
SITE_DOMAIN=yourdomain.com
SITE_FRONTEND_URL=https://yourdomain.com
RECRUITER_FRONTEND_URL=https://recruiter.yourdomain.com

DEFAULT_FROM_EMAIL=noreply@yourdomain.com
SENTRY_DSN=<optional>

AWS_ACCESS_KEY=<...>
AWS_SECRET_KEY=<...>
AWS_STORAGE_BUCKET_NAME=<...>
AWS_SES_REGION_NAME=eu-west-1
AWS_SES_REGION_ENDPOINT=email.eu-west-1.amazonaws.com
```

!!! warning "`ALLOWED_HOSTS` is not an environment variable"

    It is a literal list in `jobsp/settings.py` containing `peeljobs.com`,
    `test.peeljobs.com`, `localhost` and `127.0.0.1`. Deploying under any other
    domain means editing that list, or Django will reject every request with
    `DisallowedHost`.

## Install

```bash
cd /var/www/peeljobs/backend

# --locked, not --frozen: a stale uv.lock should fail the deploy rather than
# silently install dependencies that no longer match pyproject.toml.
# --no-dev keeps ruff, prospector and debug tooling off production.
uv sync --locked --no-dev

uv run manage_server.py migrate --noinput
uv run manage_server.py collectstatic --noinput
```

## Services

### Django

`/etc/systemd/system/peeljobs.service`:

```ini
[Unit]
Description=PeelJobs Django Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/peeljobs/backend
Environment="PATH=/var/www/peeljobs/backend/.venv/bin"
Environment="DJANGO_SETTINGS_MODULE=jobsp.settings_server"
ExecStart=/var/www/peeljobs/backend/.venv/bin/gunicorn \
  --workers 3 \
  --bind unix:/run/peeljobs/peeljobs.sock \
  jobsp.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Celery

`/etc/systemd/system/peeljobs-celery.service`:

```ini
[Unit]
Description=PeelJobs Celery Worker
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/peeljobs/backend
Environment="PATH=/var/www/peeljobs/backend/.venv/bin"
Environment="DJANGO_SETTINGS_MODULE=jobsp.settings_server"
ExecStart=/var/www/peeljobs/backend/.venv/bin/celery -A jobsp worker --loglevel=info
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

A second unit running `celery -A jobsp beat` is needed for scheduled tasks.
Read [Background Jobs](../architecture/background-jobs.md) before enabling
beat — several tasks are disabled, and the ones that work send bulk email.

### Frontends

Each SvelteKit app builds to a Node server:

```bash
cd site        # and again in recruiter/
pnpm install --frozen-lockfile
pnpm build
pnpm start     # node build
```

Run each under systemd or a process manager, with its `.env` pointing
`PUBLIC_API_BASE_URL` at the public API URL.

## Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        root /var/www/peeljobs;
        expires 30d;
    }

    location /media/ {
        root /var/www/peeljobs;
        expires 30d;
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # REQUIRED. settings_server.py sets SECURE_SSL_REDIRECT together with
        # SECURE_PROXY_SSL_HEADER. Without this header Django cannot tell the
        # original request was HTTPS and will redirect in a loop.
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_pass http://unix:/run/peeljobs/peeljobs.sock;
    }
}
```

!!! danger "The `X-Forwarded-Proto` header is not optional"

    Omit it and every request redirects forever. `SECURE_SSL_REDIRECT` sees
    what looks like a plain HTTP request, redirects to HTTPS, terminates at
    nginx, arrives at Django looking like HTTP again, and repeats.

## Database

PostgreSQL needs the `pg_trgm` extension, which migration `0079` creates.
`CREATE EXTENSION` requires superuser. If the deploy role is not one, create it
ahead of time:

```bash
sudo -u postgres psql -d peeljobs_prod -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

No search service is needed — see [Search](../architecture/search.md).

## Checklist

- [ ] `DEBUG=False` and a `SECRET_KEY` that is not in git
- [ ] Your domain added to `ALLOWED_HOSTS` in `jobsp/settings.py`
- [ ] TLS terminated, with `X-Forwarded-Proto` passed through
- [ ] `pg_trgm` available before migrating
- [ ] `uv sync --locked --no-dev`
- [ ] `collectstatic` run
- [ ] Frontend `.env` files pointing at the public API URL
- [ ] Background job state reviewed before starting beat
- [ ] Database backups configured
