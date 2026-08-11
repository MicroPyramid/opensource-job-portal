import sentry_sdk

from .settings import *

# from sentry_sdk.integrations.django import DjangoIntegration
# from sentry_sdk.integrations.celery import CeleryIntegration

DEBUG = False
# Set explicitly rather than inherited: TEMPLATE_DEBUG previously came from
# settings_local via the base module and stayed True in production.
TEMPLATE_DEBUG = DEBUG

CELERY_IMPORTS = "dashboard.tasks"

# Cookie Domain Configuration for Cross-Subdomain Auth
# Allows cookies to be shared between peeljobs.com and recruiter.peeljobs.com
SESSION_COOKIE_DOMAIN = ".peeljobs.com"  # Note: leading dot is important
CSRF_COOKIE_DOMAIN = ".peeljobs.com"

# Ensure cookies are secure in production
SESSION_COOKIE_SECURE = True  # Only send over HTTPS
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# --- Transport security -----------------------------------------------------
#
# DEPLOYMENT PREREQUISITE: nginx terminates TLS and proxies to gunicorn over
# HTTP, so Django cannot see the original scheme by itself. SECURE_SSL_REDIRECT
# below relies on SECURE_PROXY_SSL_HEADER, which in turn requires nginx to send:
#
#     proxy_set_header X-Forwarded-Proto $scheme;
#
# The nginx config is not in this repo. If that header is missing, Django sees
# every request as plain HTTP and will redirect forever. Add the header before
# deploying this change.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True

# HSTS: one year, applied to subdomains (recruiter.peeljobs.com etc., which
# already share cookies via the .peeljobs.com domain above). Reversible by
# lowering max-age and waiting it out.
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# SECURE_HSTS_PRELOAD is deliberately left off. Turning it on is an invitation
# to submit peeljobs.com to the browsers' built-in preload lists, which is
# effectively irreversible and would make every subdomain HTTPS-only for users
# who have never visited the site. That is a decision for the domain owner, not
# a lint fix, so `check --deploy` will keep reporting security.W022 until
# someone makes it deliberately.


# sentry_sdk.init(
#     dsn=os.getenv("SENTRY_DSN"),
#     integrations=[DjangoIntegration(), CeleryIntegration()],
#     traces_sample_rate=1.0,
#     send_default_pii=True,
# )

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    # Add data like request headers and IP for users;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "root": {
        "level": "WARNING",
        "handlers": ["console"],  # Changed from ["sentry"]
    },
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
    },
    "handlers": {
        # "sentry": {
        #     "level": "ERROR",
        #     "class": "raven.contrib.django.raven_compat.handlers.SentryHandler",
        # },
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

AWS_STORAGE_BUCKET_NAME = AWS_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_DEFAULT_ACL = "public-read"
S3_DOMAIN = AWS_S3_CUSTOM_DOMAIN = str(AWS_BUCKET_NAME) + ".s3.amazonaws.com"

LOGO = f"https://{S3_DOMAIN}/logo.png"

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

MEDIA_ROOT = f"/{DEFAULT_S3_PATH}/"
MEDIA_URL = f"//{S3_DOMAIN}/{DEFAULT_S3_PATH}/"
STATIC_ROOT = f"/{STATIC_S3_PATH}/"
STATIC_URL = f"https://{S3_DOMAIN}/"
COMPRESS_URL = STATIC_URL
