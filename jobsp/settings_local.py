# Local development settings
# This file contains settings that should only be used in local development
# and not on production servers.

from .settings import *

# Development-specific installed apps
LOCAL_INSTALLED_APPS = [
    "schema_viewer",
    "behave_django",
    # Uncomment the following for debug toolbar support
    # "debug_toolbar",
    # "template_profiler_panel",
    # Add other development-only apps here
]

# Add local apps to INSTALLED_APPS
INSTALLED_APPS = INSTALLED_APPS + tuple(LOCAL_INSTALLED_APPS)

# Development-specific middleware (uncomment if using debug toolbar)
# LOCAL_MIDDLEWARE = [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]
# MIDDLEWARE = LOCAL_MIDDLEWARE + MIDDLEWARE

# Development-specific settings
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Use console email backend for local development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Test runner for BDD tests
TEST_RUNNER = "django_behave.runner.DjangoBehaveTestSuiteRunner"

# Internal IPs for debug toolbar and other dev tools
INTERNAL_IPS = ("127.0.0.1", "localhost")

# Debug toolbar panels (uncomment if using debug toolbar)
# DEBUG_TOOLBAR_PANELS = [
#     "debug_toolbar.panels.versions.VersionsPanel",
#     "debug_toolbar.panels.timer.TimerPanel",
#     "debug_toolbar.panels.settings.SettingsPanel",
#     "debug_toolbar.panels.headers.HeadersPanel",
#     "debug_toolbar.panels.request.RequestPanel",
#     "debug_toolbar.panels.sql.SQLPanel",
#     "debug_toolbar.panels.staticfiles.StaticFilesPanel",
#     "debug_toolbar.panels.templates.TemplatesPanel",
#     "debug_toolbar.panels.cache.CachePanel",
#     "debug_toolbar.panels.signals.SignalsPanel",
#     "debug_toolbar.panels.logging.LoggingPanel",
#     "debug_toolbar.panels.redirects.RedirectsPanel",
#     "debug_toolbar.panels.profiling.ProfilingPanel",
#     "template_profiler_panel.panels.template.TemplateProfilerPanel",
# ]

# Local database settings (if different from main settings)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'peeljobs_local',
#         'USER': 'your_db_user',
#         'PASSWORD': 'your_db_password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Development-specific middleware (if needed)
# LOCAL_MIDDLEWARE = [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]
# MIDDLEWARE = LOCAL_MIDDLEWARE + MIDDLEWARE

# Internal IPs for debug toolbar and other dev tools
INTERNAL_IPS = ("127.0.0.1", "localhost")

# Additional logging for development
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}
    },
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        },
        "standard": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Local-specific cache settings (if different)
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'unique-snowflake',
#     }
# }

# Development-specific static/media settings
# Use local file storage instead of S3 for development
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# Override S3 storage settings for local development
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Uncomment if you want different paths for local development
# STATIC_ROOT = os.path.join(BASE_DIR, "local_static")
# MEDIA_ROOT = os.path.join(BASE_DIR, "local_media")

# Disable any production-specific optimizations
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

# Local celery settings (if different)
# CELERY_TASK_ALWAYS_EAGER = True  # Execute tasks synchronously for testing
# CELERY_TASK_EAGER_PROPAGATES = True

# Additional development tools settings
# DJANGO_EXTENSIONS = True  # if using django-extensions

print("Local development settings loaded")
