# Environment variables guidelines

- All environment variables defined below and their usage.
- Kindly add below environment variables to your local development with appropriate key/value accordingly.

## Common keys

DEBUG=True/False
SECRET_KEY=""
HTML_MINIFY=True/False
ENV_TYPE="DEV" or "PROD"
DEFAULT_FROM_EMAIL='PeelJobs <peeljobs@micropyramid.com>'
PEEL_URL="http://peeljobs.com/"
CACHE_BACKEND = "memcached://127.0.0.1:11211/"

## Celery keys

CELERY_BROKER_URL='redis://localhost:6379/1'

## Google authentication keys

GOOGLE_CLIENT_ID=""
GOOGLE_CLIENT_SECRET=""
GOOGLE_LOGIN_HOST='http://localhost:8000'
## Elasticsearch keys

HAYSTACKURL='http://127.0.0.1:9200/'

## Postgresql DB keys

DB_NAME='peeljobs'
DB_USER='postgres'
DB_PASSWORD='root'
DB_HOST='127.0.0.1'
DB_PORT='5432'


## Github keys

GITAPPID=""
GITAPPSECRET=""


## Facebook Integration keys

FACEBOOK_APP_ID=""
FACEBOOK_APP_SECRET=""
FBPEELJOBSPAGEID=""

## Google recaptcha keys

RECAPTCHAPUBLICKEY=""
RECAPTCHAPRIVATEKEY=""

## AWS keys

AWS_STORAGE_BUCKET_NAME=""
AWS_ACCESS_KEY=''
AWS_SECRET_KEY=''
CLOUDFRONT_DOMAIN = ""
CLOUDFRONT_ID=''
AWS_SES_REGION_NAME = 'eu-west-1'
AWS_SES_REGION_ENDPOINT = 'email.eu-west-1.amazonaws.com'

## Sentry keys

SENTRY_DSN=''
