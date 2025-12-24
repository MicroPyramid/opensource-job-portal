"""
Recruiter URL Configuration

NOTE: Most recruiter functionality has been migrated to SvelteKit (recruiter_ui/)
and REST API (/api/v1/recruiter/). These legacy URLs are kept for:
- Utility functions (how_it_works, interview_location)
- Backward compatibility redirects

For new development, use:
- SvelteKit frontend: /recruiter_ui/
- REST API endpoints: /api/v1/recruiter/
"""
from django.urls import re_path as url
from django.views.generic import RedirectView

from recruiter.views import (
    how_it_works,
    interview_location,
)

app_name = "recruiter"

urlpatterns = [
    # Redirect old recruiter URLs to new SvelteKit dashboard
    url(r"^$", RedirectView.as_view(url="http://localhost:5174/dashboard", permanent=False), name="index"),
    url(r"^dashboard/$", RedirectView.as_view(url="http://localhost:5174/dashboard", permanent=False), name="dashboard"),
    url(r"^job/list/$", RedirectView.as_view(url="http://localhost:5174/dashboard/jobs", permanent=False), name="list"),
    url(r"^profile/$", RedirectView.as_view(url="http://localhost:5174/dashboard/account", permanent=False), name="profile"),
    url(r"^login/$", RedirectView.as_view(url="http://localhost:5174/login", permanent=False), name="new_user"),

    # Legacy utility endpoints (still used by some parts of the system)
    url(r"^how-it-works/$", how_it_works, name="how_it_works"),
    url(
        r"^job/interview-location/(?P<location_count>[a-zA-Z0-9]+)/$",
        interview_location,
        name="interview_location",
    ),
]
