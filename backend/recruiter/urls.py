"""
Recruiter URL Configuration

The recruiter dashboard now lives in SvelteKit (`recruiter/`) against
`/api/v1/recruiter/`. What survives here is only what the still-rendering
job-seeker Django templates reach for:

- ``new_user`` — reversed by base.html, auth_base.html,
  base_with_tailwind_megamenu.html and recruiter_v2/post_job.html
- ``list`` — reversed by the agency client templates
  (templates/recruiter/company/{client_list,add_client,edit_client}.html)
- ``dashboard`` — reversed by recruiter_404.html, which psite, tickets, pjob
  and agency all render
- ``how_it_works`` — a marketing page with no SvelteKit equivalent yet

The ``index`` and ``profile`` redirects were removed once nothing reversed
them. These go the same way when the legacy templates do.

FIXME: the redirect targets are hardcoded to localhost:5174.
"""

from django.urls import re_path as url
from django.views.generic import RedirectView

from recruiter.views import (
    how_it_works,
)

app_name = "recruiter"

urlpatterns = [
    url(
        r"^dashboard/$",
        RedirectView.as_view(url="http://localhost:5174/dashboard", permanent=False),
        name="dashboard",
    ),
    url(
        r"^job/list/$",
        RedirectView.as_view(
            url="http://localhost:5174/dashboard/jobs", permanent=False
        ),
        name="list",
    ),
    url(
        r"^login/$",
        RedirectView.as_view(url="http://localhost:5174/login", permanent=False),
        name="new_user",
    ),
    url(r"^how-it-works/$", how_it_works, name="how_it_works"),
]
