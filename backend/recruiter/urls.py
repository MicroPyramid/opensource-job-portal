"""
Recruiter URL Configuration

Nothing here renders. The recruiter dashboard lives in `recruiter/` (SvelteKit)
against `/api/v1/recruiter/` — see docs/recruiter-migration-status.md, where all
61 legacy routes are accounted for.

What survives is three redirects, kept only because templates that still render
reverse their names:

- ``new_user`` — base.html, auth_base.html, base_with_tailwind_megamenu.html
- ``list`` — the agency client templates
  (templates/recruiter/company/{client_list,add_client,edit_client}.html)
- ``dashboard`` — recruiter_404.html, rendered by psite, tickets, pjob, agency

They go when those templates go. ``index`` and ``profile`` already went that
way, and ``how_it_works`` was deleted on 2026-08-12 — it extended
``recruiter/index.html``, removed back in d6763e9, so every request had been a
TemplateDoesNotExist 500 with nothing reversing its name.

Redirect targets come from ``settings.RECRUITER_FRONTEND_URL`` so they follow
the deployed recruiter UI instead of being pinned to a dev port.
"""

from django.conf import settings
from django.urls import re_path as url
from django.views.generic import RedirectView

app_name = "recruiter"

_FRONTEND = settings.RECRUITER_FRONTEND_URL.rstrip("/")

urlpatterns = [
    url(
        r"^dashboard/$",
        RedirectView.as_view(url=f"{_FRONTEND}/dashboard/", permanent=False),
        name="dashboard",
    ),
    url(
        r"^job/list/$",
        RedirectView.as_view(url=f"{_FRONTEND}/dashboard/jobs/", permanent=False),
        name="list",
    ),
    url(
        r"^login/$",
        RedirectView.as_view(url=f"{_FRONTEND}/login/", permanent=False),
        name="new_user",
    ),
]
