"""
PeelJobs Django Sitemap Configuration
Modern, dynamic sitemap generation using Django's sitemap framework.
Only includes URLs for pages with actual content (jobs, skills, locations, etc.)
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.db.models import Count, Q
from peeldb.models import JobPost, Skill, City, Company


class PeelJobsSitemap(Sitemap):
    """
    Base sitemap class for PeelJobs
    Sets protocol to HTTPS for all sitemaps
    """
    protocol = 'https'  # Use HTTPS for all URLs (peeljobs.com)


class JobPostSitemap(PeelJobsSitemap):
    """
    Sitemap for individual job postings - highest priority
    Only includes live jobs
    """
    changefreq = "daily"
    priority = 0.9
    limit = 50000  # Max URLs per sitemap file

    def items(self):
        return JobPost.objects.filter(
            status='Live'
        ).select_related('company').prefetch_related('location').order_by('-created_on')

    def lastmod(self, obj):
        """Return last modification date"""
        return obj.published_on or obj.created_on

    def location(self, obj):
        """Job detail URL pattern: /jobs/{job-title-slug}-{job-id}/"""
        # The slug field already contains the full path, but we need /jobs/ prefix
        # Remove leading slash from slug and add /jobs/ prefix
        slug_without_slash = obj.slug.lstrip('/')
        return f"/jobs/{slug_without_slash}"


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
        combinations = JobPost.objects.filter(
            status='Live',
            skills__status='Active',
            location__status='Enabled'
        ).values_list(
            'skills__slug', 'location__slug'
        ).distinct().order_by('skills__slug', 'location__slug')[:10000]

        # Convert to list of dicts for easier template access
        return [
            {'skill': skill_slug, 'city': city_slug}
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
        combinations = JobPost.objects.filter(
            status='Live',
            min_year=0,  # Fresher jobs
            skills__status='Active',
            location__status='Enabled'
        ).values_list(
            'skills__slug', 'location__slug'
        ).distinct().order_by('skills__slug', 'location__slug')[:5000]

        return [
            {'skill': skill_slug, 'city': city_slug}
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
        return Skill.objects.filter(
            status='Active',
            jobpost__status='Live'
        ).annotate(
            job_count=Count('jobpost', filter=Q(jobpost__status='Live'))
        ).filter(job_count__gt=0).distinct().order_by('-job_count')

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
        return City.objects.filter(
            status='Enabled',
            locations__status='Live'
        ).annotate(
            job_count=Count('locations', filter=Q(locations__status='Live'))
        ).filter(job_count__gt=0).distinct().order_by('-job_count')

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
        return Company.objects.filter(
            is_active=True,
            jobpost__status='Live'
        ).annotate(
            job_count=Count('jobpost', filter=Q(jobpost__status='Live'))
        ).filter(job_count__gt=0).distinct().order_by('-job_count')

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
        return [
            'job_list',
            'full_time_jobs',
            'walkin_jobs',
            'internship_jobs',
            'government_jobs',
            'companies',
            'recruiters',
            'contact',
            'jobs_by_skill',
            'jobs_by_industry',
            'jobs_by_degree',
            'jobs_by_location',
            'fresher_jobs_by_skills',
        ]

    def location(self, item):
        return reverse(item)
