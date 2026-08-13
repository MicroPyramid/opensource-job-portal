"""
URL Configuration for inbound mail webhooks
"""

from django.urls import path

from . import views

app_name = "webhooks"

urlpatterns = [
    path("ses-bounce/", views.ses_bounce, name="ses-bounce"),
]
