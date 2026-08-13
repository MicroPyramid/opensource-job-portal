"""
URL Configuration for Job Alerts API v1
"""

from django.urls import path

from . import views

app_name = "alerts"

urlpatterns = [
    path("subscribe/", views.subscribe, name="subscribe"),
    path("verify/", views.verify, name="verify"),
    path("unsubscribe/", views.unsubscribe, name="unsubscribe"),
]
