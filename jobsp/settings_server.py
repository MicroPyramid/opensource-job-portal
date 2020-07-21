from .settings import *

DEBUG = False

CELERY_IMPORTS = ("social.tasks", "dashboard.tasks")

# Set your DSN value
RAVEN_CONFIG = {
    "dsn": os.getenv("RAVEN_CONFIG_DSN"),
}

# Add raven to the list of installed apps
INSTALLED_APPS = INSTALLED_APPS + (
    # ...
    "raven.contrib.django.raven_compat",
    # 'elasticapm.contrib.django',
)
ELASTIC_APM = {
    "APP_NAME": os.getenv("ELASTIC_APM_APP_NAME"),
    "SECRET_TOKEN": os.getenv("ELASTIC_APM_SECRET_TOKEN"),
}

MIDDLEWARE = [
    "raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware",
    "raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware",
    # 'elasticapm.contrib.django.middleware.TracingMiddleware',
] + MIDDLEWARE

MIDDLEWARE_CLASSES = MIDDLEWARE

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


INTERNAL_IPS = ("127.0.0.1", "183.82.113.154")
# DEBUG_TOOLBAR_PATCH_SETTINGS = False
# DEBUG_TOOLBAR_PANELS = [
#     'debug_toolbar.panels.versions.VersionsPanel',
#     'debug_toolbar.panels.timer.TimerPanel',
#     'debug_toolbar.panels.settings.SettingsPanel',
#     'debug_toolbar.panels.headers.HeadersPanel',
#     'debug_toolbar.panels.request.RequestPanel',
#     'debug_toolbar.panels.sql.SQLPanel',
#     'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#     'debug_toolbar.panels.templates.TemplatesPanel',
#     'debug_toolbar.panels.cache.CachePanel',
#     'debug_toolbar.panels.signals.SignalsPanel',
#     'debug_toolbar.panels.logging.LoggingPanel',
#     'debug_toolbar.panels.redirects.RedirectsPanel',
# ]

INACTIVE_MAIL_SENDER = os.getenv("INACTIVEMAILSENDER")
MAIL_SENDER = os.getenv("MAILSENDER")

GIT_BRANCH = "master"
UWSGI_FILE_NAME = "jobs_uwsgi.ini"
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWSS3CUSTOMDOMAIN")
