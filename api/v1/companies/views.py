"""
Company Views for API v1
"""
from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from peeldb.models import Company, JobPost, Industry, City
from .serializers import CompanyListSerializer, CompanyDetailSerializer


class CompanyPagination(PageNumberPagination):
    """Pagination for company listings"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CompanyListView(generics.ListAPIView):
    """
    List all companies with filtering and pagination

    Filter by:
    - company_type: Company type (Company, Consultant)
    - size: Company size (1-10, 11-20, 21-50, 50-200, 200+)
    - location: City slug for filtering
    - industry: Industry slug for filtering
    - search: Search by company name
    """
    serializer_class = CompanyListSerializer
    pagination_class = CompanyPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'profile']
    ordering_fields = ['name', 'registered_date']
    ordering = ['-registered_date']

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='company_type',
                description='Filter by company type',
                required=False,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample('Company', value='Company'),
                    OpenApiExample('Consultant', value='Consultant'),
                ]
            ),
            OpenApiParameter(
                name='size',
                description='Filter by company size',
                required=False,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample('1-10', value='1-10'),
                    OpenApiExample('200+', value='200+'),
                ]
            ),
            OpenApiParameter(
                name='location',
                description='Filter by city slug',
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name='industry',
                description='Filter by industry slug',
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name='search',
                description='Search by company name or description',
                required=False,
                type=OpenApiTypes.STR,
            ),
        ],
        responses={200: CompanyListSerializer(many=True)},
        tags=['Companies'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Filter companies based on query parameters
        Only include companies with active jobs
        """
        queryset = Company.objects.filter(
            is_active=True
        ).annotate(
            job_count=Count('jobpost', filter=Q(jobpost__status='Live'))
        ).filter(
            job_count__gt=0  # Only companies with active jobs
        )

        # Filter by company type
        company_type = self.request.query_params.get('company_type')
        if company_type:
            queryset = queryset.filter(company_type=company_type)

        # Filter by company size
        size = self.request.query_params.get('size')
        if size:
            queryset = queryset.filter(size=size)

        # Filter by location (city slug)
        location = self.request.query_params.get('location')
        if location:
            # Find companies with jobs in this city
            try:
                city = City.objects.get(slug=location)
                company_ids = JobPost.objects.filter(
                    location=city,
                    status='Live'
                ).values_list('company_id', flat=True).distinct()
                queryset = queryset.filter(id__in=company_ids)
            except City.DoesNotExist:
                pass

        # Filter by industry
        industry = self.request.query_params.get('industry')
        if industry:
            # Find companies with jobs in this industry
            try:
                ind = Industry.objects.get(slug=industry)
                company_ids = JobPost.objects.filter(
                    industry=ind,
                    status='Live'
                ).values_list('company_id', flat=True).distinct()
                queryset = queryset.filter(id__in=company_ids)
            except Industry.DoesNotExist:
                pass

        return queryset.distinct()


class CompanyDetailView(generics.RetrieveAPIView):
    """
    Get detailed company information by slug
    """
    serializer_class = CompanyDetailSerializer
    lookup_field = 'slug'

    @extend_schema(
        responses={200: CompanyDetailSerializer},
        tags=['Companies'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Company.objects.filter(is_active=True)


@extend_schema(
    responses={200: {
        'type': 'object',
        'properties': {
            'company_types': {'type': 'array'},
            'sizes': {'type': 'array'},
            'locations': {'type': 'array'},
            'industries': {'type': 'array'},
        }
    }},
    tags=['Companies'],
)
@api_view(['GET'])
def company_filter_options(request):
    """
    Get available filter options for companies page
    Returns counts for each filter option
    """
    # Get companies with active jobs
    active_companies = Company.objects.filter(
        is_active=True
    ).annotate(
        job_count=Count('jobpost', filter=Q(jobpost__status='Live'))
    ).filter(job_count__gt=0)

    # Company types with counts
    company_types = active_companies.values('company_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # Company sizes with counts
    sizes = active_companies.values('size').annotate(
        count=Count('id')
    ).order_by('-count')

    # Get locations from active job posts
    locations = City.objects.filter(
        locations__status='Live',
        locations__company__is_active=True
    ).annotate(
        count=Count('locations', distinct=True)
    ).order_by('-count')[:20]

    location_data = [{
        'label': f"{loc.name}",
        'value': loc.slug,
        'count': loc.count
    } for loc in locations]

    # Get industries from active job posts
    industries = Industry.objects.filter(
        jobpost__status='Live',
        jobpost__company__is_active=True
    ).annotate(
        count=Count('jobpost', distinct=True)
    ).order_by('-count')[:20]

    industry_data = [{
        'label': ind.name,
        'value': ind.slug,
        'count': ind.count
    } for ind in industries]

    return Response({
        'company_types': [
            {
                'label': ct['company_type'] if ct['company_type'] else 'Other',
                'value': ct['company_type'] if ct['company_type'] else 'other',
                'count': ct['count']
            }
            for ct in company_types
        ],
        'sizes': [
            {
                'label': s['size'] if s['size'] else 'Not Specified',
                'value': s['size'] if s['size'] else '',
                'count': s['count']
            }
            for s in sizes if s['size']
        ],
        'locations': location_data,
        'industries': industry_data,
    })
