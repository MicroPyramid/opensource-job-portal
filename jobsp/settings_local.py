from .settings import *

DEBUG = True

HTML_MINIFY = False
HTTP_HOST = "test.peeljobs.com:8000"
GOOGLE_OAUTH2_REDIRECT = "http://localhost:8000/oauth2callback/"

# #Set your DSN value
# RAVEN_CONFIG = {
#     'dsn': 'http://cd6fb0e6ed94463fb15f3caee2d879f0:2e5df9dc941d40a1bea79ce22f1935d9@sentry.micropyramid.com/42',
# }
# DEBUG_TOOLBAR_PANELS = [
#     'debug_toolbar.panels.sql.SQLPanel',
#     'template_timings_panel.panels.TemplateTimings.TemplateTimings',
# ]

# Add raven to the list of installed apps
INSTALLED_APPS = INSTALLED_APPS + (
    # ...
    # 'raven.contrib.django.raven_compat',
    "debug_toolbar",
    "template_timings_panel",
    "django_web_profiler",
    "behave_django",
)

MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware",] + MIDDLEWARE
MIDDLEWARE_CLASSES = MIDDLEWARE
# MIDDLEWARE_CLASSES = (
#   'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
#   'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
# ) + MIDDLEWARE_CLASSES


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        },
        "standard": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            # 'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        # 'file_log': {
        #     'level':'DEBUG',
        #     'class':'logging.handlers.TimedRotatingFileHandler',
        #     'filename': BASE_DIR + '/logs/django_dev.log',
        #     'when': 'S', # this specifies the interval
        #     'interval': 5, # defaults to 1, only necessary for other values
        #     # 'maxBytes': 1024*1024*5,# 5 MB
        #     'backupCount': 5,
        #     'formatter':'standard',
        # }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        # 'request-logging': {
        #     'level': 'DEBUG',
        #     'handlers': ['file_log'],
        #     'propagate': False,
        # },
    },
}

INTERNAL_IPS = ("127.0.0.1", "183.82.113.154")

DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "template_timings_panel.panels.TemplateTimings.TemplateTimings",
]

MAIL_SENDER = ""
INACTIVE_MAIL_SENDER = ""

TEST_RUNNER = "django_behave.runner.DjangoBehaveTestSuiteRunner"


AWS_STORAGE_BUCKET_NAME = os.getenv("AWSSTORAGEBUCKETNAME")
AM_ACCESS_KEY = AWS_ACCESS_KEY_ID = os.getenv("AMACCESSKEY")
AM_PASS_KEY = AWS_SECRET_ACCESS_KEY = os.getenv("AMPASSKEY")

CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONTDOMAIN")
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWSS3CUSTOMDOMAIN")
CLOUDFRONT_ID = os.getenv("CLOUDFRONTID")
