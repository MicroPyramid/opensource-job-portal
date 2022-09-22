from .settings import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

DEBUG = False

CELERY_IMPORTS = ("social.tasks", "dashboard.tasks")


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[DjangoIntegration(), CeleryIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "root": {"level": "WARNING", "handlers": ["sentry"],},
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
    },
    "handlers": {
        "sentry": {
            "level": "ERROR",
            "class": "raven.contrib.django.raven_compat.handlers.SentryHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "raven": {"level": "DEBUG", "handlers": ["console"], "propagate": False,},
        "sentry.errors": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}


GIT_BRANCH = "master"
UWSGI_FILE_NAME = "jobs_uwsgi.ini"

AWS_STORAGE_BUCKET_NAME = AWS_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_DEFAULT_ACL = "public-read"
S3_DOMAIN = AWS_S3_CUSTOM_DOMAIN = str(AWS_BUCKET_NAME) + ".s3.amazonaws.com"

LOGO = "https://%s/logo.png" % (S3_DOMAIN)

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
DEFAULT_S3_PATH = "media"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATIC_S3_PATH = "static"
COMPRESS_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_HEADERS = {
    "Expires": "Sun, 15 June 2020 20:00:00 GMT",
    "Cache-Control": "max-age=16400000",
    "public-read": True,
}

AWS_IS_GZIPPED = True
AWS_ENABLED = True
AWS_S3_SECURE_URLS = True

MEDIA_ROOT = "/%s/" % DEFAULT_S3_PATH
MEDIA_URL = "//%s/%s/" % (S3_DOMAIN, DEFAULT_S3_PATH)
STATIC_ROOT = "/%s/" % STATIC_S3_PATH
STATIC_URL = "https://%s/" % (S3_DOMAIN)
COMPRESS_URL = STATIC_URL
