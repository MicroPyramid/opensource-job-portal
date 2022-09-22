import os

from celery.schedules import crontab
from corsheaders.defaults import default_headers, default_methods
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = os.getenv("DEBUG", True)
TEMPLATE_DEBUG = DEBUG

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "support@peeljobs.com")

CONTACT_NUMBER = os.getenv("CONTACT_NUMBER", "850 009 9499")

PEEL_URL = os.getenv("PEEL_URL", "http://peeljobs.com/")

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
CELERY_IMPORTS = ("social.tasks", "dashboard.tasks", "recruiter.tasks")

# stackoverflow app
SOF_APP_ID = os.getenv("SOFAPPID")
SOF_APP_SECRET = os.getenv("SOFAPPSECRET")
SOF_APP_KEY = os.getenv("SOFAPPKEY")

broker_api = os.getenv("BROKER_API", "http://guest:guest@localhost:15672/api/")

# Enable debug logging

logging = "DEBUG"

GIT_APP_ID = os.getenv("GITAPPID")
GIT_APP_SECRET = os.getenv("GITAPPSECRET")

ALLOWED_HOSTS = ["peeljobs.com", "test.peeljobs.com", "localhost", "127.0.0.1"]

# tw app
tw_oauth_token_secret = os.getenv("twoauthtokensecret")
tw_oauth_token = os.getenv("twoauthtokensecret")

TW_APP_KEY = os.getenv("TWAPPKEY")
TW_APP_SECRET = os.getenv("TWAPPSECRET")
OAUTH_TOKEN = os.getenv("OAUTHTOKEN")
OAUTH_SECRET = os.getenv("OAUTHSECRET")

PJ_TW_APP_KEY = os.getenv("PJTWAPPKEY")
PJ_TW_APP_SECRET = os.getenv("PJTWAPPSECRET")

# fb app
FB_APP_ID = os.getenv("FACEBOOK_APP_ID")
FB_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FB_PEELJOBS_PAGEID = os.getenv("FBPEELJOBSPAGEID")

# google app
GOOGLE_CLIENT_ID = GOOGLE_OAUTH2_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = GOOGLE_OAUTH2_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_LOGIN_HOST = os.getenv("GOOGLE_LOGIN_HOST")

# ln app
LN_API_KEY = os.getenv("LNAPIKEY")
LN_SECRET_KEY = os.getenv("LNSECRETKEY")
LN_OAUTH_USER_TOKEN = os.getenv("LNOAUTHUSERTOKEN")
LN_OAUTH_USER_SECRET = os.getenv("LNOAUTHUSERSECRET")
LN_COMPANYID = os.getenv("LNCOMPANYID")

# re-captcha
RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHAPUBLICKEY")
RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHAPRIVATEKEY")
RECAPTCHA_USE_SSL = True

# Make this unique, and don"t share it with anybody.
SECRET_KEY = os.getenv("SECRET_KEY")

ADMINS = (
    # ("Your Name", "your_email@example.com"),
)

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}


TIME_ZONE = "Asia/Calcutta"

LANGUAGE_CODE = "en-us"

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = False


# List of finder classes that know how to find static files in various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "compressor.finders.CompressorFinder",
)

HTML_MINIFY = os.getenv("HTML_MINIFY", False)

ROOT_URLCONF = "jobsp.urls"

# Python dotted path to the WSGI application used by Django"s runserver.
WSGI_APPLICATION = "jobsp.wsgi.application"

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.messages",
    "sorl.thumbnail",
    "compressor",
    "storages",
    "peeldb",
    # 'django_simple_forum',
    "haystack",
    "dashboard",
    "search",
    "simple_pagination",
    "tellme",
    "django_celery_beat",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "django_ses",
)

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    # "hmin.middleware.MinMiddleware",
    # "hmin.middleware.MarkMiddleware",
    # "jobsp.middlewares.DetectMobileBrowser",
    "jobsp.middlewares.LowerCased",
]


CORS_ALLOWED_ORIGINS = ["http://localhost:4200", "http://127.0.0.1:4200"]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.peeljobs\.com$",
]
CORS_ALLOW_METHODS = list(default_methods)
CORS_ALLOW_HEADERS = list(default_headers)


AUTH_USER_MODEL = "peeldb.User"
LOGIN_URL = "/"

AUTHENTICATION_BACKENDS = (
    "social.auth_backend.PasswordlessAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR + "/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # "jobsp.context_processors.export_vars",
                "peeldb.context_processors.get_pj_icons",
            ],
        },
    },
]

AM_ACCESS_KEY = AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY")
AM_PASS_KEY = AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_KEY")
AWS_SES_REGION_NAME = os.getenv("AWS_SES_REGION_NAME")
AWS_SES_REGION_ENDPOINT = os.getenv("AWS_SES_REGION_ENDPOINT")
AWS_STORAGE_BUCKET_NAME=os.getenv("AWS_STORAGE_BUCKET_NAME")


COMPRESS_CSS_FILTERS = [
    "compressor.filters.css_default.CssAbsoluteFilter",
    "compressor.filters.cssmin.CSSMinFilter",
]
COMPRESS_JS_FILTERS = ["compressor.filters.jsmin.JSMinFilter"]
COMPRESS_REBUILD_TIMEOUT = 5400


MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"
# STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"

ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"
COMPRESS_OUTPUT_DIR = "CACHE"
COMPRESS_URL = STATIC_URL
COMPRESS_ENABLED = True
COMPRESS_PRECOMPILERS = (
    ("text/less", "lessc {infile} {outfile}"),
    ("text/x-sass", "sass {infile} {outfile}"),
    ("text/x-scss", "sass {infile} {outfile}"),
)

COMPRESS_OFFLINE_CONTEXT = {
    "STATIC_URL": "STATIC_URL",
}

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)


# Haystack settings for Elasticsearch
# HAYSTACK_CONNECTIONS = {
#     "default": {
#         "ENGINE": "peeldb.backends.ConfigurableElasticSearchEngine",
#         "URL": "http://127.0.0.1:9200/",
#         "INDEX_NAME": "job_haystack",
#         "TIMEOUT": 60,
#     },
# }

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.elasticsearch7_backend.Elasticsearch7SearchEngine",
        "URL": "http://127.0.0.1:9200/",
        "INDEX_NAME": "haystack",
    },
}


HAYSTACK_SIGNAL_PROCESSOR = "haystack.signals.RealtimeSignalProcessor"
HAYSTACK_DEFAULT_OPERATOR = "OR"
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 1

CELERY_TIMEZONE = "Asia/Calcutta"

CELERY_BEAT_SCHEDULE = {
    # Executes every day evening at 5:00 PM GMT +5.30
    "moving-published-jobs-to-live": {
        "task": "dashboard.tasks.jobpost_published",
        "schedule": crontab(minute="*", day_of_week="mon,tue,wed,thu,fri,sat"),
    },
    "sending-today-applied-users-info-to-recruiters": {
        "task": "dashboard.tasks.recruiter_jobpost_applicants",
        "schedule": crontab(
            hour="16", minute="00", day_of_week="mon,tue,wed,thu,fri,sat"
        ),
    },
    # "sending-profile_update-notifications-to-applicants": {
    #     "task": "dashboard.tasks.applicants_notifications",
    #     "schedule": crontab(
    #         hour="16", minute="00", day_of_week="mon,tue,wed,thu,fri,sat"
    #     ),
    # },
    "sending-daily-statistics-report-to-admins": {
        "task": "dashboard.tasks.daily_report",
        "schedule": crontab(
            hour="08", minute="00", day_of_week="mon,tue,wed,thu,fri,sat,sun"
        ),
    },
    "sending-weekly-jobs-notifications-to-applicants": {
        "task": "dashboard.tasks.applicants_job_notifications",
        "schedule": crontab(hour="09", minute="00", day_of_week="mon"),
    },
    # "all-users-profile-update-and-birthday-notifications": {
    #     "task": "dashboard.tasks.alerting_applicants",
    #     "schedule": crontab(
    #         hour="10", minute="05", day_of_week="mon,tue,wed,thu,fri,sat,sun"
    #     ),
    # },
    # "alerting-all-inactive-users-and-applicants-resume-upload-notifications": {
    #     "task": "dashboard.tasks.applicants_profile_update_notifications",
    #     "schedule": crontab(
    #         hour="09", minute="00", day_of_week="mon,tue,wed,thu,fri,sat,sun"
    #     ),
    # },
    "sending-profile-update-notifications-two-hours-after-registering": {
        "task": "dashboard.tasks.applicants_profile_update_notifications_two_hours",
        "schedule": crontab(
            hour="*/2", minute="00", day_of_week="mon,tue,wed,thu,fri,sat,sun"
        ),
    },
    # "walkin-notifications-to-applicants": {
    #     "task": "dashboard.tasks.applicants_walkin_job_notifications",
    #     "schedule": crontab(hour="09", minute="00", day_of_week="thu"),
    # },
    # "handling-sendgrid-bounces": {
    #     "task": "dashboard.tasks.handle_sendgrid_bounces",
    #     "schedule": crontab(
    #         hour="03", minute="10", day_of_week="mon,tue,wed,thu,fri,sat"
    #     ),
    # },
    "daily-sitemap-generation": {
        "task": "dashboard.tasks.sitemap_generation",
        "schedule": crontab(
            hour="00", minute="10", day_of_week="mon,tue,wed,thu,fri,sat"
        ),
    },
    "sending-today-live-jobs-to-users-based-on-profile": {
        "task": "dashboard.tasks.job_alerts_to_users",
        "schedule": crontab(
            hour="17", minute="00", day_of_week="mon,tue,wed,thu,fri,sat,sun"
        ),
    },
    "sending-today-live-jobs-to-alerts": {
        "task": "dashboard.tasks.job_alerts_to_alerts",
        "schedule": crontab(
            hour="10", minute="00", day_of_week="mon,tue,wed,thu,fri,sat,sun"
        ),
    },
    "sending-today-live-jobs-to-subscribers": {
        "task": "dashboard.tasks.job_alerts_to_subscribers",
        "schedule": crontab(
            hour="18", minute="00", day_of_week="mon,tue,wed,thu,fri,sat,sun"
        ),
    },
    # "recruiter-profile-update-notifications": {
    #     "task": "dashboard.tasks.recruiter_profile_update_notifications",
    #     "schedule": crontab(hour="09", minute="30", day_of_week="mon"),
    # },
    "haystack-rebuilding-indexes": {
        "task": "dashboard.tasks.rebuilding_index",
        "schedule": crontab(
            hour="00", minute="20", day_of_week="mon,tue,wed,thu,fri,sat,sun"
        ),
    },
}
SUPPORT_EMAILS = [
    "ashwin@micropyramid.com",
]


THUMBNAIL_COLORSPACE = None
THUMBNAIL_PRESERVE_FORMAT = False
THUMBNAIL_FORMAT = "PNG"
THUMBNAIL_CACHE_TIMEOUT = 3600 * 24 * 365 * 10

TIMEZONE = "Asia/Calcutta"
LOGO = "http://localhost:8000/logo.png"

# BULK_SMS_USERNAME = os.getenv("BULKSMSUSERNAME")
# BULK_SMS_PASSWORD = os.getenv("BULKSMSPASSWORD")
# BULK_SMS_FROM = os.getenv("BULKSMSFROM")

MINIFIED_URL = os.getenv("MINIFIED_URL")


THUMBNAIL_BACKEND = "jobsp.thumbnailname.SEOThumbnailBackend"
THUMBNAIL_DEBUG = True

THUMBNAIL_FORCE_OVERWRITE = True

# SMS_AUTH_KEY = os.getenv("SMSAUTHKEY")


# AWS_ENABLED = os.getenv("AWSENABLED")
# DISQUS_SHORTNAME = ""

# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
#         "LOCATION": "127.0.0.1:11211",
#         "TIMEOUT": 48 * 60 * 60,
#         "OPTIONS": {"server_max_value_length": 1024 * 1024 * 2,},
#     }
# }

# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.dummy.DummyCache",
#     }
# }

#CACHE_BACKEND = os.getenv("CACHE_BACKEND", "memcached://127.0.0.1:11211/")

FB_ACCESS_TOKEN = os.getenv("FBACCESSTOKEN")
FB_PAGE_ACCESS_TOKEN = os.getenv("FBPAGEACCESSTOKEN")
FB_GROUP_ACCESS_TOKEN = os.getenv("FBGROUPACCESSTOKEN")
FB_ALL_GROUPS_TOKEN = os.getenv("FBALLGROUPSTOKEN")
FB_DEL_ACCESS_TOKEN = os.getenv("FBDELACCESSTOKEN")
REC_FB_ACCESS_TOKEN = os.getenv("RECFBACCESSTOKEN")

URLS = [
    "http://stage.peeljobs.com/",
    "http://stage.peeljobs.com/fresher-jobs/",
    "http://stage.peeljobs.com/jobs/",
    "http://stage.peeljobs.com/companies/",
]

DAILY_REPORT_USERS = [
    "kamal.seo@gmail.com",
    "varun@micropyramid.com",
    "ashwin@micropyramid.com",
]
# MIDDLEWARE_CLASSES = MIDDLEWARE

if os.getenv("ENV_TYPE") == "DEV":
    INSTALLED_APPS = INSTALLED_APPS + (
        # "debug_toolbar",
        # "template_profiler_panel",
        "behave_django",
    )

    # MIDDLEWARE = [
    #     "debug_toolbar.middleware.DebugToolbarMiddleware",
    # ] + MIDDLEWARE

    INTERNAL_IPS = ("127.0.0.1",)

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
        "debug_toolbar.panels.profiling.ProfilingPanel",
        "template_profiler_panel.panels.template.TemplateProfilerPanel",
    ]

    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    TEST_RUNNER = "django_behave.runner.DjangoBehaveTestSuiteRunner"

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
                #'datefmt' : "%d/%b/%Y %H:%M:%S"
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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        # 'rest_framework.authentication.SessionAuthentication',
    ]
}

REST_USE_JWT = True

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

EMAIL_BACKEND = "django_ses.SESBackend"

MP_CELERY_MONITOR_KEY = os.getenv("MP_CELERY_MONITOR_KEY")
CELERY_MONITOR_URL = os.getenv("CELERY_MONITOR_URL")
