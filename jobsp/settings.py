import os
import json
from celery.schedules import crontab

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DEFAULT_FROM_EMAIL = os.getenv("DEFAULTFROMEMAIL")

CONTACT_NUMBER = os.getenv("CONTACTNUMBER")

PEEL_URL = os.getenv("PEELURL")

CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_IMPORTS = ("social.tasks", "dashboard.tasks", "recruiter.tasks")

# stackoverflow app
SOF_APP_ID = os.getenv("SOFAPPID")
SOF_APP_SECRET = os.getenv("SOFAPPSECRET")
SOF_APP_KEY = os.getenv("SOFAPPKEY")

# github app
broker_api = os.getenv("BROKER_API")

# Enable debug logging

logging = "DEBUG"

GIT_APP_ID = os.getenv("GITAPPID")
GIT_APP_SECRET = os.getenv("GITAPPSECRET")

ALLOWED_HOSTS = ["*"]

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
FB_APP_ID = os.getenv("FBAPPID")
FB_SECRET = os.getenv("FBSECRET")
FB_PEELJOBS_PAGEID = os.getenv("FBPEELJOBSPAGEID")

# google app
GP_CLIENT_ID = GOOGLE_OAUTH2_CLIENT_ID = os.getenv("GPCLIENTID")
GP_CLIENT_SECRET = GOOGLE_OAUTH2_CLIENT_SECRET = os.getenv("GPCLIENTSECRET")
GOOGLE_OAUTH2_REDIRECT = os.getenv("GOOGLEOAUTH2REDIRECT")

if os.getenv("CLIENT_SECRET_DATA"):
    with open("client_secret.json", "w") as outfile:
        json.dump(json.loads(os.getenv("CLIENT_SECRET_DATA")), outfile)

GOOGLE_OAUTH2_CLIENT_SECRETS_JSON = "client_secret.json"

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

MGUN_API_URL = os.getenv("MGUNAPIURL")
MGUN_API_KEY = os.getenv("MGUNAPIKEY")
# MAIL_SENDER = ''

SG_USER = os.getenv("SGUSER")
SG_PWD = os.getenv("SGPWD")

# Make this unique, and don"t share it with anybody.
SECRET_KEY = "=v0l#u!6$z@wjc^zepe1-u0!!7f1y)&4(#&coi5xzm1s=s(g4e"

ADMINS = (
    # ("Your Name", "your_email@example.com"),
)

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_NAME"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}


TIME_ZONE = "Asia/Calcutta"

LANGUAGE_CODE = "en-us"

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# List of finder classes that know how to find static files in various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "compressor.finders.CompressorFinder",
)

# List of callables that know how to import templates from various sources.
# TEMPLATE_LOADERS = (
#     "django.template.loaders.filesystem.Loader",
#     "django.template.loaders.app_directories.Loader",
# )

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    "hmin.middleware.MinMiddleware",
    "hmin.middleware.MarkMiddleware",
    "jobsp.middlewares.DetectMobileBrowser",
    "jobsp.middlewares.LowerCased",
]

MIDDLEWARE_CLASSES = MIDDLEWARE

HTML_MINIFY = False

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
    "django_blog_it.django_blog_it",
    "tellme",
    "django_celery_beat",
)

AUTH_USER_MODEL = "peeldb.User"
LOGIN_URL = "/"

AUTHENTICATION_BACKENDS = (
    # ... your other backends
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
                "peeldb.context_processors.get_pj_icons",
            ],
        },
    },
]
SESSION_ENGINE = "django.contrib.sessions.backends.file"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


AWS_STORAGE_BUCKET_NAME = os.getenv("AWSSTORAGEBUCKETNAME")
AM_ACCESS_KEY = AWS_ACCESS_KEY_ID = os.getenv("AMACCESSKEY")
AM_PASS_KEY = AWS_SECRET_ACCESS_KEY = os.getenv("AMPASSKEY")

CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONTDOMAIN")
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWSS3CUSTOMDOMAIN")
# CLOUDFRONT_DOMAIN = "cdn.peeljobs.com"
CLOUDFRONT_ID = os.getenv("CLOUDFRONTID")

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
DEFAULT_S3_PATH = "media"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATIC_S3_PATH = "static"
COMPRESS_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_DEFAULT_ACL = None

COMPRESS_CSS_FILTERS = [
    "compressor.filters.css_default.CssAbsoluteFilter",
    "compressor.filters.cssmin.CSSMinFilter",
]
COMPRESS_JS_FILTERS = ["compressor.filters.jsmin.JSMinFilter"]
COMPRESS_REBUILD_TIMEOUT = 5400

AWS_HEADERS = {
    "Expires": "Sun, 15 June 2020 20:00:00 GMT",
    "Cache-Control": "max-age=16400000",
    "public-read": True,
}

AWS_IS_GZIPPED = True
AWS_ENABLED = True
AWS_S3_SECURE_URLS = True

MEDIA_ROOT = "/%s/" % DEFAULT_S3_PATH
MEDIA_URL = "//%s/%s/" % (CLOUDFRONT_DOMAIN, DEFAULT_S3_PATH)
STATIC_ROOT = "/%s/" % STATIC_S3_PATH
STATIC_URL = "https://%s/" % (CLOUDFRONT_DOMAIN)
ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"


COMPRESS_OUTPUT_DIR = "CACHE"
COMPRESS_URL = STATIC_URL
COMPRESS_ENABLED = True

COMPRESS_PRECOMPILERS = (
    ("text/less", "/usr/local/bin/lessc {infile} {outfile}"),
    ("text/x-sass", "/usr/local/bin/sass {infile} {outfile}"),
    ("text/x-scss", "/usr/local/bin/sass {infile} {outfile}"),
)

COMPRESS_OFFLINE_CONTEXT = {
    "STATIC_URL": "STATIC_URL",
}

# Haystack settings for Elasticsearch
HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "peeldb.backends.ConfigurableElasticSearchEngine",
        "URL": "http://127.0.0.1:9200/",
        "INDEX_NAME": "job_haystack",
        "TIMEOUT": 60,
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
    "sending-profile_update-notifications-to-applicants": {
        "task": "dashboard.tasks.applicants_notifications",
        "schedule": crontab(
            hour="16", minute="00", day_of_week="mon,tue,wed,thu,fri,sat"
        ),
    },
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
    "all-users-profile-update-and-birthday-notifications": {
        "task": "dashboard.tasks.alerting_applicants",
        "schedule": crontab(
            hour="10", minute="05", day_of_week="mon,tue,wed,thu,fri,sat,sun"
        ),
    },
    "alerting-all-inactive-users-and-applicants-resume-upload-notifications": {
        "task": "dashboard.tasks.applicants_profile_update_notifications",
        "schedule": crontab(
            hour="09", minute="00", day_of_week="mon,tue,wed,thu,fri,sat,sun"
        ),
    },
    "sending-profile-update-notifications-two-hours-after-registering": {
        "task": "dashboard.tasks.applicants_profile_update_notifications_two_hours",
        "schedule": crontab(
            hour="*/2", minute="00", day_of_week="mon,tue,wed,thu,fri,sat,sun"
        ),
    },
    "walkin-notifications-to-applicants": {
        "task": "dashboard.tasks.applicants_walkin_job_notifications",
        "schedule": crontab(hour="09", minute="00", day_of_week="thu"),
    },
    "handling-sendgrid-bounces": {
        "task": "dashboard.tasks.handle_sendgrid_bounces",
        "schedule": crontab(
            hour="03", minute="10", day_of_week="mon,tue,wed,thu,fri,sat"
        ),
    },
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
    "checking-meta-data": {
        "task": "dashboard.tasks.check_meta_data",
        "schedule": crontab(
            hour="*/6", minute="00", day_of_week="mon,tue,wed,thu,fri,sat,sun"
        ),
    },
    "recruiter-profile-update-notifications": {
        "task": "dashboard.tasks.recruiter_profile_update_notifications",
        "schedule": crontab(hour="09", minute="30", day_of_week="mon"),
    },
    "haystack-rebuilding-indexes": {
        "task": "dashboard.tasks.rebuilding_index",
        "schedule": crontab(
            hour="00", minute="20", day_of_week="mon,tue,wed,thu,fri,sat,sun"
        ),
    },
}

THUMBNAIL_COLORSPACE = None
THUMBNAIL_PRESERVE_FORMAT = False
THUMBNAIL_FORMAT = "PNG"
THUMBNAIL_CACHE_TIMEOUT = 3600 * 24 * 365 * 10

TIMEZONE = "Asia/Calcutta"
LOGO = "https://%s/logo.png" % (CLOUDFRONT_DOMAIN)

BULK_SMS_USERNAME = os.getenv("BULKSMSUSERNAME")
BULK_SMS_PASSWORD = os.getenv("BULKSMSPASSWORD")
BULK_SMS_FROM = os.getenv("BULKSMSFROM")

MINIFIED_URL = os.getenv("MINIFIED_URL")

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_DB = os.getenv("MONGO_DB")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PWD = os.getenv("MONGO_PWD")

THUMBNAIL_BACKEND = "jobsp.thumbnailname.SEOThumbnailBackend"
THUMBNAIL_DEBUG = True

THUMBNAIL_FORCE_OVERWRITE = True

INACTIVE_MAIL_SENDER = os.getenv("INACTIVEMAILSENDER")
MAIL_SENDER = os.getenv("MAILSENDER")
SMS_AUTH_KEY = os.getenv("SMSAUTHKEY")


AWS_ENABLED = False
DISQUS_SHORTNAME = ""

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
        "TIMEOUT": 48 * 60 * 60,
        "OPTIONS": {"server_max_value_length": 1024 * 1024 * 90,},
    }
}

CACHE_BACKEND = "memcached://127.0.0.1:11211/"

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

# MIDDLEWARE_CLASSES = MIDDLEWARE
