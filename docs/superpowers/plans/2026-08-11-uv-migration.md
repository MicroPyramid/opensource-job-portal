# uv + pyproject.toml Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace pip/`requirements.txt` dependency management in `backend/` with a uv-managed project using `pyproject.toml` and a committed `uv.lock`.

**Architecture:** `backend/pyproject.toml` becomes the single dependency manifest, declaring 27 runtime dependencies under `[project.dependencies]` and 8 dev dependencies under a PEP 735 `[dependency-groups] dev` group. No `[build-system]` is declared, so uv treats the project as a non-package ("virtual") project — it installs dependencies into `backend/.venv` without building or installing the project itself. `uv run` replaces manual venv activation everywhere.

**Tech Stack:** uv 0.12.1, Python 3.12, Django 5.2.10, PEP 621 project metadata, PEP 735 dependency groups.

## Global Constraints

- `requires-python = ">=3.12"`; `backend/.python-version` contains exactly `3.12`.
- All 34 existing version pins (27 runtime + 7 dev) carry over **byte-identical**. No version may change.
- `ruff==0.16.2` is the only permitted addition, to the `dev` group.
- Comment groupings from `requirements.txt` are preserved inline in `pyproject.toml`.
- `[build-system]` must NOT be declared. `[tool.uv] package = false` must be.
- `uv.lock` is committed. `backend/.venv/` is gitignored.
- Deploy uses `uv sync --locked --no-dev` — never `--frozen`, never with dev deps.
- Spec: `docs/superpowers/specs/2026-08-11-uv-migration-design.md`

---

### Task 1: Unblock verification — fix the broken recruiter serializer import

The migration's success gate is `manage.py check` passing. It currently fails with an
`ImportError` unrelated to packaging, introduced by commit `66513e7`. Until this is fixed, a
migration failure is indistinguishable from the pre-existing breakage. This is a standalone
bug fix and gets its own commit.

**Files:**
- Modify: `backend/api/v1/recruiter/auth_views.py:16-31` (import block), `:475` (dead statement)

**Interfaces:**
- Consumes: nothing.
- Produces: a green `python manage.py check`, which every later task depends on as its gate.

- [ ] **Step 1: Reproduce the failure**

Run: `cd backend && source ../../env/bin/activate && python manage.py check`
Expected: FAIL — `ImportError: cannot import name 'AcceptInvitationSerializer' from 'api.v1.recruiter.auth_serializers'`

- [ ] **Step 2: Confirm where the class actually lives**

Run: `grep -n "class AcceptInvitationSerializer" backend/api/v1/recruiter/*.py`
Expected: exactly one hit — `backend/api/v1/recruiter/serializers.py:176`

- [ ] **Step 3: Move the import to the real module**

Remove `AcceptInvitationSerializer,` from the `from .auth_serializers import (...)` block and
add a separate import. Do NOT restore the re-export in `auth_serializers.py` — ruff's
unused-import rule would strip it again on the next run.

```python
from .auth_serializers import (
    RegisterSerializer,
    LoginSerializer,
    VerifyEmailSerializer,
    ResendVerificationSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    GoogleAuthUrlSerializer,
    GoogleCallbackSerializer,
    GoogleCompleteSerializer,
    UserSerializer,
    UpdateProfileSerializer
)
from .serializers import AcceptInvitationSerializer
```

- [ ] **Step 4: Remove the dead expression statement**

`backend/api/v1/recruiter/auth_views.py:475` is a no-op left by the same autofix — ruff
removed the assignment target but kept the subscript expression.

```python
# before
        redirect_uri = serializer.validated_data['redirect_uri']
        serializer.validated_data['account_type']

# after
        redirect_uri = serializer.validated_data['redirect_uri']
```

- [ ] **Step 5: Verify the fix**

Run: `cd backend && source ../../env/bin/activate && python manage.py check`
Expected: PASS — `System check identified no issues (0 silenced).`

- [ ] **Step 6: Commit**

```bash
git add backend/api/v1/recruiter/auth_views.py
git commit -m "fix: import AcceptInvitationSerializer from its defining module"
```

---

### Task 2: Create the uv project and prove dependency parity

**Files:**
- Create: `backend/pyproject.toml`, `backend/.python-version`, `backend/uv.lock`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: green `manage.py check` from Task 1.
- Produces: `backend/.venv` managed by uv; `uv run <cmd>` as the execution entrypoint for all later tasks.

- [ ] **Step 1: Pin the interpreter**

```bash
cd backend && echo "3.12" > .python-version
```

- [ ] **Step 2: Write `backend/pyproject.toml`**

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

`[build-system]` is deliberately absent — that is what makes uv treat this as a non-package
project. `package = false` states the same intent explicitly rather than leaving it to
inference.

- [ ] **Step 3: Resolve and create the environment**

Run: `cd backend && uv sync`
Expected: `uv.lock` created, `.venv` created, all packages resolved with no conflicts.

- [ ] **Step 4: Gate — Django must still import**

Run: `cd backend && uv run manage.py check`
Expected: PASS — `System check identified no issues (0 silenced).`

- [ ] **Step 5: Gate — prove the runtime dependency set is unchanged**

This is the load-bearing check. It is what proves this was a tooling change and not an
accidental dependency change.

A naive `grep -E '^[a-zA-Z0-9._-]+=='` silently drops the two bracketed-extra lines
(`psycopg[binary]`, `sentry-sdk[django]`) and would report a false pass on 25 of 27 deps.
Strip the extras from the name before comparing:

```bash
cd backend
grep -vE '^\s*#|^\s*$' requirements.txt | sed 's/#.*//' | tr -d ' ' | sort > /tmp/pip-all.txt
fail=0
while read -r line; do
  name="${line%%[[=]*}"; ver="${line##*==}"
  got=$(uv export --no-dev --no-hashes 2>/dev/null \
        | grep -iE "^${name}(\[[^]]*\])?==" | head -1 | sed 's/;.*//' | tr -d ' ')
  gotver="${got##*==}"
  if [ "$gotver" = "$ver" ]; then printf "  OK   %-40s %s\n" "$name" "$ver"
  else printf "  FAIL %-40s declared=%s resolved=%s\n" "$name" "$ver" "${gotver:-MISSING}"; fail=1; fi
done < /tmp/pip-all.txt
[ $fail -eq 0 ] && echo "PARITY CONFIRMED" || echo "PARITY FAILED"
```

Expected: `PARITY CONFIRMED`, with all 27 declared runtime deps listed `OK`. The uv export
contains ~69 lines total; the surplus are transitive dependencies the lockfile now pins
explicitly, which is expected and correct.

Note that the hand-built `../../env` venv is NOT a valid reference point for this check — it
had drifted from `requirements.txt` on 20 of 27 packages (Django 5.2.2 vs declared 5.2.10,
simplejwt absent entirely). Compare against the declared pins, not against what happens to
be installed.

- [ ] **Step 6: Gate — unapplied migrations are enumerated and explained**

Run: `cd backend && uv run manage.py showmigrations --plan | grep '^\[ \]'`

Expected: exactly two, both explainable and neither caused by the migration:

- `peeldb.0072_remove_facebook_github_models` — pre-existing. Arrived with upstream PR #211
  and is unapplied under the old venv too.
- `token_blacklist.0013_alter_blacklistedtoken_options_and_more` — appears because uv
  installs the *declared* `djangorestframework-simplejwt==5.5.1`, while the hand-built
  `../../env` venv was still on 5.5.0 (which ships one fewer migration). uv is correct;
  the old venv had drifted.

Any migration outside these two is a FAILURE and must be explained before proceeding.

**Do not apply these migrations as part of this task.** `0072` drops tables. Applying it is
a database decision for the repository owner, not a step in a packaging migration.

- [ ] **Step 7: Gitignore the uv venv**

`.gitignore` has `env/` and `venv/` but not `.venv/`, the directory uv creates.

```
.venv/
```

- [ ] **Step 8: Commit**

```bash
git add backend/pyproject.toml backend/uv.lock backend/.python-version .gitignore
git commit -m "build: add uv project manifest and lockfile"
```

---

### Task 3: Remove the pip-era manifests

Kept separate from Task 2 so that the additive change and the destructive change are
independently reviewable and independently revertible.

**Files:**
- Delete: `backend/requirements.txt`, `backend/dev-requirements.txt`, `backend/setup.py`

**Interfaces:**
- Consumes: verified parity from Task 2 Step 5.
- Produces: `pyproject.toml` as the sole dependency manifest.

- [ ] **Step 1: Confirm `setup.py` is genuinely unreferenced**

Run: `grep -rn "setup\.py" --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=__pycache__ .`
Expected: only the self-referential comment inside `backend/setup.py` itself. `setup.py` also
opens `README.rst`, which does not exist — it crashes if invoked. Confirm with:
`ls backend/README.rst` → No such file.

- [ ] **Step 2: Delete the three files**

```bash
git rm backend/requirements.txt backend/dev-requirements.txt backend/setup.py
```

- [ ] **Step 3: Gate — nothing broke**

Run: `cd backend && uv run manage.py check`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git commit -m "build: remove requirements.txt, dev-requirements.txt and dead setup.py"
```

---

### Task 4: Fix the GitLab deploy pipeline

The pipeline is already broken independently of this migration: it runs
`pip install pipenv && pipenv install -d` against a Pipfile deleted in `8fac0de`.

**Files:**
- Modify: `.gitlab-ci.yml:8-16`

**Interfaces:**
- Consumes: `uv.lock` committed in Task 2.
- Produces: a deploy that installs from the lockfile with dev dependencies excluded.

- [ ] **Step 1: Replace the script block**

```yaml
  script:
    - sudo /bin/rm -rf /home/peeljobs/peeljobs/; cp -r . /home/peeljobs/peeljobs
    - cd /home/peeljobs/peeljobs/backend
    - command -v uv || curl -LsSf https://astral.sh/uv/install.sh | sh
    - uv sync --locked --no-dev
    - uv run manage_server.py migrate --noinput
    - sudo /usr/bin/supervisorctl restart all
```

Three deliberate changes beyond the tooling swap:
- `source /home/peeljobs/env/bin/activate` is dropped — uv manages `backend/.venv` itself.
- `--locked` not `--frozen`: `--frozen` uses the lockfile without validating it against
  `pyproject.toml`, so a forgotten `uv lock` would silently deploy stale dependencies.
- `--no-dev` keeps black/prospector/bpython/debug-toolbar off production. The previous
  `pipenv install -d` explicitly installed them there.

- [ ] **Step 2: Gate — YAML is valid**

Run: `python3 -c "import yaml,sys; yaml.safe_load(open('.gitlab-ci.yml')); print('valid')"`
Expected: `valid`

- [ ] **Step 3: Commit**

```bash
git add .gitlab-ci.yml
git commit -m "ci: deploy with uv sync --locked instead of dead pipenv invocation"
```

---

### Task 5: Update documentation

**Files:**
- Modify: `README.md:125`, `SETUP.md:56`, `SETUP.md:285`, `CLAUDE.md` (Commands → Backend), `backend/jobsp/settings_local.py:9-10`

**Interfaces:**
- Consumes: the command table from the design doc.
- Produces: no remaining instruction to run pip in this repo.

- [ ] **Step 1: Rewrite the setup blocks**

Every `python3 -m venv` + `source .../activate` + `pip install -r requirements.txt` sequence
collapses to:

```bash
cd backend/
uv sync
```

- [ ] **Step 2: Rewrite the run commands**

| Before | After |
|---|---|
| `python manage.py migrate` | `uv run manage.py migrate` |
| `python manage.py runserver` | `uv run manage.py runserver` |
| `python manage_server.py runserver` | `uv run manage_server.py runserver` |
| `celery -A jobsp worker --loglevel=info` | `uv run celery -A jobsp worker --loglevel=info` |
| `celery -A jobsp beat --loglevel=info` | `uv run celery -A jobsp beat --loglevel=info` |
| `python manage.py rebuild_index` | `uv run manage.py rebuild_index` |

- [ ] **Step 3: Fix the stale dev-install comments**

`backend/jobsp/settings_local.py:9-10` reads `# Install with: pip install -r dev-requirements.txt`
for the commented-out `schema_viewer` and `behave_django` apps. Both are now in the `dev`
group, which `uv sync` installs by default, so the comment becomes:

```python
    # "schema_viewer",  # Installed by: uv sync
    # "behave_django",  # Installed by: uv sync
```

- [ ] **Step 4: Gate — no pip instructions remain**

Run: `git grep -n "requirements.txt\|pip install" -- . ':!docs/superpowers'`
Expected: only `.vscode/settings.json` (editor config, consciously out of scope per the spec).

- [ ] **Step 5: Commit**

```bash
git add README.md SETUP.md CLAUDE.md backend/jobsp/settings_local.py
git commit -m "docs: replace pip workflow with uv across setup and run instructions"
```

---

### Task 6: End-to-end verification

Runs the spec's full acceptance list against a genuinely clean environment. Nothing is
committed here; this task either passes or sends earlier tasks back.

- [ ] **Step 1: Clean-slate sync**

```bash
cd backend && rm -rf .venv && uv sync
```
Expected: completes with no resolution errors.

- [ ] **Step 2: Django check**

Run: `cd backend && uv run manage.py check`
Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 3: Migrations**

Run: `cd backend && uv run manage.py showmigrations --plan | grep -c '^\[ \]'`
Expected: `0`

- [ ] **Step 4: Server boots and serves the API docs**

```bash
cd backend && uv run manage.py runserver 8000 &
sleep 8
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/docs/
kill %1
```
Expected: `200`

- [ ] **Step 5: Celery worker imports cleanly**

```bash
cd backend && timeout 20 uv run celery -A jobsp worker --loglevel=info 2>&1 | head -30
```
Expected: banner prints and tasks register; no `ImportError` / `ModuleNotFoundError`. A
broker connection failure is acceptable if Redis is not running locally — the gate is import
health, not connectivity.

- [ ] **Step 6: Dev group is present**

Run: `cd backend && uv run ruff --version && uv run black --version`
Expected: `ruff 0.16.2` and a black version banner — proves the `dev` group syncs by default.

- [ ] **Step 7: Report for code review**

Summarise: files added/removed, the parity diff result from Task 2 Step 5, every gate's
outcome, and the two out-of-repo risks (live-box supervisor config, dependabot).

---

## Out of scope — flagged, not fixed

- **Supervisor config on the live box** almost certainly points into `/home/peeljobs/env`.
  It must be repointed at `backend/.venv/bin/gunicorn` server-side before the first uv deploy.
  Not in this repo.
- **Dependabot** will stop producing backend PRs once `requirements.txt` is gone. The 6 open
  `dependabot/pip/backend/*` PRs patch a deleted file and should be merged or closed.
- **The 27 recruiter `svelte-check` errors** — unrelated to this work.
- **Whether ruff replaces black + prospector** — lint policy, not packaging.
