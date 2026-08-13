"""
API v1 URL routing
"""

from django.urls import include, path

app_name = "v1"

urlpatterns = [
    path("auth/", include("api.v1.auth.urls")),
    path("profile/", include("api.v1.profile.urls")),
    path("locations/", include("api.v1.locations.urls")),
    path("skills/", include("api.v1.skills.urls")),
    path("employment/", include("api.v1.employment.urls")),
    path("jobs/", include("api.v1.jobs.urls")),
    path("alerts/", include("api.v1.alerts.urls", namespace="alerts")),
    path("recruiters/", include("api.v1.recruiters.urls", namespace="recruiters")),
    path("companies/", include("api.v1.companies.urls")),
    path("contact/", include("api.v1.contact.urls")),
    path("recruiter/", include("api.v1.recruiter.urls")),
    path("webhooks/", include("api.v1.webhooks.urls", namespace="webhooks")),
]
