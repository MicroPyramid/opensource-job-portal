"""
Company Serializers for API v1
"""
from rest_framework import serializers
from peeldb.models import Company, JobPost


class CompanyListSerializer(serializers.ModelSerializer):
    """
    Serializer for company listings with job counts
    """
    logo = serializers.SerializerMethodField()
    job_count = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    industry_name = serializers.SerializerMethodField()
    nature_of_business = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'slug',
            'logo',
            'company_type',
            'size',
            'industry_name',
            'location',
            'job_count',
            'nature_of_business',
        ]

    def get_logo(self, obj):
        """Return company logo URL"""
        if obj.profile_pic:
            request = self.context.get('request')
            if request:
                try:
                    return request.build_absolute_uri(obj.profile_pic.url)
                except Exception:
                    pass
        # Return default logo
        return 'https://cdn.peeljobs.com/static/company_logo.png'

    def get_job_count(self, obj):
        """Return count of live job posts for this company"""
        return JobPost.objects.filter(
            company=obj,
            status='Live'
        ).count()

    def get_location(self, obj):
        """Return company location from address or job locations"""
        if obj.address:
            # Extract city from address (simple approach)
            return obj.address.split(',')[0] if ',' in obj.address else obj.address[:50]

        # Fallback: Get location from job posts
        job = JobPost.objects.filter(company=obj, status='Live').first()
        if job and job.location.exists():
            city = job.location.first()
            return f"{city.name}, {city.state.name}"

        return "Multiple Locations"

    def get_industry_name(self, obj):
        """Return industry name from job posts"""
        job = JobPost.objects.filter(
            company=obj,
            status='Live',
            industry__isnull=False
        ).first()

        if job and job.industry.exists():
            return job.industry.first().name

        return "Technology"

    def get_nature_of_business(self, obj):
        """Return nature of business tags"""
        # Simple heuristic based on company type and industry
        tags = []

        if obj.company_type == 'Company':
            tags.append('B2B')
        elif obj.company_type == 'Consultant':
            tags.append('B2B')
            tags.append('Services')

        # Add based on size
        if obj.size in ['200+', '50-200']:
            tags.append('Enterprise')

        return tags[:3]  # Max 3 tags


class CompanyDetailSerializer(serializers.ModelSerializer):
    """
    Detailed company serializer for company profile page
    """
    logo = serializers.SerializerMethodField()
    job_count = serializers.SerializerMethodField()
    active_jobs = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'slug',
            'logo',
            'company_type',
            'size',
            'profile',
            'website',
            'address',
            'phone_number',
            'email',
            'registered_date',
            'job_count',
            'active_jobs',
        ]

    def get_logo(self, obj):
        """Return company logo URL"""
        if obj.profile_pic:
            request = self.context.get('request')
            if request:
                try:
                    return request.build_absolute_uri(obj.profile_pic.url)
                except Exception:
                    pass
        return 'https://cdn.peeljobs.com/static/company_logo.png'

    def get_job_count(self, obj):
        """Return count of live job posts"""
        return JobPost.objects.filter(company=obj, status='Live').count()

    def get_active_jobs(self, obj):
        """Return list of active jobs (limited)"""
        from api.v1.jobs.serializers import JobListSerializer

        jobs = JobPost.objects.filter(
            company=obj,
            status='Live'
        ).order_by('-created_on')[:10]

        return JobListSerializer(
            jobs,
            many=True,
            context=self.context
        ).data
