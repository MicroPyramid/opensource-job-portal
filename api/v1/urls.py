"""
API v1 URL routing
"""
from django.urls import path, include

app_name = "v1"

urlpatterns = [
    path("auth/", include("api.v1.auth.urls")),
    # Future endpoints for Job Seekers:
    # path('jobs/', include('api.v1.jobs.urls')),
    # path('profile/', include('api.v1.users.urls')),
]
