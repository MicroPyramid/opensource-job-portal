"""
URL Configuration for Recruiters API v1
"""

from django.urls import path

from . import views

app_name = "recruiters"

urlpatterns = [
    path("", views.RecruiterListView.as_view(), name="recruiter-list"),
    path(
        "<str:username>/",
        views.RecruiterDetailView.as_view(),
        name="recruiter-detail",
    ),
]
