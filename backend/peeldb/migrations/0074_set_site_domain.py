"""
Point the Sites row at the real hostname.

`django.contrib.sitemaps` builds its absolute <loc> URLs from
`Site.objects.get_current()`, and that row had never been moved off Django's
stock `example.com` — so every URL in every sitemap section, ~27,000 of them,
advertised `https://example.com/...` to crawlers.

`PeelJobsSitemap.get_domain()` now reads `settings.SITE_DOMAIN` and so no longer
depends on this row, but the *index* view
(`django.contrib.sitemaps.views.index`, wired in `jobsp/urls.py`) resolves the
host through `get_current_site(request)` and offers no equivalent hook. It reads
the database row, so the row has to be right.

Settings stays the source of truth; this migration just syncs the row to it.
"""

from django.conf import settings
from django.db import migrations


def set_site_domain(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    domain = settings.SITE_DOMAIN
    Site.objects.update_or_create(
        pk=settings.SITE_ID,
        defaults={"domain": domain, "name": domain},
    )


def restore_example_com(apps, schema_editor):
    # Django's own default, so reversing lands back where this started rather
    # than leaving a half-configured row.
    Site = apps.get_model("sites", "Site")
    Site.objects.filter(pk=settings.SITE_ID).update(
        domain="example.com", name="example.com"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("peeldb", "0073_jobpost_views_count"),
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.RunPython(set_site_domain, restore_example_com),
    ]
