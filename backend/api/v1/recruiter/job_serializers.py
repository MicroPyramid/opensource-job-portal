"""
Serializers for Recruiter Job Management API
"""
import datetime
from rest_framework import serializers
from peeldb.models import (
    JobPost, City, Skill, Industry, Qualification,
    AppliedJobs, User
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
    accepts_applications = serializers.SerializerMethodField()

    class Meta:
        model = JobPost
        fields = [
            'id',
            'title',
            'slug',
            'company_name',
            'job_type',
            'work_mode',
            'status',
            'location_display',
            'applicants_count',
            'views_count',
            'vacancies',
            'created_on',
            'published_on',
            'time_ago',
            'days_until_expiry',
            'is_expiring_soon',
            'accepts_applications',
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
        # Social media view fields have been removed
        return 0  # TODO: Implement proper analytics tracking

    def get_time_ago(self, obj):
        """Calculate time since job was created"""
        if not obj.created_on:
            return "Recently created"

        try:
            now = timezone.now()

            # Handle both datetime and date objects
            if isinstance(obj.created_on, datetime.date) and not isinstance(obj.created_on, datetime.datetime):
                # Convert date to datetime at midnight
                created_datetime = datetime.datetime.combine(obj.created_on, datetime.time.min)
                # Make timezone aware
                created_datetime = timezone.make_aware(created_datetime)
            elif isinstance(obj.created_on, datetime.datetime):
                created_datetime = obj.created_on
                # Ensure datetime is timezone aware
                if timezone.is_naive(created_datetime):
                    created_datetime = timezone.make_aware(created_datetime)
            else:
                return "Recently created"

            diff = now - created_datetime
        except Exception as e:
            # If anything goes wrong, just return a default
            return "Recently created"

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
        """Calculate days until job expires (30-day rule from published_on)"""
        if not obj.published_on:
            return None

        from django.conf import settings
        max_age_days = getattr(settings, 'JOB_APPLICATION_MAX_AGE_DAYS', 30)
        age = timezone.now() - obj.published_on
        days_remaining = max_age_days - age.days

        return days_remaining if days_remaining >= 0 else 0

    def get_is_expiring_soon(self, obj):
        """Check if job is expiring within 7 days"""
        days = self.get_days_until_expiry(obj)
        if days is None:
            return False
        return 0 < days <= 7

    def get_accepts_applications(self, obj):
        """Check if this job post can still accept applications (30-day rule)"""
        return obj.can_accept_applications()


class RecruiterJobDetailSerializer(RecruiterJobListSerializer):
    """Comprehensive serializer for recruiter's job detail view"""
    locations = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    industries = serializers.SerializerMethodField()
    qualifications = serializers.SerializerMethodField()

    class Meta(RecruiterJobListSerializer.Meta):
        fields = RecruiterJobListSerializer.Meta.fields + [
            'description',
            'job_role',
            'locations',
            'skills',
            'industries',
            'qualifications',
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
            # New enhanced fields
            'seniority_level',
            'application_method',
            'application_url',
            'show_salary',
            'benefits',
            'language_requirements',
            'required_certifications',
            'preferred_certifications',
            'relocation_required',
            'travel_percentage',
            'hiring_timeline',
            'hiring_priority',
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


class RecruiterJobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new jobs"""
    location_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    industry_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    qualification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )

    # Override model fields to make them not required for drafts
    title = serializers.CharField(required=True, allow_blank=False)
    job_role = serializers.CharField(required=False, allow_blank=True, default='')
    description = serializers.CharField(required=False, allow_blank=True, default='')
    company_name = serializers.CharField(required=False, allow_blank=True, default='')
    job_type = serializers.CharField(required=False, allow_blank=True)
    work_mode = serializers.CharField(required=False, allow_blank=True)
    company_description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    company_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    company_links = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    company_emails = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Numeric fields with defaults
    vacancies = serializers.IntegerField(required=False, default=1)
    min_salary = serializers.IntegerField(required=False, default=0)
    max_salary = serializers.IntegerField(required=False, default=0)
    min_year = serializers.IntegerField(required=False, default=0)
    max_year = serializers.IntegerField(required=False, default=0)
    min_month = serializers.IntegerField(required=False, default=0)
    max_month = serializers.IntegerField(required=False, default=0)

    class Meta:
        model = JobPost
        fields = [
            'title',
            'job_role',
            'description',
            'company_name',
            'job_type',
            'work_mode',
            'location_ids',
            'skill_ids',
            'industry_ids',
            'qualification_ids',
            'min_salary',
            'max_salary',
            'salary_type',
            'min_year',
            'max_year',
            'min_month',
            'max_month',
            'fresher',
            'vacancies',
            'company_description',
            'company_address',
            'company_links',
            'company_emails',
            # New enhanced fields
            'seniority_level',
            'application_method',
            'application_url',
            'show_salary',
            'benefits',
            'language_requirements',
            'required_certifications',
            'preferred_certifications',
            'relocation_required',
            'travel_percentage',
            'hiring_timeline',
            'hiring_priority',
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

        return data

    def create(self, validated_data):
        """Create job with related data"""
        # Extract many-to-many IDs
        location_ids = validated_data.pop('location_ids', [])
        skill_ids = validated_data.pop('skill_ids', [])
        industry_ids = validated_data.pop('industry_ids', [])
        qualification_ids = validated_data.pop('qualification_ids', [])

        # Get user from context
        user = self.context['user']

        # Auto-fill company info if user has company
        if user.company:
            validated_data['company'] = user.company
            if not validated_data.get('company_name'):
                validated_data['company_name'] = user.company.name

        # Generate slug
        if not validated_data.get('slug'):
            title = validated_data.get('title', 'untitled-job')
            validated_data['slug'] = slugify(title) if title else 'untitled-job'

        # Set default status to Draft
        if 'status' not in validated_data:
            validated_data['status'] = 'Draft'

        # Set default values for required fields
        if 'vacancies' not in validated_data or validated_data['vacancies'] is None:
            validated_data['vacancies'] = 1

        if 'job_type' not in validated_data or not validated_data['job_type']:
            validated_data['job_type'] = 'full-time'

        if 'work_mode' not in validated_data or not validated_data['work_mode']:
            validated_data['work_mode'] = 'in-office'

        # Set default meta fields (required by model but auto-generated)
        if 'meta_title' not in validated_data:
            validated_data['meta_title'] = validated_data.get('title', '')
        if 'meta_description' not in validated_data:
            # Use first 160 chars of description as meta description
            desc = validated_data.get('description', '')
            validated_data['meta_description'] = desc[:160] if desc else ''

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
            'remarks',
        ]

    def get_applicant(self, obj):
        """Get applicant basic info"""
        user = obj.user
        if not user:
            return None

        # Calculate experience
        years = int(user.year) if user.year and user.year.isdigit() else 0
        months = int(user.month) if user.month and user.month.isdigit() else 0

        experience_str = ""
        if years > 0:
            experience_str = f"{years}y"
        if months > 0:
            experience_str += f" {months}m" if experience_str else f"{months}m"
        if not experience_str:
            experience_str = "Fresher"

        return {
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}".strip() or user.email,
            'email': user.email,
            'mobile': user.mobile,
            'profile_pic': user.profile_pic.url if user.profile_pic else None,
            'experience': experience_str,
            'current_location': user.current_city.name if user.current_city else None,
            'resume_url': user.resume.url if user.resume else None,
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


class ApplicantDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for applicant profile"""
    application = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    employment_history = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    certifications = serializers.SerializerMethodField()
    experience = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'mobile',
            'profile_pic',
            'experience',
            'location',
            'profile_description',
            'resume',
            'current_salary',
            'expected_salary',
            'notice_period',
            'relocation',
            'show_email',
            'skills',
            'employment_history',
            'education',
            'certifications',
            'application',
        ]

    def get_application(self, obj):
        """Get application details for this job"""
        request = self.context.get('request')
        job_id = self.context.get('job_id')

        if job_id:
            try:
                application = AppliedJobs.objects.get(user=obj, job_post_id=job_id)
                return {
                    'id': application.id,
                    'status': application.status,
                    'applied_on': application.applied_on,
                    'remarks': application.remarks,
                }
            except AppliedJobs.DoesNotExist:
                pass

        return None

    def get_experience(self, obj):
        """Get formatted experience"""
        years = int(obj.year) if obj.year and obj.year.isdigit() else 0
        months = int(obj.month) if obj.month and obj.month.isdigit() else 0

        return {
            'years': years,
            'months': months,
            'total_months': years * 12 + months,
            'display': f"{years}y {months}m" if years > 0 else (f"{months}m" if months > 0 else "Fresher")
        }

    def get_location(self, obj):
        """Get location details"""
        location_data = {
            'current_city': obj.current_city.name if obj.current_city else None,
            'current_state': obj.current_city.state.name if obj.current_city and obj.current_city.state else None,
            'preferred_cities': [city.name for city in obj.preferred_city.all()[:5]],
            'relocation': obj.relocation,
        }

        if obj.city:
            location_data['city'] = obj.city.name
            location_data['state'] = obj.city.state.name if obj.city.state else None

        return location_data

    def get_skills(self, obj):
        """Get technical skills"""
        skills = []
        for tech_skill in obj.skills.all():
            skill_data = {
                'name': tech_skill.skill.name,
                'years': tech_skill.year,
                'months': tech_skill.month,
                'proficiency': tech_skill.proficiency,
                'last_used': tech_skill.last_used,
                'is_major': tech_skill.is_major,
            }
            skills.append(skill_data)

        return skills

    def get_employment_history(self, obj):
        """Get employment history"""
        history = []
        for emp in obj.employment_history.all():
            history.append({
                'company': emp.company,
                'designation': emp.designation,
                'from_date': emp.from_date,
                'to_date': emp.to_date,
                'current_job': emp.current_job,
                'job_profile': emp.job_profile,
            })

        return history

    def get_education(self, obj):
        """Get education details"""
        education = []
        for edu in obj.education.all():
            education.append({
                'institute': edu.institute.name if edu.institute else None,
                'degree': edu.degree.degree_name.name if edu.degree and edu.degree.degree_name else None,
                'specialization': edu.degree.specialization if edu.degree else None,
                'from_date': edu.from_date,
                'to_date': edu.to_date,
                'score': edu.score,
                'current_education': edu.current_education,
            })

        return education

    def get_certifications(self, obj):
        """Get certifications"""
        certifications = []
        for cert in obj.user_certifications.all():
            certifications.append({
                'name': cert.name,
                'organization': cert.organization,
                'credential_id': cert.credential_id,
                'credential_url': cert.credential_url,
                'issued_date': cert.issued_date,
                'expiry_date': cert.expiry_date,
                'does_not_expire': cert.does_not_expire,
            })

        return certifications
