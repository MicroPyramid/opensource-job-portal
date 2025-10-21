"""
Serializers for Recruiter Job Management API
"""
from rest_framework import serializers
from peeldb.models import (
    JobPost, City, Skill, Industry, Qualification,
    FunctionalArea, AppliedJobs, User
)
from django.utils import timezone
from django.utils.text import slugify


class RecruiterJobListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for recruiter's job listings"""
    location_display = serializers.SerializerMethodField()
    applicants_count = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()

    class Meta:
        model = JobPost
        fields = [
            'id',
            'title',
            'slug',
            'company_name',
            'job_type',
            'status',
            'location_display',
            'applicants_count',
            'views_count',
            'vacancies',
            'created_on',
            'published_on',
            'last_date',
            'time_ago',
            'days_until_expiry',
            'is_expiring_soon',
        ]

    def get_location_display(self, obj):
        """Get primary location for display"""
        locations = obj.location.all()
        if locations:
            location_names = [loc.name for loc in locations[:2]]
            if len(locations) > 2:
                return f"{', '.join(location_names)} +{len(locations) - 2}"
            return ', '.join(location_names)
        return "Not specified"

    def get_applicants_count(self, obj):
        """Get number of applicants"""
        return obj.appliedjobs_set.count()

    def get_views_count(self, obj):
        """Get total views across all platforms"""
        return obj.fb_views + obj.tw_views + obj.ln_views + obj.other_views

    def get_time_ago(self, obj):
        """Calculate time since job was created"""
        if not obj.created_on:
            return "Recently created"

        now = timezone.now()
        diff = now - obj.created_on

        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                return "Just now"
            return f"{hours}h ago"
        elif diff.days == 1:
            return "1 day ago"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks}w ago"
        else:
            months = diff.days // 30
            return f"{months}mo ago"

    def get_days_until_expiry(self, obj):
        """Calculate days until job expires"""
        if not obj.last_date:
            return None

        now = timezone.now().date()
        if obj.last_date < now:
            return 0

        diff = obj.last_date - now
        return diff.days

    def get_is_expiring_soon(self, obj):
        """Check if job is expiring within 7 days"""
        days = self.get_days_until_expiry(obj)
        if days is None:
            return False
        return 0 < days <= 7


class RecruiterJobDetailSerializer(RecruiterJobListSerializer):
    """Comprehensive serializer for recruiter's job detail view"""
    locations = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    industries = serializers.SerializerMethodField()
    qualifications = serializers.SerializerMethodField()
    functional_areas = serializers.SerializerMethodField()

    class Meta(RecruiterJobListSerializer.Meta):
        fields = RecruiterJobListSerializer.Meta.fields + [
            'description',
            'job_role',
            'locations',
            'skills',
            'industries',
            'qualifications',
            'functional_areas',
            'min_salary',
            'max_salary',
            'salary_type',
            'min_year',
            'max_year',
            'min_month',
            'max_month',
            'fresher',
            'company_description',
            'company_address',
            'company_links',
            'company_emails',
            # Walk-in fields
            'walkin_contactinfo',
            'walkin_show_contact_info',
            'walkin_from_date',
            'walkin_to_date',
            'walkin_time',
            # Government job fields
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

    def get_locations(self, obj):
        """Get all locations with state info"""
        return [{
            'id': loc.id,
            'name': loc.name,
            'slug': loc.slug,
            'state': loc.state.name if loc.state else None,
            'state_slug': loc.state.slug if loc.state else None,
        } for loc in obj.location.all()]

    def get_skills(self, obj):
        """Get all required skills"""
        return [{
            'id': skill.id,
            'name': skill.name,
            'slug': skill.slug,
        } for skill in obj.skills.all()]

    def get_industries(self, obj):
        """Get all industries"""
        return [{
            'id': ind.id,
            'name': ind.name,
            'slug': ind.slug,
        } for ind in obj.industry.all()]

    def get_qualifications(self, obj):
        """Get all qualifications"""
        return [{
            'id': qual.id,
            'name': qual.name,
            'slug': qual.slug,
        } for qual in obj.edu_qualification.all()]

    def get_functional_areas(self, obj):
        """Get all functional areas"""
        return [{
            'id': fa.id,
            'name': fa.name,
        } for fa in obj.functional_area.all()]


class RecruiterJobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new jobs"""
    location_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    industry_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    qualification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    functional_area_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = JobPost
        fields = [
            'title',
            'job_role',
            'description',
            'company_name',
            'job_type',
            'location_ids',
            'skill_ids',
            'industry_ids',
            'qualification_ids',
            'functional_area_ids',
            'min_salary',
            'max_salary',
            'salary_type',
            'min_year',
            'max_year',
            'min_month',
            'max_month',
            'fresher',
            'vacancies',
            'last_date',
            'company_description',
            'company_address',
            'company_links',
            'company_emails',
            # Walk-in fields
            'walkin_contactinfo',
            'walkin_show_contact_info',
            'walkin_from_date',
            'walkin_to_date',
            'walkin_time',
            # Government job fields
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

    def validate(self, data):
        """Validate job data"""
        # Validate salary range
        min_sal = data.get('min_salary', 0)
        max_sal = data.get('max_salary', 0)
        if max_sal > 0 and min_sal > max_sal:
            raise serializers.ValidationError({
                'min_salary': 'Minimum salary cannot be greater than maximum salary'
            })

        # Validate experience range
        min_year = data.get('min_year', 0)
        max_year = data.get('max_year', 0)
        if max_year > 0 and min_year > max_year:
            raise serializers.ValidationError({
                'min_year': 'Minimum experience cannot be greater than maximum experience'
            })

        # Validate last_date is in future
        last_date = data.get('last_date')
        if last_date and last_date < timezone.now().date():
            raise serializers.ValidationError({
                'last_date': 'Last date must be in the future'
            })

        return data

    def create(self, validated_data):
        """Create job with related data"""
        # Extract many-to-many IDs
        location_ids = validated_data.pop('location_ids', [])
        skill_ids = validated_data.pop('skill_ids', [])
        industry_ids = validated_data.pop('industry_ids', [])
        qualification_ids = validated_data.pop('qualification_ids', [])
        functional_area_ids = validated_data.pop('functional_area_ids', [])

        # Get user from context
        user = self.context['user']

        # Auto-fill company info if user has company
        if user.company:
            validated_data['company'] = user.company
            if not validated_data.get('company_name'):
                validated_data['company_name'] = user.company.name

        # Generate slug
        if not validated_data.get('slug'):
            validated_data['slug'] = slugify(validated_data['title'])

        # Set default status to Draft
        if 'status' not in validated_data:
            validated_data['status'] = 'Draft'

        # Create job
        job = JobPost.objects.create(**validated_data)

        # Set many-to-many relationships
        if location_ids:
            job.location.set(City.objects.filter(id__in=location_ids))
        if skill_ids:
            job.skills.set(Skill.objects.filter(id__in=skill_ids))
        if industry_ids:
            job.industry.set(Industry.objects.filter(id__in=industry_ids))
        if qualification_ids:
            job.edu_qualification.set(Qualification.objects.filter(id__in=qualification_ids))
        if functional_area_ids:
            job.functional_area.set(FunctionalArea.objects.filter(id__in=functional_area_ids))

        return job


class RecruiterJobUpdateSerializer(RecruiterJobCreateSerializer):
    """Serializer for updating existing jobs"""
    class Meta(RecruiterJobCreateSerializer.Meta):
        # Make all fields optional for updates
        extra_kwargs = {
            field: {'required': False}
            for field in RecruiterJobCreateSerializer.Meta.fields
        }

    def update(self, instance, validated_data):
        """Update job with related data"""
        # Extract many-to-many IDs
        location_ids = validated_data.pop('location_ids', None)
        skill_ids = validated_data.pop('skill_ids', None)
        industry_ids = validated_data.pop('industry_ids', None)
        qualification_ids = validated_data.pop('qualification_ids', None)
        functional_area_ids = validated_data.pop('functional_area_ids', None)

        # Update basic fields
        for field, value in validated_data.items():
            setattr(instance, field, value)

        # Update slug if title changed
        if 'title' in validated_data:
            instance.slug = slugify(validated_data['title'])

        instance.save()

        # Update many-to-many relationships if provided
        if location_ids is not None:
            instance.location.set(City.objects.filter(id__in=location_ids))
        if skill_ids is not None:
            instance.skills.set(Skill.objects.filter(id__in=skill_ids))
        if industry_ids is not None:
            instance.industry.set(Industry.objects.filter(id__in=industry_ids))
        if qualification_ids is not None:
            instance.edu_qualification.set(Qualification.objects.filter(id__in=qualification_ids))
        if functional_area_ids is not None:
            instance.functional_area.set(FunctionalArea.objects.filter(id__in=functional_area_ids))

        return instance


class JobApplicationSerializer(serializers.ModelSerializer):
    """Serializer for job applications"""
    applicant = serializers.SerializerMethodField()
    applied_time_ago = serializers.SerializerMethodField()

    class Meta:
        model = AppliedJobs
        fields = [
            'id',
            'applicant',
            'status',
            'applied_on',
            'applied_time_ago',
        ]

    def get_applicant(self, obj):
        """Get applicant basic info"""
        user = obj.user
        return {
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}".strip() or user.email,
            'email': user.email,
            'profile_pic': user.profile_pic.url if user.profile_pic else None,
        }

    def get_applied_time_ago(self, obj):
        """Calculate time since application"""
        now = timezone.now()
        diff = now - obj.applied_on

        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                return "Just now"
            return f"{hours}h ago"
        elif diff.days == 1:
            return "1 day ago"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        else:
            weeks = diff.days // 7
            return f"{weeks}w ago"
