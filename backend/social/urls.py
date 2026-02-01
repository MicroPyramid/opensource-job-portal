from django.urls import re_path as url

from social.views import google_login

app_name = "social"

urlpatterns = [
    # Only Google OAuth supported
    url(r"^google_login/$", google_login, name="google_login"),
]
