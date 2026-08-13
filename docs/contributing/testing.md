# Testing

## Running tests

```bash
cd backend

uv run manage.py test                    # everything
uv run manage.py test api.v1.jobs        # one module
uv run manage.py test api.v1.jobs.tests.JobSearchTests
```

Tests use `jobsp.settings_local` and run against a throwaway PostgreSQL
database Django creates and drops. Your development data is untouched, but the
role in `DB_USER` needs permission to create databases.

There is no `TEST_RUNNER` override. It briefly pointed at a BDD runner that was
never a dependency, and later at a search-indexing runner that existed only to
disconnect the Haystack signal processor. Both are gone; the Django default is
correct.

!!! note "No Elasticsearch, ever"

    If a test failure mentions Elasticsearch, Haystack, or a search index,
    something stale is being run — nothing in the project uses them. Search is
    PostgreSQL, maintained by the database on write. Do not start
    Elasticsearch.

## Layout

Tests sit beside the code:

```
api/v1/alerts/tests.py
api/v1/auth/tests.py
api/v1/common/tests.py
api/v1/jobs/tests.py
api/v1/profile/tests.py
api/v1/recruiter/tests.py
api/v1/webhooks/tests.py
dashboard/tests.py
mp_celery_monitor/tests.py
tickets/tests.py
```

## Coverage

```bash
uv run coverage run manage.py test
uv run coverage report
uv run coverage html      # htmlcov/index.html
```

## What to test

Cover behaviour, not implementation. For an API change that means the
happy path, permissions (can the wrong user reach it?), validation failures,
and any filtering or ordering the endpoint promises.

Search is worth calling out. `api/v1/jobs/tests.py:JobSearchTests` asserts
things that are easy to regress silently:

- word-order-independent matching
- a title match outranking a description match
- stemming (`manager` finding "management")
- unrelated jobs being excluded
- the typo fallback firing
- the fuzzy fallback **not** firing when full-text search already matched
- nonsense returning nothing
- an empty search returning everything
- an explicit `?ordering=` beating relevance ordering
- search composing with other filters
- an edited job being immediately searchable

That last one guards the generated column: it proves nothing needs reindexing.

## Writing tests

Use `setUpTestData` for fixtures shared across a test case — it runs once per
class rather than per test.

```python
class JobSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        ...
```

Assert on meaningful values rather than counts alone. `assertEqual(len(x), 3)`
passes for the wrong three results.

API tests hitting the test client need hosts allowed:

```python
from django.test import TestCase, override_settings

@override_settings(ALLOWED_HOSTS=["*"])
class MyAPITests(TestCase):
    ...
```

`ALLOWED_HOSTS` is a literal list in `jobsp/settings.py` that does not include
`testserver`, so without this the client raises `DisallowedHost`.

## Before opening a PR

```bash
cd backend
uv run manage.py test
uv run manage.py check
uv run manage.py makemigrations --check --dry-run   # no model drift
uv run ruff check .
uv run ruff format --check .
```

Frontend:

```bash
cd site      # and recruiter/
pnpm check
```

Docs:

```bash
mkdocs build --strict
```
