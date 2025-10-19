"""
Job Views for API v1
Provides job listing, detail, and filter options endpoints
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from peeldb.models import JobPost, City, Skill, Industry, Qualification, SavedJobs, AppliedJobs
from .serializers import JobListSerializer, JobDetailSerializer
from .filters import JobFilter


class JobPagination(PageNumberPagination):
    """Custom pagination for job listings"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for job listings and details.

    Provides:
    - list: Paginated job listings with advanced filtering
    - retrieve: Detailed job information by ID or slug

    Filters available:
    - search: Search in title, company, description
    - location: Filter by city slugs (multiple)
    - skills: Filter by skill slugs (multiple)
    - industry: Filter by industry slugs (multiple)
    - education: Filter by qualification slugs (multiple)
    - job_type: Filter by job type (full-time, internship, etc.)
    - min_salary, max_salary: Salary range in LPA
    - min_experience, max_experience: Experience range in years
    - fresher: Fresher jobs only (boolean)
    - is_remote: Remote jobs only (boolean)
    - posted_after, posted_before: Date range filters

    Ordering:
    - published_on (default: newest first)
    - title
    - min_salary, max_salary
    """
    permission_classes = [AllowAny]
    pagination_class = JobPagination
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = JobFilter
    search_fields = ['title', 'company_name', 'description', 'job_role']
    ordering_fields = ['published_on', 'title', 'min_salary', 'max_salary', 'created_on']
    ordering = ['-published_on']
    lookup_field = 'id'

    def get_queryset(self):
        """
        Get optimized queryset with prefetched relations
        Only returns Live jobs by default
        """
        return JobPost.objects.filter(
            status='Live'
        ).select_related(
            'company',
            'country',
            'major_skill'
        ).prefetch_related(
            'location',
            'skills',
            'industry',
            'edu_qualification',
            'functional_area'
        ).distinct()

    def get_serializer_class(self):
        """Use detailed serializer for retrieve, lightweight for list"""
        if self.action == 'retrieve':
            return JobDetailSerializer
        return JobListSerializer

    @extend_schema(
        summary="Get job details",
        description="Retrieve detailed information about a specific job by ID or slug",
        tags=['Jobs'],
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve job by ID or slug
        Supports both numeric ID and string slug
        Normalizes slug to match database format (with leading/trailing slashes)
        """
        lookup_value = kwargs.get('id')

        # Try to retrieve by ID first
        try:
            if lookup_value.isdigit():
                instance = self.get_queryset().get(id=int(lookup_value))
            else:
                # Normalize slug: ensure it starts and ends with /
                # Database slugs are stored as /slug-text/
                normalized_slug = lookup_value.strip()
                if not normalized_slug.startswith('/'):
                    normalized_slug = '/' + normalized_slug
                if not normalized_slug.endswith('/'):
                    normalized_slug = normalized_slug + '/'

                # Try by normalized slug
                instance = self.get_queryset().get(slug=normalized_slug)
        except JobPost.DoesNotExist:
            return Response(
                {'detail': 'Job not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        summary="List jobs",
        description="Get paginated list of job postings with advanced filtering and search capabilities",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                description='Search in job title, company name, description, and job role',
                required=False,
            ),
            OpenApiParameter(
                name='location',
                type=OpenApiTypes.STR,
                description='Filter by location slug (can be specified multiple times)',
                required=False,
                many=True,
            ),
            OpenApiParameter(
                name='skills',
                type=OpenApiTypes.STR,
                description='Filter by skill slug (can be specified multiple times)',
                required=False,
                many=True,
            ),
            OpenApiParameter(
                name='industry',
                type=OpenApiTypes.STR,
                description='Filter by industry slug (can be specified multiple times)',
                required=False,
                many=True,
            ),
            OpenApiParameter(
                name='education',
                type=OpenApiTypes.STR,
                description='Filter by education/qualification slug (can be specified multiple times)',
                required=False,
                many=True,
            ),
            OpenApiParameter(
                name='job_type',
                type=OpenApiTypes.STR,
                description='Filter by job type (full-time, internship, walk-in, government, Fresher)',
                required=False,
                many=True,
            ),
            OpenApiParameter(
                name='min_salary',
                type=OpenApiTypes.NUMBER,
                description='Minimum salary in LPA (Lakhs Per Annum)',
                required=False,
            ),
            OpenApiParameter(
                name='max_salary',
                type=OpenApiTypes.NUMBER,
                description='Maximum salary in LPA (Lakhs Per Annum)',
                required=False,
            ),
            OpenApiParameter(
                name='min_experience',
                type=OpenApiTypes.INT,
                description='Minimum years of experience',
                required=False,
            ),
            OpenApiParameter(
                name='max_experience',
                type=OpenApiTypes.INT,
                description='Maximum years of experience',
                required=False,
            ),
            OpenApiParameter(
                name='fresher',
                type=OpenApiTypes.BOOL,
                description='Show only fresher jobs',
                required=False,
            ),
            OpenApiParameter(
                name='is_remote',
                type=OpenApiTypes.BOOL,
                description='Show only remote jobs',
                required=False,
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                description='Order results by field (prefix with - for descending). Options: published_on, title, min_salary, max_salary',
                required=False,
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                description='Page number for pagination',
                required=False,
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                description='Number of results per page (max 100)',
                required=False,
            ),
        ],
        tags=['Jobs'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Manage saved jobs",
        description="Save, unsave, or get saved jobs (requires authentication)",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'job_id': {
                        'type': 'integer',
                        'description': 'ID of the job to save (required for POST)'
                    }
                }
            }
        },
        responses={
            200: {'description': 'Success - GET returns list of saved jobs'},
            201: {'description': 'Job saved successfully'},
            400: {'description': 'Bad request'},
            404: {'description': 'Job not found'}
        },
        tags=['Jobs'],
    )
    @action(detail=False, methods=['get', 'post'], permission_classes=[IsAuthenticated], url_path='saved')
    def saved_jobs(self, request):
        """
        GET: Get all saved jobs for the authenticated user
        POST: Save a job for the authenticated user
        """
        if request.method == 'GET':
            # Get all saved jobs
            saved_jobs = SavedJobs.objects.filter(user=request.user).select_related('job_post')
            jobs = [saved.job_post for saved in saved_jobs if saved.job_post.status == 'Live']
            serializer = JobListSerializer(jobs, many=True, context={'request': request})
            return Response(serializer.data)

        elif request.method == 'POST':
            # Save a job
            job_id = request.data.get('job_id')

            if not job_id:
                return Response(
                    {'error': 'job_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                job = JobPost.objects.get(id=job_id, status='Live')
            except JobPost.DoesNotExist:
                return Response(
                    {'error': 'Job not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if already saved
            if SavedJobs.objects.filter(job_post=job, user=request.user).exists():
                return Response(
                    {'error': 'Job already saved'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save the job
            SavedJobs.objects.create(job_post=job, user=request.user)

            return Response(
                {'message': 'Job saved successfully', 'job_id': job_id},
                status=status.HTTP_201_CREATED
            )

    @extend_schema(
        summary="Unsave job",
        description="Remove a saved/bookmarked job (requires authentication)",
        responses={
            200: {'description': 'Job unsaved successfully'},
            404: {'description': 'Saved job not found'}
        },
        tags=['Jobs'],
    )
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated], url_path='saved')
    def unsave_job(self, request, id=None):
        """Remove a saved job for the authenticated user"""
        try:
            job = JobPost.objects.get(id=id)
        except JobPost.DoesNotExist:
            return Response(
                {'error': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            saved_job = SavedJobs.objects.get(job_post=job, user=request.user)
            saved_job.delete()
            return Response(
                {'message': 'Job unsaved successfully'},
                status=status.HTTP_200_OK
            )
        except SavedJobs.DoesNotExist:
            return Response(
                {'error': 'Saved job not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Apply for job",
        description="Submit an application for a job (requires authentication)",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'remarks': {
                        'type': 'string',
                        'description': 'Optional remarks or cover letter',
                        'nullable': True
                    }
                }
            }
        },
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'application_id': {'type': 'integer'}
                }
            },
            400: {'description': 'Already applied or invalid request'},
            404: {'description': 'Job not found'}
        },
        tags=['Jobs'],
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='apply')
    def apply_for_job(self, request, id=None):
        """Apply for a job"""
        try:
            job = JobPost.objects.get(id=id, status='Live')
        except JobPost.DoesNotExist:
            return Response(
                {'error': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if already applied
        if AppliedJobs.objects.filter(job_post=job, user=request.user).exists():
            return Response(
                {'error': 'You have already applied for this job'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get request metadata
        ip_address = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        remarks = request.data.get('remarks', '')

        # Create application
        application = AppliedJobs.objects.create(
            job_post=job,
            user=request.user,
            status='Applied',
            remarks=remarks,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return Response(
            {
                'message': 'Application submitted successfully',
                'application_id': application.id
            },
            status=status.HTTP_201_CREATED
        )


class JobFilterOptionsView(APIView):
    """
    API endpoint to get available filter options with job counts.

    Returns all available locations, skills, industries, and education
    options along with the count of live jobs for each option.

    This endpoint is useful for populating filter dropdowns/checkboxes
    with real-time counts.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Get filter options",
        description="Retrieve all available filter options (locations, skills, industries, education) with job counts",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "locations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "slug": {"type": "string"},
                                "count": {"type": "integer"}
                            }
                        }
                    },
                    "skills": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "slug": {"type": "string"},
                                "count": {"type": "integer"}
                            }
                        }
                    },
                    "industries": {"type": "array"},
                    "education": {"type": "array"},
                    "job_types": {"type": "array"},
                }
            }
        },
        tags=['Jobs'],
    )
    def get(self, request):
        """Get all filter options with job counts"""

        # Base queryset for live jobs
        live_jobs = JobPost.objects.filter(status='Live')

        # Get locations with job counts
        locations = City.objects.filter(
            locations__in=live_jobs
        ).annotate(
            count=Count('locations', filter=Q(locations__status='Live'))
        ).order_by('-count', 'name').values('id', 'name', 'slug', 'count')[:50]

        # Get skills with job counts
        skills = Skill.objects.filter(
            jobpost__in=live_jobs
        ).annotate(
            count=Count('jobpost', filter=Q(jobpost__status='Live'))
        ).order_by('-count', 'name').values('id', 'name', 'slug', 'count')[:50]

        # Get industries with job counts
        industries = Industry.objects.filter(
            jobpost__in=live_jobs
        ).annotate(
            count=Count('jobpost', filter=Q(jobpost__status='Live'))
        ).order_by('-count', 'name').values('id', 'name', 'slug', 'count')

        # Get education/qualifications with job counts
        education = Qualification.objects.filter(
            jobpost__in=live_jobs
        ).annotate(
            count=Count('jobpost', filter=Q(jobpost__status='Live'))
        ).order_by('-count', 'name').values('id', 'name', 'slug', 'count')

        # Get job types with counts
        from peeldb.models import JOB_TYPE
        job_types = []
        for value, label in JOB_TYPE:
            count = live_jobs.filter(job_type=value).count()
            if count > 0:
                job_types.append({
                    'value': value,
                    'label': label,
                    'count': count
                })

        return Response({
            'locations': list(locations),
            'skills': list(skills),
            'industries': list(industries),
            'education': list(education),
            'job_types': job_types,
        })
