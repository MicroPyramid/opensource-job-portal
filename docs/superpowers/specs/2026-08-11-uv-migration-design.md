# Migrate backend from pip + requirements.txt to uv + pyproject.toml

**Date:** 2026-08-11
**Status:** Approved, pending implementation plan

## Goal

Replace pip/`requirements.txt` dependency management in `backend/` with a uv-managed
project: `pyproject.toml` as the single manifest, `uv.lock` committed for reproducible
installs, and `uv run` as the command entrypoint.

## Non-goals

- Changing any dependency version. All 34 existing pins (27 runtime + 7 dev) carry over
  unchanged, so that any post-migration breakage is attributable to tooling, not a version
  bump. `ruff` is the single *addition*, and only because it is already in use undeclared.
- Consolidating lint tooling. `black` and `prospector` stay as-is; whether ruff replaces them
  is a lint-policy decision, tracked separately.
- Adding a `.github/dependabot.yml`. Dependabot currently runs from repo settings and detects
  the `pip` ecosystem at `/backend`; after this migration it will stop matching. Accepted
  knowingly — see Risks.
- Dockerising the backend. No Dockerfile exists today.

## Current state

| Item | State |
|---|---|
| `backend/requirements.txt` | 27 pinned deps, grouped by comment headers |
| `backend/dev-requirements.txt` | 7 pinned dev deps |
| `backend/setup.py` | **Dead code.** Opens a non-existent `README.rst` (crashes if run); `install_requires=[]`; referenced by nothing |
| `.gitlab-ci.yml` | **Broken.** Runs `pip install pipenv && pipenv install -d`, but the Pipfile was deleted in `8fac0de` |
| Python | 3.12.3 (system and the hand-built `../../env` venv) |
| uv | 0.12.1, already installed locally |
| ruff | **Undeclared but in active use.** `.ruff_cache` is gitignored and commit `66513e7` rewrote 20+ files as "resolve ruff linting errors", yet ruff appears in neither requirements file and is not installed anywhere on the dev machine |

## Design

### Layout

```
backend/
  pyproject.toml      # new — single dependency manifest
  uv.lock             # new — committed
  .python-version     # new — "3.12"
  .venv/              # new — uv-managed, gitignored
  requirements.txt        DELETED
  dev-requirements.txt    DELETED
  setup.py                DELETED
```

`pyproject.toml` sits beside `manage.py` at the Python root, not at the repo root — the repo
root is a polyglot workspace (`site/`, `recruiter/` are pnpm projects).

### `pyproject.toml`

```toml
[project]
name = "opensource-job-portal"
version = "0.1.0"
description = "An opensource job portal with unlimited free job posting and social API authentication."
readme = "../README.md"
requires-python = ">=3.12"
license = "MIT"
authors = [{ name = "Micropyramid", email = "hello@micropyramid.com" }]

dependencies = [
  # Core Framework
  "django==5.2.10",
  "python-dotenv==1.2.1",
  # Database
  "psycopg[binary]==3.3.2",
  "pymemcache==4.0.0",
  # Task Queue & Background Jobs
  "celery==5.6.2",
  "django-celery-beat==2.8.1",
  "redis==7.1.0",
  # Search
  "django-haystack==3.3.0",
  "elasticsearch==7.17.12",
  # REST API
  "djangorestframework==3.16.1",
  "djangorestframework-simplejwt==5.5.1",
  "dj-rest-auth==7.0.2",
  "drf-spectacular==0.29.0",
  "django-filter==25.2",
  # Storage & Media
  "boto3==1.42.39",
  "django-storages==1.14.6",
  "sorl-thumbnail==13.0.0",
  "pillow==12.1.0",
  # Email
  "django-ses==4.6.0",
  # Frontend & Assets
  "django-compressor==4.6.0",
  "django-cors-headers==4.9.0",
  # Utilities
  "arrow==1.4.0",
  "lxml==6.0.2",
  "requests==2.32.5",
  "pytz==2025.2",
  # Monitoring & Error Tracking
  "sentry-sdk[django]==2.51.0",
  # Production Server
  "gunicorn==25.0.0",
]

[dependency-groups]
dev = [
  # Code Quality & Linting
  "black==25.1.0",
  "prospector==1.17.1",
  "ruff==0.16.2",
  # Testing
  "behave-django==1.5.0",
  "coverage==7.8.2",
  # Development Tools
  "bpython==0.25",
  "django-schema-viewer==0.5.3",
  # Debug Tools (uncomment in settings_local.py to use)
  "django-debug-toolbar-template-profiler==2.1.0",
]

[tool.uv]
package = false
```

**Metadata** carries over from `setup.py` so nothing is lost when it is deleted. `readme`
points at the real `README.md`; `setup.py` pointed at a `README.rst` that has never existed.

**`package = false`** is technically redundant — uv treats a project without `[build-system]`
as a non-package ("virtual") project, installing its dependencies but not building or
installing the project itself. It is stated explicitly so the intent does not rest on an
inference. This is an application, not a distributable library.

**Comment groupings** from `requirements.txt` are preserved inline. They are the only
documentation of *why* each dependency is present.

**`ruff==0.16.2`** is added to close the gap identified above. An unpinned ruff run from
outside the project is what produced the currently-broken backend (see Dependencies).
Pinning it makes lint runs reproducible and reviewable.

### Python version

`requires-python = ">=3.12"` with `.python-version` = `3.12`.

Matches the current system and venv (3.12.3) without pinning to a patch release. uv resolves
the interpreter from `.python-version` and will download it if absent — which removes the
deploy's dependence on how `/home/peeljobs/env` was hand-built.

### Command changes

| Before | After |
|---|---|
| `source ../../env/bin/activate` + `pip install -r requirements.txt` | `uv sync` |
| `pip install -r requirements.txt -r dev-requirements.txt` | `uv sync` (`dev` is a default group) |
| `python manage.py <cmd>` | `uv run manage.py <cmd>` |
| `python manage_server.py <cmd>` | `uv run manage_server.py <cmd>` |
| `celery -A jobsp worker --loglevel=info` | `uv run celery -A jobsp worker --loglevel=info` |
| `celery -A jobsp beat --loglevel=info` | `uv run celery -A jobsp beat --loglevel=info` |

The existing `../../env` venv is retired. It is outside the repo and is left on disk for the
user to remove; nothing in the repo will reference it.

### GitLab deploy

`.gitlab-ci.yml` `deploy_live.script` becomes:

```yaml
- sudo /bin/rm -rf /home/peeljobs/peeljobs/; cp -r . /home/peeljobs/peeljobs
- cd /home/peeljobs/peeljobs/backend
- command -v uv || curl -LsSf https://astral.sh/uv/install.sh | sh
- uv sync --locked --no-dev
- uv run manage_server.py migrate --noinput
- sudo /usr/bin/supervisorctl restart all
```

Three deliberate changes beyond the tooling swap:

- The `source /home/peeljobs/env/bin/activate` line is dropped. uv creates and manages
  `backend/.venv` itself.
- **`--locked`, not `--frozen`.** `--frozen` uses the lockfile as-is without validating it
  against `pyproject.toml`, so a forgotten `uv lock` would silently deploy stale dependencies.
  `--locked` fails the pipeline instead.
- **`--no-dev`** keeps black, prospector, bpython and the debug toolbar off the production
  box. The current `pipenv install -d` explicitly installed dev dependencies in production.

The `command -v uv || curl ...` guard exists because the runner's PATH cannot be inspected
from this repo. If uv turns out to be preinstalled on the `peeljobs-live` runner, the guard
is a no-op and can be dropped later.

**Supervisor is out of scope.** Whatever supervisor config runs gunicorn on the live box
likely references a Python path inside `/home/peeljobs/env`. That config is not in this
repo and must be updated on the server to point at `backend/.venv/bin/gunicorn`. Flagged,
not fixed — see Risks.

### Documentation

| File | Change |
|---|---|
| `README.md:125` | `pip install -r requirements.txt` → `uv sync` |
| `SETUP.md:56` | venv + pip block → `uv sync` |
| `SETUP.md:285` | `pip install -r requirements.txt` → `uv sync` |
| `CLAUDE.md` Commands → Backend | Full block rewritten to `uv sync` / `uv run` |
| `backend/jobsp/settings_local.py:9-10` | Comments say "Install with: pip install -r dev-requirements.txt" → `uv sync` |
| `.gitignore` | Add `.venv/` (currently has `env/` and `venv/` but not `.venv/`) |

`.vscode/settings.json` references `requirements.txt` as a Copilot instruction source. Left
alone — it is editor config, not project tooling, and pointing Copilot at a deleted file
degrades gracefully. Noted so it is a conscious omission rather than an oversight.

## Dependencies

**This migration is blocked on a pre-existing bug.** `backend/api/v1/recruiter/auth_views.py:28`
imports `AcceptInvitationSerializer` from `.auth_serializers`, but commit `66513e7` removed it
from that module's re-export line. The class actually lives in
`backend/api/v1/recruiter/serializers.py:176`. `manage.py check` currently fails with an
`ImportError`, so the whole Django app will not import.

This must be fixed **first, as a separate commit**, so that `uv run manage.py check` passing
is a meaningful signal. Otherwise a migration failure is indistinguishable from the existing
breakage. The fix is to import the name from its real home rather than restoring the
re-export, which ruff would strip again on the next run.

The same commit should remove the dead expression statement left at
`backend/api/v1/recruiter/auth_views.py:475` (`serializer.validated_data['account_type']`),
another artifact of the same autofix.

## Verification

The migration is done when all of the following pass:

1. `cd backend && uv sync` completes from a clean state (no `.venv`, no `uv.lock` regeneration errors).
2. `uv run manage.py check` — exit 0, no issues. (Requires the import fix above.)
3. `uv run manage.py showmigrations --plan` reports 0 unapplied migrations, same as today.
4. `uv run manage.py runserver` starts and serves `http://localhost:8000/api/docs/`.
5. `uv run celery -A jobsp worker --loglevel=info` starts without import errors.
6. The dependency set is unchanged: `uv export --no-dev --no-hashes` diffed against the
   deleted `requirements.txt` shows the same 27 packages at the same versions, modulo
   transitive pins the lockfile now makes explicit.
7. `git grep -n "requirements.txt"` returns only historical/changelog references.

Step 6 is the load-bearing check — it is what proves this was a tooling change and not an
accidental dependency change.

## Risks

| Risk | Mitigation |
|---|---|
| **Supervisor config on the live box points into `/home/peeljobs/env`.** Deploy would restart gunicorn against a venv no longer being updated. | Out of repo scope. Must be updated server-side to `backend/.venv/bin/gunicorn` before the first uv deploy. Called out explicitly here so it is not discovered during an outage. |
| **`uv` may not be on the `peeljobs-live` runner.** | Install guard in the CI script. |
| **Dependabot stops producing backend PRs** once `requirements.txt` is gone, since it is enabled via repo settings with `pip` ecosystem detection. The 6 currently-open `dependabot/pip/backend/*` PRs will also go stale. | Accepted per scope decision. Revisit by adding `.github/dependabot.yml` with `package-ecosystem: uv` if the PR flow is missed. |
| **The 6 open dependabot PRs conflict** — they patch a file this migration deletes. | Merge or close them before migrating, whichever is preferred. Their version bumps would then need re-applying to `pyproject.toml`. |
| **`uv.lock` pins transitive dependencies that `requirements.txt` left floating.** A transitive package could resolve to a different version than what is installed in `../../env` today. | Verification step 6 surfaces this. Any diff is reviewed, not auto-accepted. |

## Open items deferred

- Whether ruff replaces `black` + `prospector`. Lint policy, not packaging.
- `.github/dependabot.yml` for the uv ecosystem.
- Dockerising the backend.
- The 27 recruiter `svelte-check` type errors — unrelated to this work, tracked separately.
