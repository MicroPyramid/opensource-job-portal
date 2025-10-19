"""
Job Filters for API v1
Provides advanced filtering capabilities for job listings
"""
from django_filters import rest_framework as filters
from django.db.models import Q
from peeldb.models import JobPost, City, Skill, Industry, Qualification


class JobFilter(filters.FilterSet):
    """
    Comprehensive filter set for job listings
    Supports filtering by location, skills, salary, experience, etc.
    """

    # Text search (searches in title, company_name, description)
    search = filters.CharFilter(method='filter_search', label='Search')

    # Location filters (multiple cities by slug or ID)
    location = filters.ModelMultipleChoiceFilter(
        field_name='location__slug',
        to_field_name='slug',
        queryset=City.objects.all(),
        label='Locations'
    )

    # Skills filter (multiple skills by slug or ID)
    skills = filters.ModelMultipleChoiceFilter(
        field_name='skills__slug',
        to_field_name='slug',
        queryset=Skill.objects.all(),
        label='Skills'
    )

    # Industry filter (multiple industries by slug or ID)
    industry = filters.ModelMultipleChoiceFilter(
        field_name='industry__slug',
        to_field_name='slug',
        queryset=Industry.objects.all(),
        label='Industries'
    )

    # Education/Qualification filter
    education = filters.ModelMultipleChoiceFilter(
        field_name='edu_qualification__slug',
        to_field_name='slug',
        queryset=Qualification.objects.all(),
        label='Education'
    )

    # Job type filter (full-time, internship, walk-in, government, Fresher)
    job_type = filters.MultipleChoiceFilter(
        choices=JobPost._meta.get_field('job_type').choices,
        label='Job Type'
    )

    # Salary filters
    min_salary = filters.NumberFilter(method='filter_min_salary', label='Minimum Salary (LPA)')
    max_salary = filters.NumberFilter(method='filter_max_salary', label='Maximum Salary (LPA)')

    # Experience filters
    min_experience = filters.NumberFilter(method='filter_min_experience', label='Minimum Experience (years)')
    max_experience = filters.NumberFilter(method='filter_max_experience', label='Maximum Experience (years)')

    # Fresher filter
    fresher = filters.BooleanFilter(field_name='fresher', label='Fresher Jobs Only')

    # Remote filter (checks if any location name contains "Remote")
    is_remote = filters.BooleanFilter(method='filter_remote', label='Remote Jobs Only')

    # Date filters
    posted_after = filters.DateFilter(
        field_name='published_on',
        lookup_expr='gte',
        label='Posted After'
    )
    posted_before = filters.DateFilter(
        field_name='published_on',
        lookup_expr='lte',
        label='Posted Before'
    )

    class Meta:
        model = JobPost
        fields = [
            'search',
            'location',
            'skills',
            'industry',
            'education',
            'job_type',
            'min_salary',
            'max_salary',
            'min_experience',
            'max_experience',
            'fresher',
            'is_remote',
            'posted_after',
            'posted_before',
        ]

    def filter_search(self, queryset, name, value):
        """
        Search across title, company_name, and description
        """
        if not value:
            return queryset

        return queryset.filter(
            Q(title__icontains=value) |
            Q(company_name__icontains=value) |
            Q(description__icontains=value) |
            Q(job_role__icontains=value)
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
                (Q(salary_type='Year') & Q(max_salary__gte=min_salary_value)) |
                # Month-based salary (multiply by 12)
                (Q(salary_type='Month') & Q(max_salary__gte=min_salary_value / 12))
            ) |
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
                (Q(salary_type='Year') & Q(min_salary__lte=max_salary_value)) |
                # Month-based salary (multiply by 12)
                (Q(salary_type='Month') & Q(min_salary__lte=max_salary_value / 12))
            ) |
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

        return queryset.filter(
            Q(max_year__gte=value) | Q(fresher=True)
        )

    def filter_max_experience(self, queryset, name, value):
        """
        Filter jobs where min_year <= user's max_experience
        This ensures jobs requiring more experience are excluded
        """
        if value is None:
            return queryset

        return queryset.filter(
            Q(min_year__lte=value) | Q(fresher=True)
        )

    def filter_remote(self, queryset, name, value):
        """
        Filter remote jobs by checking location names
        """
        if not value:
            return queryset

        return queryset.filter(
            location__name__icontains='remote'
        ).distinct()
