# Test Data

Three separate things, in increasing order of how much they create.

## 1. Initial data (needed by everyone)

```bash
cd backend
uv run manage.py load_initial_data
```

Loads eight fixtures in dependency order: countries, states, cities, skills,
industries, qualifications, functional areas, languages.

This is reference data, not sample content — location and skill pickers are
empty without it, and job posting will not work properly. Run it once after
`migrate`.

## 2. Named test users (recommended for development)

```bash
uv run manage.py create_test_users
```

Creates one user of each role with predictable credentials, defined in
`backend/peeldb/fixtures/test-users.json`.

| Role | Email | Password |
| --- | --- | --- |
| Superuser | `ashwin@micropyramid.com` | auto-generated, printed once |
| Company Admin | `ashwin.company@micropyramid.com` | `123456` |
| Recruiter | `ashwin.recruiter@micropyramid.com` | `123456` |
| Individual recruiter | `ashwin.individual@micropyramid.com` | `123456` |
| Job seeker | `ashwin.jobseeker@micropyramid.com` | `123456` |

Each recruiter-type user gets five sample job posts, which is enough to
exercise the dashboard.

The Company Admin and Recruiter share a company — that pairing is what you want
for testing permissions, since it is the only way to check that a recruiter
cannot edit another recruiter's postings. The Individual recruiter has no
company at all.

| Flag | Effect |
| --- | --- |
| `--clear` | Delete the existing test users and recreate them |
| `--config PATH` | Use a different JSON definition file |

!!! warning "Development only"

    These are hardcoded, publicly documented credentials. Never run this
    against an internet-reachable deployment.

## 3. Bulk sample data (for realistic volume)

```bash
uv run manage.py create_test_data
```

Generates data at a volume where pagination, search ranking and dashboard
queries behave like production.

| Flag | Default |
| --- | --- |
| `--companies` | 50 |
| `--recruiters` | 100 |
| `--jobseekers` | 500 |
| `--jobs` | 1000 |
| `--applications` | 3000 |
| `--clear` | off |

```bash
# Smaller, faster dataset
uv run manage.py create_test_data --companies=20 --recruiters=50 \
  --jobseekers=200 --jobs=500

# Wipe and regenerate
uv run manage.py create_test_data --clear
```

Bulk users are created with the password `testpass123`.

Generating the default 1000 jobs also populates the full-text search column for
each — it is a generated column maintained by PostgreSQL on write, so there is
no separate indexing step. See [Search](../architecture/search.md).

## Order of operations

```bash
uv run manage.py migrate
uv run manage.py load_initial_data     # reference data — always
uv run manage.py createsuperuser       # or use create_test_users instead
uv run manage.py create_test_users     # optional: predictable logins
uv run manage.py create_test_data      # optional: volume
```

`load_initial_data` must run before either test-data command, because generated
jobs reference real cities and skills.
