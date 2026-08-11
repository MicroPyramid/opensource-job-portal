import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
#
# This deliberately defaults to the production-safe base module rather than
# settings_local: the production worker is started by supervisor, whose config
# lives outside this repo and may not set DJANGO_SETTINGS_MODULE. Defaulting to
# a development module would silently give production the console email backend
# -- the exact failure this file's sibling settings.py used to cause.
#
# For local development, select the dev module explicitly:
#   DJANGO_SETTINGS_MODULE=jobsp.settings_local uv run celery -A jobsp worker
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobsp.settings")

app = Celery("jobsp")

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
