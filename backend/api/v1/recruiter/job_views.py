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

from peeldb.models import (
    JobPost, AppliedJobs, City, Skill, Industry,
    Qualification, Country, State
)
from .job_serializers import (
    RecruiterJobListSerializer,
    RecruiterJobDetailSerializer,
    RecruiterJobCreateSerializer,
    RecruiterJobUpdateSerializer,
    JobApplicationSerializer,
    ApplicantDetailSerializer
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
            'location', 'skills', 'industry', 'edu_qualification'
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

    # Debug: Log incoming data
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Creating job with data: {request.data}")

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

    # Debug: Log validation errors
    logger.error(f"Job creation validation errors: {serializer.errors}")
    print(f"Job creation validation errors: {serializer.errors}")

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

    # Prevent editing published jobs (Live, Disabled, or Expired)
    if job.status in ['Live', 'Disabled', 'Expired']:
        return Response(
            {"error": f"Cannot edit a job with status '{job.status}'. Only Draft jobs can be edited."},
            status=status.HTTP_400_BAD_REQUEST
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

    # Prevent deleting published jobs (Live, Disabled, or Expired)
    if job.status in ['Live', 'Disabled', 'Expired']:
        return Response(
            {"error": f"Cannot delete a job with status '{job.status}'. Published jobs cannot be hard-deleted. Use the Close option instead."},
            status=status.HTTP_400_BAD_REQUEST
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
    if not job.title:
        return Response(
            {"error": "Job must have title to be published"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not job.description or job.description.strip() == '':
        return Response(
            {"error": "Job must have description to be published"},
            status=status.HTTP_400_BAD_REQUEST
        )

    job.status = 'Live'
    job.published_on = timezone.now()
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
    description="Get overall statistics for recruiter's jobs with application pipeline metrics",
    parameters=[
        OpenApiParameter('period', OpenApiTypes.STR, description='Time period for trend calculation: 7d, 30d, 90d (default: 30d)'),
    ],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """Get dashboard statistics for recruiter with application analytics"""
    user = request.user
    period = request.GET.get('period', '30d')

    # Parse period
    if period == '7d':
        days = 7
    elif period == '90d':
        days = 90
    else:
        days = 30

    from datetime import timedelta
    start_date = timezone.now() - timedelta(days=days)
    prev_start_date = start_date - timedelta(days=days)

    jobs = JobPost.objects.filter(user=user)

    # Basic stats
    total_jobs = jobs.count()
    live_jobs = jobs.filter(status='Live').count()
    draft_jobs = jobs.filter(status='Draft').count()
    closed_jobs = jobs.filter(status='Disabled').count()
    expired_jobs = jobs.filter(status='Expired').count()

    # Application stats
    all_applicants = AppliedJobs.objects.filter(job_post__user=user)
    total_applicants = all_applicants.count()

    # NEW: Applications in current period
    new_applicants = all_applicants.filter(
        applied_on__gte=start_date
    ).count()

    # NEW: Applications in previous period (for trend)
    prev_applicants = all_applicants.filter(
        applied_on__gte=prev_start_date,
        applied_on__lt=start_date
    ).count()

    # Calculate trend
    if prev_applicants > 0:
        trend_pct = ((new_applicants - prev_applicants) / prev_applicants) * 100
        applicants_trend = f"{'+' if trend_pct > 0 else ''}{trend_pct:.1f}%"
    else:
        applicants_trend = "N/A"

    # NEW: Pipeline metrics
    pipeline = {
        'pending': all_applicants.filter(status='Pending').count(),
        'shortlisted': all_applicants.filter(status='Shortlisted').count(),
        'hired': all_applicants.filter(status='Hired').count(),
        'rejected': all_applicants.filter(status='Rejected').count(),
    }

    # Conversion rate
    if total_applicants > 0:
        pipeline['conversion_rate'] = round(
            (pipeline['hired'] / total_applicants) * 100, 2
        )
    else:
        pipeline['conversion_rate'] = 0

    # Average applications per live job
    avg_applications_per_job = (
        total_applicants / live_jobs if live_jobs > 0 else 0
    )

    # Recent jobs with enhanced data
    recent_jobs = jobs.order_by('-created_on')[:5]
    recent_jobs_data = []

    for job in recent_jobs:
        job_data = RecruiterJobListSerializer(
            job, context={'request': request}
        ).data

        # Add new application metrics
        job_applicants = AppliedJobs.objects.filter(job_post=job)
        new_apps_7d = job_applicants.filter(
            applied_on__gte=timezone.now() - timedelta(days=7)
        ).count()

        job_data['new_applicants'] = new_apps_7d
        job_data['pending_review'] = job_applicants.filter(status='Pending').count()

        recent_jobs_data.append(job_data)

    return Response({
        "stats": {
            "total_jobs": total_jobs,
            "live_jobs": live_jobs,
            "draft_jobs": draft_jobs,
            "closed_jobs": closed_jobs,
            "expired_jobs": expired_jobs,
            "total_applicants": total_applicants,
            "new_applicants": new_applicants,
            "applicants_trend": applicants_trend,
            "avg_applications_per_job": round(avg_applications_per_job, 1),
        },
        "pipeline": pipeline,
        "recent_jobs": recent_jobs_data
    })


@extend_schema(
    tags=["Recruiter - Jobs"],
    summary="Get Job Form Metadata",
    description="Get all metadata needed for job posting form (countries, states, cities, skills, industries, qualifications, functional areas)",
    parameters=[
        OpenApiParameter('country_id', OpenApiTypes.INT, description='Country ID to filter states'),
        OpenApiParameter('state_id', OpenApiTypes.INT, description='State ID to filter cities'),
        OpenApiParameter('search', OpenApiTypes.STR, description='Search term for filtering'),
    ],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_form_metadata(request):
    """
    Get metadata for job posting form

    This endpoint provides all the reference data needed for the job posting form:
    - Countries, States, Cities (hierarchical)
    - Skills
    - Industries
    - Qualifications
    - Functional Areas
    """
    country_id = request.GET.get('country_id')
    state_id = request.GET.get('state_id')
    search = request.GET.get('search', '')

    # Countries
    countries = Country.objects.filter(status='Enabled').order_by('name')
    countries_data = [{
        'id': c.id,
        'name': c.name,
        'slug': c.slug,
    } for c in countries]

    # States (filter by country if provided)
    states_query = State.objects.filter(status='Enabled')
    if country_id:
        states_query = states_query.filter(country_id=country_id)
    if search:
        states_query = states_query.filter(name__icontains=search)
    states = states_query.order_by('name')[:100]  # Limit to 100
    states_data = [{
        'id': s.id,
        'name': s.name,
        'slug': s.slug,
        'country_id': s.country_id,
    } for s in states]

    # Cities (filter by state if provided)
    cities_query = City.objects.filter(status='Enabled')
    if state_id:
        cities_query = cities_query.filter(state_id=state_id)
    elif country_id:
        cities_query = cities_query.filter(state__country_id=country_id)
    if search:
        cities_query = cities_query.filter(name__icontains=search)
    cities = cities_query.order_by('name')[:100]  # Limit to 100
    cities_data = [{
        'id': c.id,
        'name': c.name,
        'slug': c.slug,
        'state': {
            'id': c.state.id if c.state else None,
            'name': c.state.name if c.state else None,
        } if c.state else None
    } for c in cities]

    # Skills
    skills_query = Skill.objects.filter(status='Active')
    if search:
        skills_query = skills_query.filter(name__icontains=search)
    skills = skills_query.order_by('name')[:100]  # Limit to 100
    skills_data = [{
        'id': s.id,
        'name': s.name,
        'slug': s.slug,
    } for s in skills]

    # Industries
    industries_query = Industry.objects.filter(status='Active')
    if search:
        industries_query = industries_query.filter(name__icontains=search)
    industries = industries_query.order_by('name')[:100]  # Limit to 100
    industries_data = [{
        'id': i.id,
        'name': i.name,
        'slug': i.slug,
    } for i in industries]

    # Qualifications
    qualifications_query = Qualification.objects.filter(status='Active')
    if search:
        qualifications_query = qualifications_query.filter(name__icontains=search)
    qualifications = qualifications_query.order_by('name')[:100]  # Limit to 100
    qualifications_data = [{
        'id': q.id,
        'name': q.name,
        'slug': q.slug,
    } for q in qualifications]

    return Response({
        'countries': countries_data,
        'states': states_data,
        'cities': cities_data,
        'skills': skills_data,
        'industries': industries_data,
        'qualifications': qualifications_data,
    })


@extend_schema(
    tags=["Recruiter - Applicants"],
    summary="Get Applicant Detail",
    description="Get detailed profile of a specific applicant for a job",
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_applicant_detail(request, job_id, applicant_id):
    """Get detailed profile of an applicant"""
    user = request.user

    # Verify job ownership
    try:
        job = JobPost.objects.get(id=job_id, user=user)
    except JobPost.DoesNotExist:
        return Response(
            {"error": "Job not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get application
    try:
        application = AppliedJobs.objects.select_related('user').get(
            id=applicant_id,
            job_post=job
        )
    except AppliedJobs.DoesNotExist:
        return Response(
            {"error": "Applicant not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get detailed user profile
    applicant_user = application.user
    if not applicant_user:
        return Response(
            {"error": "Applicant user not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = ApplicantDetailSerializer(
        applicant_user,
        context={'request': request, 'job_id': job_id}
    )

    return Response(serializer.data)


@extend_schema(
    tags=["Recruiter - Applicants"],
    summary="Update Applicant Status",
    description="Update applicant status (Pending, Shortlisted, Hired, Rejected) and add remarks",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'status': {
                    'type': 'string',
                    'enum': ['Pending', 'Shortlisted', 'Hired', 'Rejected'],
                    'description': 'New status for the application'
                },
                'remarks': {
                    'type': 'string',
                    'description': 'Recruiter notes/remarks about the applicant'
                }
            }
        }
    }
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_applicant_status(request, job_id, applicant_id):
    """Update applicant status and remarks"""
    user = request.user

    # Verify job ownership
    try:
        job = JobPost.objects.get(id=job_id, user=user)
    except JobPost.DoesNotExist:
        return Response(
            {"error": "Job not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get application
    try:
        application = AppliedJobs.objects.select_related('user').get(
            id=applicant_id,
            job_post=job
        )
    except AppliedJobs.DoesNotExist:
        return Response(
            {"error": "Applicant not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Update status if provided
    new_status = request.data.get('status')
    if new_status:
        valid_statuses = ['Pending', 'Shortlisted', 'Hired', 'Rejected']
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        application.status = new_status

    # Update remarks if provided
    remarks = request.data.get('remarks')
    if remarks is not None:
        application.remarks = remarks

    application.save()

    # Return updated application
    serializer = JobApplicationSerializer(application, context={'request': request})

    return Response({
        "success": True,
        "message": f"Applicant status updated to {application.status}",
        "application": serializer.data
    })
