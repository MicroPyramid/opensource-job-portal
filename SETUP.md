# PeelJobs - Setup Guide

A dynamic job board platform built with Django 4.2.22, PostgreSQL, Redis, and modern web technologies.

## Prerequisites

- **Python**: 3.12+
- **Node.js**: 22.x
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **Search**: Elasticsearch 7.17.6

### Install System Dependencies

```bash
# Core packages
sudo apt update && sudo apt install -y \
  git postgresql redis-server python3-dev python3-venv \
  build-essential libjpeg-dev zlib1g-dev

# Node.js 22.x
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# Elasticsearch (Docker)
docker run -d --name elasticsearch \
  -p 127.0.0.1:9200:9200 \
  -e "discovery.type=single-node" \
  docker.elastic.co/elasticsearch/elasticsearch:7.17.12

or

docker run -d --name elasticsearch \
  -p 127.0.0.1:9200:9200 \
  -e "discovery.type=single-node" \
  -e "ES_JAVA_OPTS=-Xms2g -Xmx2g" \
  --memory=8g \
  --memory-swap=8g \
  docker.elastic.co/elasticsearch/elasticsearch:7.17.6


```

## Development Setup

### 1. Project Setup

```bash
# Clone and setup
git clone <your-repo-url>
cd <repo>/backend

# Python environment — uv creates and manages .venv from pyproject.toml
# and pins the interpreter from .python-version. Dev tooling is included
# by default; use `uv sync --no-dev` to omit it.
uv sync
```

### 2. Environment Configuration

Create `.env` file:

```env
DEBUG=True
SECRET_KEY="$(openssl rand -base64 50)"
DATABASE_URL=postgresql://postgres:password@localhost/peeljobs
REDIS_URL=redis://localhost:6379/0
ELASTICSEARCH_URL=http://localhost:9200
PEEL_URL=http://localhost:8000/
DEFAULT_FROM_EMAIL=noreply@peeljobs.local
```

### 3. Database Setup

```bash
# Create database
sudo -u postgres createdb peeljobs
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'password';"

# Run migrations
uv run manage.py migrate
uv run manage.py load_initial_data
uv run manage.py createsuperuser

# (Optional) Create test data for development
uv run manage.py create_test_data
```

### 4. Test Users (Optional)

Create test users with known credentials for development:

```bash
# Create test users (loads from backend/peeldb/fixtures/test-users.json)
uv run manage.py create_test_users

# Recreate test users (delete and create fresh)
uv run manage.py create_test_users --clear

# Use custom config file
uv run manage.py create_test_users --config /path/to/custom-users.json
```

**Default test user credentials** (defined in `backend/peeldb/fixtures/test-users.json`):

| User Type     | Email                                | Password                      | Description                                    |
| ------------- | ------------------------------------ | ----------------------------- | ---------------------------------------------- |
| Superuser     | ashwin@micropyramid.com              | _auto-generated (shown once)_ | Django admin                                   |
| Company Admin | ashwin.company@micropyramid.com      | 123456                        | Company admin (is_admin=True, owns company)    |
| Recruiter     | ashwin.recruiter@micropyramid.com    | 123456                        | Company recruiter (is_admin=False, same company) |
| Individual    | ashwin.individual@micropyramid.com   | 123456                        | Independent recruiter (no company)             |
| Jobseeker     | ashwin.jobseeker@micropyramid.com    | 123456                        | Job seeker with full profile                   |

Each recruiter type creates 5 sample job posts. Customize by editing `test-users.json`.

### 5. Test Data (Optional)

For development, populate the database with bulk test data:

```bash
# Create default test data (50 companies, 100 recruiters, 500 job seekers, 1000 jobs)
uv run manage.py create_test_data

# Create custom amounts
uv run manage.py create_test_data --companies=20 --recruiters=50 --jobseekers=200 --jobs=500

# Clear existing test data and create fresh
uv run manage.py create_test_data --clear
```

Bulk test users are created with password: `testpass123`

### 6. Frontend Assets

```bash
npm install
npm run build
pnpm run watch-css
pnpm run build-css
```

## Running the Application

Start services in separate terminals:

```bash
# Django server
uv run manage.py runserver

# Celery worker
DJANGO_SETTINGS_MODULE=jobsp.settings_local uv run celery -A jobsp worker --loglevel=info

# Celery beat
DJANGO_SETTINGS_MODULE=jobsp.settings_local uv run celery -A jobsp beat --loglevel=info
```

**Access Points:**

- Main App: http://localhost:8000
- Admin: http://localhost:8000/admin/
- Schema Viewer: http://localhost:8000/schema-viewer/

## Management Scripts

| Environment | Command                   | Settings             |
| ----------- | ------------------------- | -------------------- |
| Development | `uv run manage.py`        | `settings_local.py`  |
| Production  | `uv run manage_server.py` | `settings_server.py` |

## Production Deployment

### Environment Variables

```env
DEBUG=False
SECRET_KEY="production-secret-key"
DATABASE_URL=postgresql://peeljobs_user:password@localhost/peeljobs_prod
REDIS_URL=redis://localhost:6379/1
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SENTRY_DSN=your_sentry_dsn_here
```

### Systemd Services

**Django Service** (`/etc/systemd/system/peeljobs.service`):

```ini
[Unit]
Description=PeelJobs Django Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/peeljobs/backend
Environment="PATH=/var/www/peeljobs/backend/.venv/bin"
Environment="DJANGO_SETTINGS_MODULE=jobsp.settings_server"
ExecStart=/var/www/peeljobs/backend/.venv/bin/gunicorn --workers 3 --bind unix:/run/peeljobs/peeljobs.sock jobsp.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Celery Service** (`/etc/systemd/system/peeljobs-celery.service`):

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

### Nginx Configuration

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
        # REQUIRED: settings_server.py sets SECURE_SSL_REDIRECT together with
        # SECURE_PROXY_SSL_HEADER. Without this header Django cannot tell that
        # the original request was HTTPS and will redirect in a loop.
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://unix:/run/peeljobs/peeljobs.sock;
    }
}
```

## Common Commands

```bash
# Database
uv run manage.py migrate
uv run manage.py makemigrations

# Testing
uv run manage.py test

# Static files
uv run manage.py collectstatic

# Search index
uv run manage.py update_index
```

## Troubleshooting

### Service Issues

```bash
# Check services
sudo systemctl status postgresql redis-server

# Check Elasticsearch
curl http://localhost:9200

# Check Redis
redis-cli ping
```

### Common Fixes

```bash
# Reset migrations (dev only)
uv run manage.py migrate --fake-initial

# Reinstall dependencies from the lockfile
uv sync --reinstall

# Fix permissions
sudo chown -R $USER:$USER .
```

## Technology Stack

- **Framework**: Django 5.x
- **Database**: PostgreSQL
- **Cache**: Redis + Celery 5.5.0
- **Search**: Elasticsearch 7.17.6
- **Frontend**: Bootstrap → Tailwind CSS 4.1
- **Icons**: FontAwesome → Lucide
- **Monitoring**: Sentry
