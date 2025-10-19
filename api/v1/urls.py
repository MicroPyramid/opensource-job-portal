"""
API v1 URL routing
"""
from django.urls import path, include

app_name = "v1"

urlpatterns = [
    path("auth/", include("api.v1.auth.urls")),
    path("profile/", include("api.v1.profile.urls")),
    path("locations/", include("api.v1.locations.urls")),
    path("skills/", include("api.v1.skills.urls")),
    path("employment/", include("api.v1.employment.urls")),
    path("jobs/", include("api.v1.jobs.urls")),
]
