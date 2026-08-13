"""
Root URL configuration.

Django's remit is now the REST API, transactional email, XML sitemaps and
platform admin — `docs/django-retirement.md` calls that the finish line. The
job-seeker site is SvelteKit in `site/` and the recruiter dashboard is
SvelteKit in `recruiter/`, both against `/api/v1/`.

The ~90 template-rendering routes that used to live here went with
`candidate/`, `pjob/`, `search/` and `agency/`. They are not redirected: the
platform has had no live traffic for years, so there are no rankings or inbound
links to honour.
"""

from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.sitemaps.views import index as sitemap_index
from django.contrib.sitemaps.views import sitemap as sitemap_view
from django.urls import path
from django.urls import re_path as url
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from api.v1.webhooks.views import ses_bounce
from psite.sitemaps import (
    CompanySitemap,
    FresherSkillLocationSitemap,
    JobPostSitemap,
    LocationSitemap,
    SkillLocationSitemap,
    SkillSitemap,
    StaticPagesSitemap,
)
from psite.views import custom_404, custom_500

sitemaps = {
    "jobs": JobPostSitemap,
    "skill-locations": SkillLocationSitemap,
    "fresher-skill-locations": FresherSkillLocationSitemap,
    "skills": SkillSitemap,
    "locations": LocationSitemap,
    "companies": CompanySitemap,
    "static": StaticPagesSitemap,
}

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^dashboard/", include("dashboard.urls", namespace="dashboard")),
    url(r"tickets/", include("tickets.urls", namespace="tickets")),
    url(r"^social/", include("social.urls", namespace="social")),
    url(r"^celery-check/", include("mp_celery_monitor.urls", namespace="celery-check")),
    # Job Seeker + Recruiter API (DRF + JWT)
    path("api/", include("api.urls", namespace="api")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # AWS SNS holds this path in a live subscription, so it stays where it is
    # even though the handler moved to `api/v1/webhooks/`.
    url(r"^bounces/$", ses_bounce, name="ses_bounce_legacy"),
    # Domain comes from `settings.SITE_DOMAIN` via `Sitemap.get_domain()`, not
    # the Sites framework — see psite/sitemaps.py.
    path(
        "sitemap.xml",
        sitemap_index,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.index",
    ),
    path(
        "sitemap-<section>.xml",
        sitemap_view,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

handler404 = custom_404
handler500 = custom_500

# Include local development URLs -- only when DEBUG is on.
#
# This used to be an unguarded `try: from .urls_local import ...` with an
# `except ImportError: pass`. urls_local is tracked in git, so it ships to
# production, and it unconditionally routes "schema-viewer/" -- a browsable dump
# of the entire database schema. Production was protected only incidentally,
# because django-schema-viewer is a dev-only dependency and the failed import
# was swallowed. That protection disappears the moment dev dependencies are
# installed in production, which the pre-uv deploy did (`pipenv install -d`).
# Gate on DEBUG so the guarantee comes from configuration, not from a missing
# package.
if settings.DEBUG:
    from .urls_local import local_urlpatterns

    urlpatterns += local_urlpatterns

# Serve media files in development
if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
