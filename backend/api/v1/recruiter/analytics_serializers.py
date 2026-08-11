"""
Response serializers for the recruiter analytics endpoints.

These mirror the dict literals built in ``analytics_views.py``. Both endpoints
assemble their payload by hand rather than from a model serializer, so there was
no serializer for drf-spectacular to infer and the operations were being dropped
from the schema entirely.

Documentation only: nothing here is applied to an outgoing response at runtime.
"""

from rest_framework import serializers


class AnalyticsPeriodSerializer(serializers.Serializer):
    """The requested reporting window, echoed back on every analytics response."""

    start = serializers.DateTimeField(help_text="ISO 8601 start of the window")
    end = serializers.DateTimeField(help_text="ISO 8601 end of the window")
    label = serializers.CharField(help_text="'7d', '30d', '90d' or 'custom'")


class AnalyticsPipelineSerializer(serializers.Serializer):
    """Applicant counts by stage, plus the hire conversion rate."""

    pending = serializers.IntegerField()
    shortlisted = serializers.IntegerField()
    hired = serializers.IntegerField()
    rejected = serializers.IntegerField()
    conversion_rate = serializers.FloatField(
        help_text="Hired as a percentage of applications; 0 when there are none"
    )


class AnalyticsDailyCountSerializer(serializers.Serializer):
    """One bar of the applications-per-day series."""

    day = serializers.DateField()
    count = serializers.IntegerField()


class AnalyticsOverviewSerializer(serializers.Serializer):
    """Headline numbers for the whole account over the period."""

    total_applications = serializers.IntegerField()
    new_applications = serializers.IntegerField(
        help_text="Currently identical to total_applications"
    )
    trend = serializers.CharField(
        help_text="Percentage change vs the preceding window, or 'N/A' with no baseline"
    )
    avg_per_day = serializers.FloatField()
    total_jobs = serializers.IntegerField(help_text="Count of Live jobs")


class AnalyticsJobPerformanceSerializer(serializers.Serializer):
    """Per-job breakdown, returned for Live jobs only."""

    job_id = serializers.IntegerField()
    job_title = serializers.CharField()
    total_applications = serializers.IntegerField()
    new_applications = serializers.IntegerField(
        help_text="Currently identical to total_applications"
    )
    pending = serializers.IntegerField()
    shortlisted = serializers.IntegerField()
    hired = serializers.IntegerField()
    rejected = serializers.IntegerField()
    conversion_rate = serializers.FloatField()
    days_active = serializers.IntegerField(
        help_text="0 when the creation date is missing or unparseable"
    )
    avg_applications_per_day = serializers.FloatField()
    status = serializers.CharField()


class AnalyticsPeakDaysSerializer(serializers.Serializer):
    """Application counts bucketed by day of week."""

    monday = serializers.IntegerField()
    tuesday = serializers.IntegerField()
    wednesday = serializers.IntegerField()
    thursday = serializers.IntegerField()
    friday = serializers.IntegerField()
    saturday = serializers.IntegerField()
    sunday = serializers.IntegerField()


class ApplicationAnalyticsResponseSerializer(serializers.Serializer):
    """200 response from ``get_application_analytics``."""

    period = AnalyticsPeriodSerializer()
    overview = AnalyticsOverviewSerializer()
    pipeline = AnalyticsPipelineSerializer()
    applications_by_day = AnalyticsDailyCountSerializer(many=True)
    job_performance = AnalyticsJobPerformanceSerializer(
        many=True, help_text="Top 10 jobs by application volume"
    )
    peak_days = AnalyticsPeakDaysSerializer()


class JobAnalyticsMetricsSerializer(serializers.Serializer):
    """Headline numbers for a single job."""

    total_applications = serializers.IntegerField()
    avg_per_day = serializers.FloatField()


class JobApplicationAnalyticsResponseSerializer(serializers.Serializer):
    """200 response from ``get_job_application_analytics``."""

    job_id = serializers.IntegerField()
    job_title = serializers.CharField()
    period = AnalyticsPeriodSerializer()
    metrics = JobAnalyticsMetricsSerializer()
    pipeline = AnalyticsPipelineSerializer()
    applications_by_day = AnalyticsDailyCountSerializer(many=True)
