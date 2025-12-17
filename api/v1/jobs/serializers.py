"""
Job Serializers for API v1
"""
from rest_framework import serializers
from peeldb.models import (
    JobPost,
    City,
    Skill,
    Industry,
    Qualification,
    Company,
    AppliedJobs,
    SavedJobs,
    FunctionalArea,
)
from django.utils import timezone
from datetime import datetime, timedelta


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for job locations (cities)"""
    state = serializers.CharField(source='state.name', read_only=True)
    state_slug = serializers.CharField(source='state.slug', read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name', 'slug', 'state', 'state_slug']


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for job skills"""
    class Meta:
        model = Skill
        fields = ['id', 'name', 'slug']


class IndustrySerializer(serializers.ModelSerializer):
    """Serializer for industries"""
    class Meta:
        model = Industry
        fields = ['id', 'name', 'slug']


class QualificationSerializer(serializers.ModelSerializer):
    """Serializer for educational qualifications"""
    class Meta:
        model = Qualification
        fields = ['id', 'name', 'slug']


class FunctionalAreaSerializer(serializers.ModelSerializer):
    """Serializer for functional areas"""
    class Meta:
        model = FunctionalArea
        fields = ['id', 'name']


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for company details"""
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'name', 'slug', 'logo', 'profile_pic', 'company_type']

    def get_logo(self, obj):
        """Return company logo URL"""
        if obj.profile_pic:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_pic.url)
        return None


class JobListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for job listings
    Used in paginated list views for performance
    """
    locations = LocationSerializer(many=True, source='location', read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    industries = IndustrySerializer(many=True, source='industry', read_only=True)
    company_logo = serializers.SerializerMethodField()
    experience_display = serializers.SerializerMethodField()
    salary_display = serializers.SerializerMethodField()
    location_display = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    applicants_count = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()
    accepts_applications = serializers.SerializerMethodField()

    class Meta:
        model = JobPost
        fields = [
            'id',
            'title',
            'slug',
            'company_name',
            'company_logo',
            'job_type',
            'locations',
            'skills',
            'industries',
            'min_salary',
            'max_salary',
            'salary_type',
            'min_year',
            'max_year',
            'min_month',
            'max_month',
            'fresher',
            'published_on',
            'vacancies',
            'experience_display',
            'salary_display',
            'location_display',
            'time_ago',
            'applicants_count',
            'is_saved',
            'is_applied',
            'accepts_applications',
        ]

    def get_company_logo(self, obj):
        """Get company logo URL"""
        if obj.company and obj.company.profile_pic:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.company.profile_pic.url)
        return None

    def get_experience_display(self, obj):
        """Format experience requirement as readable string"""
        if obj.fresher:
            return "Fresher"

        min_exp = obj.min_year
        max_exp = obj.max_year

        if min_exp == 0 and max_exp == 0:
            return "Fresher"
        elif min_exp == max_exp:
            return f"{min_exp} year{'s' if min_exp != 1 else ''}"
        else:
            return f"{min_exp}-{max_exp} years"

    def get_salary_display(self, obj):
        """Format salary range as readable string"""
        if obj.min_salary == 0 and obj.max_salary == 0:
            return "Not Disclosed"

        # Normalize to LPA (Lakhs Per Annum)
        min_sal = obj.min_salary
        max_sal = obj.max_salary

        if obj.salary_type == "Month":
            min_sal = (min_sal * 12) / 100000  # Convert to lakhs
            max_sal = (max_sal * 12) / 100000
        else:
            min_sal = min_sal / 100000
            max_sal = max_sal / 100000

        if min_sal == 0 and max_sal > 0:
            return f"Up to ₹{max_sal:.1f} LPA"
        elif min_sal > 0 and max_sal == 0:
            return f"From ₹{min_sal:.1f} LPA"
        elif min_sal == max_sal:
            return f"₹{min_sal:.1f} LPA"
        else:
            return f"₹{min_sal:.1f}-{max_sal:.1f} LPA"

    def get_location_display(self, obj):
        """Get primary location for display"""
        locations = obj.location.all()
        if locations:
            location_names = [loc.name for loc in locations[:2]]
            if len(locations) > 2:
                return f"{', '.join(location_names)} +{len(locations) - 2} more"
            return ', '.join(location_names)
        return "Location not specified"

    def get_time_ago(self, obj):
        """Calculate and format time since job was published"""
        if not obj.published_on:
            return "Recently posted"

        now = timezone.now()
        diff = now - obj.published_on

        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago" if minutes > 0 else "Just now"
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.days == 1:
            return "1 day ago"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        elif diff.days < 365:
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = diff.days // 365
            return f"{years} year{'s' if years != 1 else ''} ago"

    def get_applicants_count(self, obj):
        """Get number of applicants for this job"""
        return AppliedJobs.objects.filter(job_post=obj).count()

    def get_is_saved(self, obj):
        """Check if job is saved by current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedJobs.objects.filter(job_post=obj, user=request.user).exists()
        return False

    def get_is_applied(self, obj):
        """Check if user has already applied for this job"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return AppliedJobs.objects.filter(job_post=obj, user=request.user).exists()
        return False

    def get_accepts_applications(self, obj):
        """Check if this job post can still accept applications (30-day rule)"""
        return obj.can_accept_applications()


class JobDetailSerializer(JobListSerializer):
    """
    Comprehensive serializer for job detail view
    Extends JobListSerializer with additional fields
    """
    company = CompanySerializer(read_only=True)
    edu_qualification = QualificationSerializer(many=True, read_only=True)
    functional_area = FunctionalAreaSerializer(many=True, read_only=True)

    class Meta(JobListSerializer.Meta):
        fields = JobListSerializer.Meta.fields + [
            'description',
            'job_role',
            'company',
            'company_description',
            'company_address',
            'company_links',
            'company_emails',
            'edu_qualification',
            'functional_area',
            # Walk-in specific fields
            'walkin_contactinfo',
            'walkin_show_contact_info',
            'walkin_from_date',
            'walkin_to_date',
            'walkin_time',
            # Government job specific fields
            'govt_job_type',
            'application_fee',
            'selection_process',
            'how_to_apply',
            'important_dates',
            'govt_from_date',
            'govt_to_date',
            'govt_exam_date',
            'age_relaxation',
        ]
