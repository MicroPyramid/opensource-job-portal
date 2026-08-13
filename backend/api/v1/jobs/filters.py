"""
Job Filters for API v1
Provides advanced filtering capabilities for job listings
"""

from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    TrigramWordSimilarity,
)
from django.db.models import F, Q
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import filters as drf_filters

from peeldb.models import City, Industry, JobPost, Qualification, Skill

# Word-similarity cutoff for the typo fallback, measured against production
# data rather than picked:
#
#   banglore -> Bangalore  0.583      developper -> Developer   0.750
#   hydrabad -> Hyderabad  0.583      javscript  -> JavaScript  0.615
#   mangaer  -> Manager    0.375      accountnt  -> Accountant  0.700
#   java     -> Jalandhar  0.400  (coincidence, not a typo)
#
# 0.3 was tried and is worse, not laxer-but-safer: "mangaer" goes from 12 job
# matches to 916 by dragging in every "Management", and city lookup starts
# offering "Manipur". 0.4 sits above the coincidental overlap.
#
# Known limit: transpositions in short words stay unmatched — "pyhton" scores
# 0.286 against "Python" because reversing two characters destroys nearly every
# shared trigram. No threshold fixes that without admitting real noise; it
# needs a different algorithm (edit distance), which is not worth adding for a
# fallback path.
TRIGRAM_FALLBACK_THRESHOLD = 0.4


class JobFilter(filters.FilterSet):
    """
    Comprehensive filter set for job listings
    Supports filtering by location, skills, salary, experience, etc.
    """

    # Text search (searches in title, company_name, description)
    search = filters.CharFilter(method="filter_search", label="Search")

    # Location filters (multiple cities by slug or ID)
    location = extend_schema_field(OpenApiTypes.STR)(
        filters.ModelMultipleChoiceFilter(
            field_name="location__slug",
            to_field_name="slug",
            queryset=City.objects.all(),
            label="Locations",
        )
    )

    # Skills filter (multiple skills by slug or ID)
    skills = extend_schema_field(OpenApiTypes.STR)(
        filters.ModelMultipleChoiceFilter(
            field_name="skills__slug",
            to_field_name="slug",
            queryset=Skill.objects.all(),
            label="Skills",
        )
    )

    # Industry filter (multiple industries by slug or ID)
    industry = extend_schema_field(OpenApiTypes.STR)(
        filters.ModelMultipleChoiceFilter(
            field_name="industry__slug",
            to_field_name="slug",
            queryset=Industry.objects.all(),
            label="Industries",
        )
    )

    # Education/Qualification filter
    education = extend_schema_field(OpenApiTypes.STR)(
        filters.ModelMultipleChoiceFilter(
            field_name="edu_qualification__slug",
            to_field_name="slug",
            queryset=Qualification.objects.all(),
            label="Education",
        )
    )

    # Job type filter (full-time, internship, walk-in, government, Fresher)
    job_type = filters.MultipleChoiceFilter(
        choices=JobPost._meta.get_field("job_type").choices, label="Job Type"
    )

    # Salary filters
    min_salary = filters.NumberFilter(
        method="filter_min_salary", label="Minimum Salary (LPA)"
    )
    max_salary = filters.NumberFilter(
        method="filter_max_salary", label="Maximum Salary (LPA)"
    )

    # Experience filters
    min_experience = filters.NumberFilter(
        method="filter_min_experience", label="Minimum Experience (years)"
    )
    max_experience = filters.NumberFilter(
        method="filter_max_experience", label="Maximum Experience (years)"
    )

    # Fresher filter
    fresher = filters.BooleanFilter(field_name="fresher", label="Fresher Jobs Only")

    # Remote filter (checks if any location name contains "Remote")
    is_remote = filters.BooleanFilter(method="filter_remote", label="Remote Jobs Only")

    # Date filters
    posted_after = filters.DateFilter(
        field_name="published_on", lookup_expr="gte", label="Posted After"
    )
    posted_before = filters.DateFilter(
        field_name="published_on", lookup_expr="lte", label="Posted Before"
    )

    # Company filters.
    #
    # `company` was already being passed by site/'s company detail page
    # (`?company=<id>`) but was not declared here, and django-filter ignores
    # params it does not know about — so that page was showing every job on the
    # board as if it belonged to the company. `company_slug` backs the
    # /<company>-job-openings/ landing pages.
    company = filters.NumberFilter(field_name="company_id", label="Company ID")
    company_slug = filters.CharFilter(
        field_name="company__slug", lookup_expr="iexact", label="Company Slug"
    )

    # Backs the /recruiters/<username>/ profile pages, which list that
    # recruiter's live jobs. Matched case-insensitively because the legacy
    # /recruiters/<recruiter_name>/ URLs used `username__iexact` and any
    # inbound link will carry whatever casing that produced.
    recruiter = filters.CharFilter(
        field_name="user__username", lookup_expr="iexact", label="Recruiter Username"
    )

    class Meta:
        model = JobPost
        fields = [
            "search",
            "location",
            "skills",
            "industry",
            "education",
            "job_type",
            "min_salary",
            "max_salary",
            "min_experience",
            "max_experience",
            "fresher",
            "is_remote",
            "posted_after",
            "posted_before",
            "company",
            "company_slug",
            "recruiter",
        ]

    def filter_search(self, queryset, name, value):
        """Full-text search over the stored ``search_vector``, ranked.

        ``JobPost.search_vector`` is a Postgres generated column weighting
        title A, job_role B, company_name C, description D, so a title hit
        outranks a description hit. ``websearch`` query syntax lets a visitor
        type ``"data scientist" -intern`` and have it mean something.

        Both paths annotate ``search_rank``; ``RelevanceOrderingFilter`` sorts
        on it. Callers that only count rows never touch the annotation.
        """
        value = (value or "").strip()
        if not value:
            return queryset

        query = SearchQuery(value, config="english", search_type="websearch")
        matches = queryset.filter(search_vector=query).annotate(
            search_rank=SearchRank(F("search_vector"), query)
        )

        # Exact-ish queries are the overwhelming majority, so the fuzzy pass is
        # a fallback rather than a blend: mixing trigram hits into a query that
        # already matched would pull "Mangalore" into a search for "manager".
        # `.exists()` costs a bounded index probe on the common path.
        if matches.exists():
            return matches

        # Nothing matched — assume a typo before showing a blank page.
        # Word-level similarity, not whole-string: `similarity('pyhton', 'Senior
        # Python Developer')` is ~0.1 because the strings differ in length,
        # while `word_similarity` scores against the best-matching word.
        #
        # Unindexed by design. `word_similarity() > x` cannot use the trigram
        # GIN index (that needs the `%>` operator, whose cutoff is a
        # session GUC), but this only runs on the zero-result path and measures
        # ~90 ms — the same as the icontains scan it replaced, on a path that
        # used to return nothing at all.
        similarity = TrigramWordSimilarity(value, "title")
        return (
            queryset.annotate(search_rank=similarity)
            .filter(search_rank__gt=TRIGRAM_FALLBACK_THRESHOLD)
            .order_by("-search_rank")
        )

    def filter_min_salary(self, queryset, name, value):
        """
        Filter jobs where max_salary >= user's min_salary (in LPA)
        Handles both Month and Year salary types
        """
        if not value:
            return queryset

        # Convert LPA to actual salary value
        min_salary_value = int(value * 100000)  # Convert lakhs to rupees

        return queryset.filter(
            Q(
                # Year-based salary
                (Q(salary_type="Year") & Q(max_salary__gte=min_salary_value))
                |
                # Month-based salary (multiply by 12)
                (Q(salary_type="Month") & Q(max_salary__gte=min_salary_value / 12))
            )
            |
            # Include jobs with no salary specified
            Q(min_salary=0, max_salary=0)
        )

    def filter_max_salary(self, queryset, name, value):
        """
        Filter jobs where min_salary <= user's max_salary (in LPA)
        Handles both Month and Year salary types
        """
        if not value:
            return queryset

        # Convert LPA to actual salary value
        max_salary_value = int(value * 100000)

        return queryset.filter(
            Q(
                # Year-based salary
                (Q(salary_type="Year") & Q(min_salary__lte=max_salary_value))
                |
                # Month-based salary (multiply by 12)
                (Q(salary_type="Month") & Q(min_salary__lte=max_salary_value / 12))
            )
            |
            # Include jobs with no salary specified
            Q(min_salary=0, max_salary=0)
        )

    def filter_min_experience(self, queryset, name, value):
        """
        Filter jobs where max_year >= user's min_experience
        This ensures jobs requiring less experience are shown
        """
        if value is None:
            return queryset

        return queryset.filter(Q(max_year__gte=value) | Q(fresher=True))

    def filter_max_experience(self, queryset, name, value):
        """
        Filter jobs where min_year <= user's max_experience
        This ensures jobs requiring more experience are excluded
        """
        if value is None:
            return queryset

        return queryset.filter(Q(min_year__lte=value) | Q(fresher=True))

    def filter_remote(self, queryset, name, value):
        """
        Filter remote jobs by checking location names
        """
        if not value:
            return queryset

        return queryset.filter(location__name__icontains="remote").distinct()


class RelevanceOrderingFilter(drf_filters.OrderingFilter):
    """Sort by search relevance when searching, by date otherwise.

    ``JobViewSet.ordering`` is ``-published_on``, and DRF applies that default
    unconditionally — which would discard the ranking ``filter_search`` just
    computed and hand back newest-first results for every query. This restores
    relevance as the default *only* while a search term is in play, and still
    yields to an explicit ``?ordering=`` from the caller.
    """

    def get_ordering(self, request, queryset, view):
        explicit = super().get_ordering(request, queryset, view)
        if request.query_params.get(self.ordering_param):
            return explicit

        # Mirror filter_search's own guard: a blank `?search=` leaves the
        # queryset unannotated, so ordering on search_rank would raise.
        if request.query_params.get("search", "").strip():
            return ("-search_rank", "-published_on")

        return explicit
