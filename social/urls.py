from django.urls import re_path as url 

from social.views import (
    facebook_login,
    google_login,
    github_login,
    linkedin_login,
    twitter_login,
    facebook_connect,
    google_connect,
    linkedin_connect,
    sofconnect,
)

app_name = "social"

urlpatterns = [
    # login
    url(r"^facebook_login/$", facebook_login, name="facebook_login"),
    url(r"^google_login/$", google_login, name="google_login"),
    url(r"^github/$", github_login, name="github_login"),
    url(r"^linkedin_login/$", linkedin_login, name="linkedin_login"),
    url(r"^twitter_login/$", twitter_login, name="twitter_login"),
    # connect after login
    url(r"^facebook-connect/$", facebook_connect, name="facebook_connect"),
    url(r"^google-connect/$", google_connect, name="google_connect"),
    url(r"^linkedin-connect/$", linkedin_connect, name="linkedin_connect"),
    url(r"^stackoverflow-connect/$", sofconnect, name="sofconnect"),
]
