from .settings import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = False

CELERY_IMPORTS = ("social.tasks", "dashboard.tasks")


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "root": {
        "level": "WARNING",
        "handlers": ["sentry"],
    },
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
        "raven": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "sentry.errors": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}


GIT_BRANCH = "master"
UWSGI_FILE_NAME = "jobs_uwsgi.ini"
AWS_S3_CUSTOM_DOMAIN = "d2pt99vxm3n8bc.cloudfront.net"


INSTALLED_APPS = INSTALLED_APPS + ("anymail",)

ANYMAIL = {
    "AMAZON_SES_CLIENT_PARAMS": {
        # example: override normal Boto credentials specifically for Anymail
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_FOR_ANYMAIL_SES"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_KEY_FOR_ANYMAIL_SES"),
        "region_name": os.getenv("AWS_LOCATION_FOR_ANYMAIL_SES"),
        # override other default options
        "config": {
            "connect_timeout": 30,
            "read_timeout": 30,
        },
    },
}

EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
