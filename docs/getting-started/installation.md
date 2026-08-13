# Installation

This walks through a complete local development environment: the Django
backend, then the two SvelteKit frontends.

## Prerequisites

| Requirement | Version | Notes |
| --- | --- | --- |
| Python | 3.12+ | Pinned by `backend/.python-version` |
| PostgreSQL | 13+ | 16 recommended. Full-text search relies on it. |
| Node.js | 22.x | Only needed for the frontends |
| pnpm | 9+ | Package manager for both frontends |
| Redis | 6+ | Only needed for Celery |
| [uv](https://docs.astral.sh/uv/) | latest | Manages the Python environment |

### System packages

=== "Debian / Ubuntu"

    ```bash
    sudo apt update && sudo apt install -y \
      git postgresql redis-server python3-dev \
      build-essential libjpeg-dev zlib1g-dev

    # Node.js 22.x
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt install -y nodejs
    sudo npm install -g pnpm
    ```

=== "macOS (Homebrew)"

    ```bash
    brew install postgresql@16 redis node@22 pnpm jpeg
    brew services start postgresql@16
    brew services start redis
    ```

### uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` creates and manages `backend/.venv` from `pyproject.toml` and `uv.lock`,
and pins the interpreter from `.python-version`. You do not create or activate
a virtualenv yourself.

## Backend

### 1. Clone and install

```bash
git clone https://github.com/MicroPyramid/opensource-job-portal.git
cd opensource-job-portal/backend

uv sync
```

`uv sync` installs development tooling (ruff, coverage, bpython) along with the
runtime dependencies. Use `uv sync --no-dev` to omit it.

### 2. Create the database

```bash
createdb peeljobs
```

If your PostgreSQL install has no role for your shell user:

```bash
sudo -u postgres createdb peeljobs
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'password';"
```

### 3. Configure the environment

Create `backend/.env`:

```ini
DEBUG=True
SECRET_KEY=replace-me

DB_NAME=peeljobs
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=127.0.0.1
DB_PORT=5432

PEEL_URL=http://localhost:8000/
DEFAULT_FROM_EMAIL=noreply@peeljobs.local
```

Generate a real secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

!!! warning "Database settings are five separate variables, not a URL"

    PeelJobs reads `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` and `DB_PORT`
    individually. There is no `DATABASE_URL` support — setting one has no
    effect, and Django will fail to connect with an empty database name.

    The same applies to Redis: the variable is `CELERY_BROKER_URL`, not
    `REDIS_URL`.

`backend/.env.example` lists every variable the project recognises, including
optional integrations. See [Configuration](configuration.md) for what each one
does and which are genuinely required.

### 4. Migrate and seed

```bash
uv run manage.py migrate
uv run manage.py load_initial_data
uv run manage.py createsuperuser
```

`load_initial_data` loads countries, states, cities, skills, industries,
qualifications, functional areas and languages in dependency order. The
application will run without it, but location and skill pickers will be empty.

The migration step also enables the `pg_trgm` extension and creates the
generated full-text search column. `CREATE EXTENSION` requires a PostgreSQL
superuser; if migration `0079_pg_trgm_extension` fails on permissions, grant
your role superuser or create the extension manually:

```bash
psql -d peeljobs -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

### 5. Run it

```bash
uv run manage.py runserver
```

| Endpoint | URL |
| --- | --- |
| API root | <http://localhost:8000/api/v1/> |
| API docs (Swagger) | <http://localhost:8000/api/docs/> |
| API docs (ReDoc) | <http://localhost:8000/api/redoc/> |
| Django admin | <http://localhost:8000/admin/> |
| Platform dashboard | <http://localhost:8000/dashboard/> |

## Frontends

Both apps are SvelteKit with `adapter-node`, and both are server-side rendered.
Neither reads the database; they call the Django API.

The backend must be running before either frontend is useful.

### Job seeker site

```bash
cd site
pnpm install
cp .env.example .env
pnpm dev
```

Serves <http://localhost:5173>.

### Recruiter dashboard

```bash
cd recruiter
pnpm install
cp .env.example .env
pnpm dev
```

Serves <http://localhost:5174>.

The default `.env.example` in each app already points at
`http://localhost:8000/api/v1` and at the other frontend's port, so no editing
is needed for a standard local setup.

## Optional: background jobs

Job alerts, notification emails and scheduled reports run through Celery. Skip
this unless you are working on them.

```bash
# Terminal 1 — worker
cd backend
DJANGO_SETTINGS_MODULE=jobsp.settings_local uv run celery -A jobsp worker --loglevel=info

# Terminal 2 — scheduler
cd backend
DJANGO_SETTINGS_MODULE=jobsp.settings_local uv run celery -A jobsp beat --loglevel=info
```

Celery defaults to `redis://localhost:6379/1` if `CELERY_BROKER_URL` is unset.

!!! note

    Several scheduled tasks are currently disabled in the source. See
    [Background Jobs](../architecture/background-jobs.md) before assuming an
    email will send.

## Verify

```bash
cd backend
uv run manage.py check      # should report no issues
uv run manage.py test       # full suite
```

## Next

- [Configuration](configuration.md) — what the other environment variables do
- [Test Data](test-data.md) — seeded logins and bulk sample data
- [Running the Stack](running.md) — day-to-day process management
