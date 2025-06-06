from django.urls import re_path as url

from social.views import (
    facebook_login,
    google_login,
    github_login,
)

app_name = "social"

urlpatterns = [
    # login
    url(r"^facebook_login/$", facebook_login, name="facebook_login"),
    url(r"^google_login/$", google_login, name="google_login"),
    url(r"^github/$", github_login, name="github_login"),
]
