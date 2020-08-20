# Environment variables guidelines
- All environment variables defined below and their usage.
- Kindly add below environment variables to your local development with appropriate key/value accordingly.

### Common keys
> DEBUG=True/False
> SECRET_KEY=""
> HTML_MINIFY=True/False
> ENV_TYPE="DEV" or "PROD"
> DEFAULT_FROM_EMAIL='PeelJobs <support@peeljobs.com>'
> CONTACT_NUMBER='+91 8500 099 499'
> PEEL_URL="http://peeljobs.com/"
> CACHE_BACKEND = "memcached://127.0.0.1:11211/"
> MINIFIED_URL=''

### Celery keys
> BROKER_API="http://guest:guest@localhost:15672/api/"
> CELERY_BROKER_URL='redis://localhost:6379/1'
> CELERY_RESULT_BACKEND = "redis://localhost:6379"

### Google authentication keys
> GPCLIENTID=""
> GPCLIENTSECRET=""
> CLIENT_SECRET_DATA=""
> GOOGLEOAUTH2REDIRECT='https://peeljobs.com/oauth2callback/'
> GOOGLE_OAUTH2_REDIRECT='http://localhost:8000/oauth2callback/'

### Facebook keys
> FBACCESSTOKEN=""
> FBPAGEACCESSTOKEN=""
> FBGROUPACCESSTOKEN=""
> FBALLGROUPSTOKEN=""
> FBDELACCESSTOKEN=""
> RECFBACCESSTOKEN=""

### Elasticsearch keys
> HAYSTACKURL='http://127.0.0.1:9200/'

### Postgresql DB keys
> DB_NAME='peeljobs'
> DB_USER='postgres'
> DB_PASSWORD='root'
> DB_HOST='127.0.0.1'
> DB_PORT='5432'

### Stack Overflow keys
> SOFAPPID="7099"
> SOFAPPSECRET=""
> SOFAPPKEY=""

### Github keys
> GITAPPID=""
> GITAPPSECRET=""
> GITREDIRECTURI="http://www.peeljobs.com/social/github/"

### Twitter keys
> twoauthtokensecret=''
> twoauthtoken=''
> TWAPPKEY=""
> TWAPPSECRET=""
> OAUTHTOKEN=''
> OAUTHSECRET=''
> PJTWAPPKEY=""
> PJTWAPPSECRET=""

### Facebook Integration keys
> FBAPPID=""
> FBSECRET=""
> FBPEELJOBSPAGEID=""

### Linkedin Integration keys
> LNAPIKEY=""
> LNSECRETKEY=""
> LNCOMPANYID=""
> LNOAUTHUSERTOKEN=""
> LNOAUTHUSERSECRET=""

### Google recaptcha keys
> RECAPTCHAPUBLICKEY=""
> RECAPTCHAPRIVATEKEY=""

### Sendgrid authentication keys
> SGUSER=''
> SGPWD=''

### SMS api keys
> BULKSMSUSERNAME='micropyramid'
> BULKSMSPASSWORD=''
> BULKSMSFROM=''
> SETTINGSFILE=''
> SMSAUTHKEY=''

### Mailgun keys
> MAILGUN_API_KEY=''

### AWS keys
> AWS_STORAGE_BUCKET_NAME=""
> AWS_ACCESS_KEY=''
> AWS_SECRET_KEY=''
> CLOUDFRONT_DOMAIN = ""
> CLOUDFRONT_ID=''
> AWSENABLED=""
> AWS_ACCESS_KEY_FOR_ANYMAIL_SES=""
> AWS_SECRET_KEY_FOR_ANYMAIL_SES=""
> AWS_LOCATION_FOR_ANYMAIL_SES=""

### Sentry keys
> SENTRY_DSN=''

### Elastic APM keys
> ELASTIC_APM_SERVICE_NAME=''
> ELASTIC_APM_SECRET_TOKEN=''
> ELASTIC_APM_SERVER_URL=''