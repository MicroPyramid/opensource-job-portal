"""
Application-focused analytics endpoints for recruiters
Focus on actionable metrics: applications, pipeline, hiring success
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta, datetime, date
from peeldb.models import JobPost, AppliedJobs


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_application_analytics(request):
    """
    Get comprehensive application analytics for recruiter
    Query params: period (7d, 30d, 90d, custom), start_date, end_date
    """
    # Parse period
    period = request.GET.get('period', '30d')
    end_date = timezone.now()

    if period == '7d':
        start_date = end_date - timedelta(days=7)
        prev_days = 7
    elif period == '90d':
        start_date = end_date - timedelta(days=90)
        prev_days = 90
    elif period == 'custom':
        try:
            start_date = timezone.make_aware(
                datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d')
            )
            end_date = timezone.make_aware(
                datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d')
            )
            prev_days = (end_date - start_date).days
        except (ValueError, TypeError):
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
    else:
        start_date = end_date - timedelta(days=30)
        prev_days = 30

    prev_start_date = start_date - timedelta(days=prev_days)

    # Get recruiter's jobs
    jobs = JobPost.objects.filter(user=request.user)

    # Applications in period
    applications = AppliedJobs.objects.filter(
        job_post__in=jobs,
        applied_on__gte=start_date,
        applied_on__lte=end_date
    )

    # Applications in previous period
    prev_applications = AppliedJobs.objects.filter(
        job_post__in=jobs,
        applied_on__gte=prev_start_date,
        applied_on__lt=start_date
    )

    # Calculate overview metrics
    total_applications = applications.count()
    prev_total = prev_applications.count()

    if prev_total > 0:
        trend_pct = ((total_applications - prev_total) / prev_total) * 100
        trend = f"{'+' if trend_pct > 0 else ''}{trend_pct:.1f}%"
    else:
        trend = "N/A"

    avg_per_day = total_applications / prev_days if prev_days > 0 else 0

    # Pipeline breakdown
    pipeline = {
        'pending': applications.filter(status='Pending').count(),
        'shortlisted': applications.filter(status='Shortlisted').count(),
        'hired': applications.filter(status='Hired').count(),
        'rejected': applications.filter(status='Rejected').count(),
    }

    if total_applications > 0:
        pipeline['conversion_rate'] = round(
            (pipeline['hired'] / total_applications) * 100, 2
        )
    else:
        pipeline['conversion_rate'] = 0

    # Applications by day
    applications_by_day = (
        applications
        .extra(select={'day': 'DATE(applied_on)'})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    # Peak days (day of week analysis)
    from django.db.models.functions import ExtractWeekDay
    peak_days_data = (
        applications
        .annotate(weekday=ExtractWeekDay('applied_on'))
        .values('weekday')
        .annotate(count=Count('id'))
    )

    # Map weekday numbers to names (1=Sunday in Django)
    weekday_map = {
        1: 'sunday', 2: 'monday', 3: 'tuesday', 4: 'wednesday',
        5: 'thursday', 6: 'friday', 7: 'saturday'
    }
    peak_days = {day: 0 for day in weekday_map.values()}
    for item in peak_days_data:
        day_name = weekday_map.get(item['weekday'])
        if day_name:
            peak_days[day_name] = item['count']

    # Job performance
    job_performance = []
    for job in jobs.filter(status='Live'):
        job_apps = applications.filter(job_post=job)
        total_job_apps = job_apps.count()

        # Calculate days active and avg per day
        if job.created_on:
            try:
                # Convert created_on to timezone-aware datetime
                if isinstance(job.created_on, datetime):
                    # It's a datetime object
                    created = job.created_on
                    if not timezone.is_aware(created):
                        # Make it timezone-aware
                        created = timezone.make_aware(created)
                elif isinstance(job.created_on, date):
                    # It's a date object, convert to datetime first
                    created = timezone.make_aware(
                        datetime.combine(job.created_on, datetime.min.time())
                    )
                else:
                    # Unknown type, skip calculation
                    days_active = 0
                    avg_per_day = 0
                    created = None

                if created:
                    days_active = (timezone.now() - created).days
                    # Prevent division by zero
                    avg_per_day = total_job_apps / days_active if days_active > 0 else 0
                else:
                    days_active = 0
                    avg_per_day = 0
            except Exception:
                # If anything goes wrong, default to 0
                days_active = 0
                avg_per_day = 0
        else:
            days_active = 0
            avg_per_day = 0

        hired_count = job_apps.filter(status='Hired').count()
        conversion = (hired_count / total_job_apps * 100) if total_job_apps > 0 else 0

        job_performance.append({
            'job_id': job.id,
            'job_title': job.title,
            'total_applications': total_job_apps,
            'new_applications': total_job_apps,
            'pending': job_apps.filter(status='Pending').count(),
            'shortlisted': job_apps.filter(status='Shortlisted').count(),
            'hired': hired_count,
            'rejected': job_apps.filter(status='Rejected').count(),
            'conversion_rate': round(conversion, 2),
            'days_active': days_active,
            'avg_applications_per_day': round(avg_per_day, 1),
            'status': job.status
        })

    # Sort by total applications
    job_performance.sort(key=lambda x: x['total_applications'], reverse=True)

    return Response({
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
            'label': period
        },
        'overview': {
            'total_applications': total_applications,
            'new_applications': total_applications,
            'trend': trend,
            'avg_per_day': round(avg_per_day, 1),
            'total_jobs': jobs.filter(status='Live').count()
        },
        'pipeline': pipeline,
        'applications_by_day': list(applications_by_day),
        'job_performance': job_performance[:10],  # Top 10 jobs
        'peak_days': peak_days
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_application_analytics(request, job_id):
    """
    Get application analytics for a specific job
    Query params: period (7d, 30d, 90d)
    """
    try:
        job = JobPost.objects.get(id=job_id, user=request.user)
    except JobPost.DoesNotExist:
        return Response({'error': 'Job not found'}, status=404)

    period = request.GET.get('period', '30d')
    end_date = timezone.now()

    if period == '7d':
        start_date = end_date - timedelta(days=7)
        days_in_period = 7
    elif period == '90d':
        start_date = end_date - timedelta(days=90)
        days_in_period = 90
    else:
        start_date = end_date - timedelta(days=30)
        days_in_period = 30

    # Get applications for this job in period
    applications = AppliedJobs.objects.filter(
        job_post=job,
        applied_on__gte=start_date
    )

    total_apps = applications.count()

    # Pipeline
    pipeline = {
        'pending': applications.filter(status='Pending').count(),
        'shortlisted': applications.filter(status='Shortlisted').count(),
        'hired': applications.filter(status='Hired').count(),
        'rejected': applications.filter(status='Rejected').count(),
    }

    if total_apps > 0:
        pipeline['conversion_rate'] = round(
            (pipeline['hired'] / total_apps) * 100, 2
        )
    else:
        pipeline['conversion_rate'] = 0

    # Applications by day
    apps_by_day = (
        applications
        .extra(select={'day': 'DATE(applied_on)'})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    return Response({
        'job_id': job_id,
        'job_title': job.title,
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
            'label': period
        },
        'metrics': {
            'total_applications': total_apps,
            'avg_per_day': round(total_apps / days_in_period, 1),
        },
        'pipeline': pipeline,
        'applications_by_day': list(apps_by_day)
    })
