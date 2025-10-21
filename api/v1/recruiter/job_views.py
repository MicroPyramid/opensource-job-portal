"""
Recruiter Job Management API Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q, Count
from django.utils import timezone

from peeldb.models import JobPost, AppliedJobs
from .job_serializers import (
    RecruiterJobListSerializer,
    RecruiterJobDetailSerializer,
    RecruiterJobCreateSerializer,
    RecruiterJobUpdateSerializer,
    JobApplicationSerializer
)


class JobPostPagination(PageNumberPagination):
    """Pagination for job listings"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema(
    tags=["Recruiter - Jobs"],
    summary="List Recruiter's Jobs",
    description="Get all jobs posted by the authenticated recruiter with filtering",
    parameters=[
        OpenApiParameter('status', OpenApiTypes.STR, description='Filter by status (Live, Draft, Expired, etc.)'),
        OpenApiParameter('search', OpenApiTypes.STR, description='Search by title or company name'),
        OpenApiParameter('ordering', OpenApiTypes.STR, description='Order by field (created_on, -created_on, title, -applicants)'),
        OpenApiParameter('page', OpenApiTypes.INT, description='Page number'),
        OpenApiParameter('page_size', OpenApiTypes.INT, description='Items per page (max 100)'),
    ],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_jobs(request):
    """
    List all jobs posted by the authenticated recruiter

    Supports filtering by status, search, and ordering
    """
    user = request.user

    # Base queryset - jobs posted by this user
    queryset = JobPost.objects.filter(user=user).select_related(
        'company', 'country'
    ).prefetch_related(
        'location', 'skills', 'industry', 'edu_qualification'
    )

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    # Search by title or company name
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(company_name__icontains=search) |
            Q(job_role__icontains=search)
        )

    # Annotate with applicants count for ordering
    queryset = queryset.annotate(applicants_count=Count('appliedjobs'))

    # Ordering
    ordering = request.GET.get('ordering', '-created_on')
    if ordering == 'applicants' or ordering == '-applicants':
        queryset = queryset.order_by('applicants_count' if ordering == 'applicants' else '-applicants_count')
    else:
        queryset = queryset.order_by(ordering)

    # Paginate
    paginator = JobPostPagination()
    page = paginator.paginate_queryset(queryset, request)

    if page is not None:
        serializer = RecruiterJobListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    serializer = RecruiterJobListSerializer(queryset, many=True, context={'request': request})
    return Response(serializer.data)


@extend_schema(
    tags=["Recruiter - Jobs"],
    summary="Get Job Details",
    description="Get detailed information about a specific job",
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job(request, job_id):
    """Get detailed info about a specific job"""
    user = request.user

    try:
        job = JobPost.objects.select_related(
            'company', 'country'
        ).prefetch_related(
            'location', 'skills', 'industry', 'edu_qualification', 'functional_area'
        ).get(id=job_id, user=user)
    except JobPost.DoesNotExist:
        return Response(
            {"error": "Job not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = RecruiterJobDetailSerializer(job, context={'request': request})
    return Response(serializer.data)


@extend_schema(
    tags=["Recruiter - Jobs"],
    summary="Create New Job",
    description="Create a new job posting",
    request=RecruiterJobCreateSerializer,
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job(request):
    """
    Create a new job posting

    Job will be created in Draft status by default
    """
    user = request.user

    # Check if user has a company (optional - can post as individual recruiter)
    if not user.company and request.data.get('company_name'):
        # Allow individual recruiters to post jobs with company name
        pass

    serializer = RecruiterJobCreateSerializer(
        data=request.data,
        context={'request': request, 'user': user}
    )

    if serializer.is_valid():
        job = serializer.save(user=user)

        response_serializer = RecruiterJobDetailSerializer(job, context={'request': request})
        return Response({
            "success": True,
            "job": response_serializer.data,
            "message": "Job created successfully"
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Recruiter - Jobs"],
    summary="Update Job",
    description="Update an existing job posting",
    request=RecruiterJobUpdateSerializer,
)
@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def update_job(request, job_id):
    """Update an existing job"""
    user = request.user

    try:
        job = JobPost.objects.get(id=job_id, user=user)
    except JobPost.DoesNotExist:
        return Response(
            {"error": "Job not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = RecruiterJobUpdateSerializer(
        job,
        data=request.data,
        partial=(request.method == 'PATCH'),
        context={'request': request, 'user': user}
    )

    if serializer.is_valid():
        job = serializer.save()

        response_serializer = RecruiterJobDetailSerializer(job, context={'request': request})
        return Response({
            "success": True,
            "job": response_serializer.data,
            "message": "Job updated successfully"
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Recruiter - Jobs"],
    summary="Delete Job",
    description="Delete a job posting",
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_job(request, job_id):
    """Delete a job"""
    user = request.user

    try:
        job = JobPost.objects.get(id=job_id, user=user)
    except JobPost.DoesNotExist:
        return Response(
            {"error": "Job not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if job has applicants
    applicants_count = AppliedJobs.objects.filter(job_post=job).count()
    if applicants_count > 0 and not request.GET.get('force'):
        return Response(
            {
                "error": f"This job has {applicants_count} applicants. Add ?force=true to confirm deletion.",
                "applicants_count": applicants_count
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    job_title = job.title
    job.delete()

    return Response({
        "success": True,
        "message": f"Job '{job_title}' deleted successfully"
    })


@extend_schema(
    tags=["Recruiter - Jobs"],
    summary="Publish Job",
    description="Publish a draft job to make it live",
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def publish_job(request, job_id):
    """Publish a draft job"""
    user = request.user

    try:
        job = JobPost.objects.get(id=job_id, user=user)
    except JobPost.DoesNotExist:
        return Response(
            {"error": "Job not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if job.status == 'Live':
        return Response(
            {"error": "Job is already live"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate required fields before publishing
    if not job.title or not job.description:
        return Response(
            {"error": "Job must have title and description to be published"},
            status=status.HTTP_400_BAD_REQUEST
        )

    job.status = 'Live'
    job.published_on = timezone.now()
    if not job.published_date:
        job.published_date = timezone.now().date()
    job.save()

    serializer = RecruiterJobDetailSerializer(job, context={'request': request})
    return Response({
        "success": True,
        "job": serializer.data,
        "message": "Job published successfully"
    })


@extend_schema(
    tags=["Recruiter - Jobs"],
    summary="Close Job",
    description="Close an active job posting",
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_job(request, job_id):
    """Close an active job"""
    user = request.user

    try:
        job = JobPost.objects.get(id=job_id, user=user)
    except JobPost.DoesNotExist:
        return Response(
            {"error": "Job not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if job.status == 'Disabled':
        return Response(
            {"error": "Job is already closed"},
            status=status.HTTP_400_BAD_REQUEST
        )

    job.status = 'Disabled'
    job.save()

    serializer = RecruiterJobDetailSerializer(job, context={'request': request})
    return Response({
        "success": True,
        "job": serializer.data,
        "message": "Job closed successfully"
    })


@extend_schema(
    tags=["Recruiter - Jobs"],
    summary="Get Job Applicants",
    description="Get all applicants for a specific job",
    parameters=[
        OpenApiParameter('status', OpenApiTypes.STR, description='Filter by application status (Pending, Shortlisted, Selected, Rejected)'),
        OpenApiParameter('ordering', OpenApiTypes.STR, description='Order by field (applied_on, -applied_on)'),
    ],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_applicants(request, job_id):
    """Get all applicants for a job"""
    user = request.user

    try:
        job = JobPost.objects.get(id=job_id, user=user)
    except JobPost.DoesNotExist:
        return Response(
            {"error": "Job not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get applications for this job
    applications = AppliedJobs.objects.filter(job_post=job).select_related('user')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)

    # Ordering
    ordering = request.GET.get('ordering', '-applied_on')
    applications = applications.order_by(ordering)

    serializer = JobApplicationSerializer(applications, many=True, context={'request': request})

    return Response({
        "job": {
            "id": job.id,
            "title": job.title,
            "status": job.status
        },
        "applications": serializer.data,
        "total_applicants": applications.count(),
        "stats": {
            "pending": applications.filter(status='Pending').count(),
            "shortlisted": applications.filter(status='Shortlisted').count(),
            "selected": applications.filter(status='Selected').count(),
            "rejected": applications.filter(status='Rejected').count(),
        }
    })


@extend_schema(
    tags=["Recruiter - Jobs"],
    summary="Get Dashboard Stats",
    description="Get overall statistics for recruiter's jobs",
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """Get dashboard statistics for recruiter"""
    user = request.user

    jobs = JobPost.objects.filter(user=user)

    # Calculate stats
    total_jobs = jobs.count()
    live_jobs = jobs.filter(status='Live').count()
    draft_jobs = jobs.filter(status='Draft').count()
    closed_jobs = jobs.filter(status='Disabled').count()
    expired_jobs = jobs.filter(status='Expired').count()

    # Total applicants across all jobs
    total_applicants = AppliedJobs.objects.filter(job_post__user=user).count()

    # Total views
    total_views = sum([
        job.fb_views + job.tw_views + job.ln_views + job.other_views
        for job in jobs
    ])

    # Recent jobs (last 5)
    recent_jobs = jobs.order_by('-created_on')[:5]
    recent_jobs_data = RecruiterJobListSerializer(
        recent_jobs, many=True, context={'request': request}
    ).data

    return Response({
        "stats": {
            "total_jobs": total_jobs,
            "live_jobs": live_jobs,
            "draft_jobs": draft_jobs,
            "closed_jobs": closed_jobs,
            "expired_jobs": expired_jobs,
            "total_applicants": total_applicants,
            "total_views": total_views,
        },
        "recent_jobs": recent_jobs_data
    })
