"""
PeelJobs Django Sitemap Configuration
Modern, dynamic sitemap generation using Django's sitemap framework.
Only includes URLs for pages with actual content (jobs, skills, locations, etc.)
"""

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.db.models import Count, Q

from peeldb.models import City, Company, JobPost, Skill


class PeelJobsSitemap(Sitemap):
    """
    Base sitemap class for PeelJobs
    Sets protocol to HTTPS for all sitemaps
    """

    protocol = "https"  # Use HTTPS for all URLs (peeljobs.com)

    def get_domain(self, site=None):
        """
        Take the hostname from settings, not from the Sites framework.

        Django's default resolves the domain through `Site.objects.get_current()`,
        and that row was never configured off Django's stock `example.com` — so
        every <loc> in every section pointed at example.com. Nothing else in the
        codebase reads Site.objects, so there is no reason to keep a database
        row as the source of truth for this.
        """
        return settings.SITE_DOMAIN


class JobPostSitemap(PeelJobsSitemap):
    """
    Sitemap for individual job postings - highest priority
    Only includes live jobs
    """

    changefreq = "daily"
    priority = 0.9
    limit = 50000  # Max URLs per sitemap file

    def items(self):
        return (
            JobPost.objects.filter(status="Live")
            .select_related("company")
            .prefetch_related("location")
            .order_by("-created_on")
        )

    def lastmod(self, obj):
        """Return last modification date"""
        return obj.published_on or obj.created_on

    def location(self, obj):
        """Job detail URL pattern: /jobs/{job-title-slug}-{job-id}/"""
        # The trailing slash is not decoration: `site/src/routes/+layout.js` sets
        # `trailingSlash = 'always'`, so the slashless form 301s. Emitting it
        # here made every URL in the largest sitemap section a redirect.
        return f"/jobs/{obj.slug.strip('/')}/"


class SkillLocationSitemap(PeelJobsSitemap):
    """
    Sitemap for skill + location combinations (e.g., python-jobs-in-bangalore)
    OPTIMIZED: Only includes combinations that have active jobs
    """

    changefreq = "daily"
    priority = 0.8
    limit = 10000

    def items(self):
        """
        Use Django ORM to get skill+location combinations with active jobs
        This avoids the cartesian product of all skills × all locations
        """
        # Get all skill-location pairs from live jobs
        combinations = (
            JobPost.objects.filter(
                status="Live", skills__status="Active", location__status="Enabled"
            )
            .values_list("skills__slug", "location__slug")
            .distinct()
            .order_by("skills__slug", "location__slug")[:10000]
        )

        # Convert to list of dicts for easier template access
        return [
            {"skill": skill_slug, "city": city_slug}
            for skill_slug, city_slug in combinations
            if skill_slug and city_slug  # Filter out None values
        ]

    def location(self, item):
        return f"/{item['skill']}-jobs-in-{item['city']}/"


class FresherSkillLocationSitemap(PeelJobsSitemap):
    """
    Sitemap for fresher jobs by skill and location
    Only includes combinations with actual fresher jobs
    """

    changefreq = "daily"
    priority = 0.7
    limit = 10000

    def items(self):
        """Use Django ORM to get fresher job skill-location combinations"""
        combinations = (
            JobPost.objects.filter(
                status="Live",
                min_year=0,  # Fresher jobs
                skills__status="Active",
                location__status="Enabled",
            )
            .values_list("skills__slug", "location__slug")
            .distinct()
            .order_by("skills__slug", "location__slug")[:5000]
        )

        return [
            {"skill": skill_slug, "city": city_slug}
            for skill_slug, city_slug in combinations
            if skill_slug and city_slug
        ]

    def location(self, item):
        return f"/{item['skill']}-fresher-jobs-in-{item['city']}/"


class SkillSitemap(PeelJobsSitemap):
    """
    Sitemap for skill-based job listings (e.g., /python-jobs/)
    Only includes skills that have live jobs
    """

    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return (
            Skill.objects.filter(status="Active", jobpost__status="Live")
            .annotate(job_count=Count("jobpost", filter=Q(jobpost__status="Live")))
            .filter(job_count__gt=0)
            .distinct()
            .order_by("-job_count")
        )

    def location(self, obj):
        return f"/{obj.slug}-jobs/"


class LocationSitemap(PeelJobsSitemap):
    """
    Sitemap for location-based job listings (e.g., /jobs-in-bangalore/)
    Only includes locations with live jobs
    """

    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return (
            City.objects.filter(status="Enabled", locations__status="Live")
            .annotate(job_count=Count("locations", filter=Q(locations__status="Live")))
            .filter(job_count__gt=0)
            .distinct()
            .order_by("-job_count")
        )

    def location(self, obj):
        return f"/jobs-in-{obj.slug}/"


class CompanySitemap(PeelJobsSitemap):
    """
    Sitemap for company job listings
    Only includes companies with active jobs
    """

    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return (
            Company.objects.filter(is_active=True, jobpost__status="Live")
            .annotate(job_count=Count("jobpost", filter=Q(jobpost__status="Live")))
            .filter(job_count__gt=0)
            .distinct()
            .order_by("-job_count")
        )

    def location(self, obj):
        return f"/{obj.slug}-job-openings/"


class StaticPagesSitemap(PeelJobsSitemap):
    """
    Sitemap for static/category pages
    These are always available regardless of job count
    """

    changefreq = "weekly"
    priority = 0.4

    def items(self):
        # Literal paths, like every other sitemap in this file. These used to be
        # Django URL names resolved through `reverse()`, which stopped working
        # the moment the pages became SvelteKit routes — one missing name raises
        # NoReverseMatch and takes the whole section down with a 500.
        #
        # Keep this list in step with `site/src/routes/(site)/`. Only pages that
        # are worth crawling belong here: no /profile/, /saved/ or
        # /applications/, which require a signed-in user.
        return [
            "/",
            "/jobs/",
            "/full-time-jobs/",
            "/walkin-jobs/",
            "/internship-jobs/",
            "/government-jobs/",
            "/companies/",
            "/recruiters/",
            "/jobs-by-skill/",
            "/jobs-by-industry/",
            "/jobs-by-degree/",
            "/job-alerts/",
            "/about/",
            "/contact/",
            "/help/",
            "/pricing/",
            "/privacy/",
            "/terms/",
        ]

    def location(self, item):
        return item
