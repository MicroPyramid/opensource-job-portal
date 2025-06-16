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
  docker.elastic.co/elasticsearch/elasticsearch:7.17.6

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
cd <repo>

# Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
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
python manage.py migrate
python manage.py loaddata industries qualification skills countries states cities
python manage.py createsuperuser
```

### 4. Frontend Assets

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
python manage.py runserver

# Celery worker
celery -A jobsp worker --loglevel=info

# Celery beat
celery -A jobsp beat --loglevel=info
```

**Access Points:**
- Main App: http://localhost:8000
- Admin: http://localhost:8000/admin/
- Schema Viewer: http://localhost:8000/schema-viewer/

## Management Scripts

| Environment | Command | Settings |
|-------------|---------|----------|
| Development | `python manage.py` | `settings_local.py` |
| Production | `python manage_server.py` | `settings_server.py` |

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
WorkingDirectory=/var/www/peeljobs
Environment="PATH=/var/www/peeljobs/venv/bin"
ExecStart=/var/www/peeljobs/venv/bin/gunicorn --workers 3 --bind unix:/run/peeljobs/peeljobs.sock jobsp.wsgi:application
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
WorkingDirectory=/var/www/peeljobs
Environment="PATH=/var/www/peeljobs/venv/bin"
ExecStart=/var/www/peeljobs/venv/bin/celery -A jobsp worker --loglevel=info
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
        proxy_pass http://unix:/run/peeljobs/peeljobs.sock;
    }
}
```

## Common Commands

```bash
# Database
python manage.py migrate
python manage.py makemigrations

# Testing
python manage.py test

# Static files
python manage.py collectstatic

# Search index
python manage.py update_index
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
python manage.py migrate --fake-initial

# Reinstall requirements
pip install -r requirements.txt

# Fix permissions
sudo chown -R $USER:$USER .
```

## Technology Stack

- **Framework**: Django 4.2.22
- **Database**: PostgreSQL
- **Cache**: Redis + Celery 5.5.0
- **Search**: Elasticsearch 7.17.6
- **Frontend**: Bootstrap → Tailwind CSS 4.1
- **Icons**: FontAwesome → Lucide
- **Monitoring**: Sentry
