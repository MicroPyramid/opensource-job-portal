"""
Profile Serializers for Job Seekers
"""
from rest_framework import serializers
from peeldb.models import (
    User, City, State, Country, Skill, TechnicalSkill,
    EmploymentHistory, EducationDetails, Degree, Qualification,
    EducationInstitue, Project, Certification
)


class CitySerializer(serializers.ModelSerializer):
    """City serializer with state and country info"""
    state_name = serializers.CharField(source='state.name', read_only=True)
    country_name = serializers.CharField(source='state.country.name', read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name', 'slug', 'state_name', 'country_name']
        read_only_fields = fields


class StateSerializer(serializers.ModelSerializer):
    """State serializer"""
    country_name = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = State
        fields = ['id', 'name', 'slug', 'country_name']
        read_only_fields = fields


class CountrySerializer(serializers.ModelSerializer):
    """Country serializer"""

    class Meta:
        model = Country
        fields = ['id', 'name', 'slug']
        read_only_fields = fields


class SkillSerializer(serializers.ModelSerializer):
    """Skill serializer"""

    class Meta:
        model = Skill
        fields = ['id', 'name', 'slug', 'skill_type']
        read_only_fields = fields


class TechnicalSkillSerializer(serializers.ModelSerializer):
    """Technical skill with proficiency serializer"""
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.filter(status='Active'),
        source='skill',
        write_only=True
    )

    class Meta:
        model = TechnicalSkill
        fields = [
            'id', 'skill', 'skill_id', 'year', 'month',
            'last_used', 'version', 'proficiency', 'is_major'
        ]


class EmploymentHistorySerializer(serializers.ModelSerializer):
    """Employment history serializer"""

    class Meta:
        model = EmploymentHistory
        fields = [
            'id', 'company', 'designation', 'from_date',
            'to_date', 'current_job', 'job_profile'
        ]


class QualificationSerializer(serializers.ModelSerializer):
    """Qualification (degree type) serializer"""

    class Meta:
        model = Qualification
        fields = ['id', 'name', 'slug']
        read_only_fields = fields


class DegreeSerializer(serializers.ModelSerializer):
    """Degree serializer with qualification details"""
    qualification = QualificationSerializer(source='degree_name', read_only=True)

    class Meta:
        model = Degree
        fields = ['id', 'qualification', 'degree_type', 'specialization']
        read_only_fields = fields


class EducationInstituteSerializer(serializers.ModelSerializer):
    """Education institute serializer"""
    city_name = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = EducationInstitue
        fields = ['id', 'name', 'address', 'city_name']
        read_only_fields = fields


class EducationDetailsSerializer(serializers.ModelSerializer):
    """Education details serializer with read/write support"""
    # Read-only nested fields
    institute_name = serializers.CharField(source='institute.name', read_only=True)
    institute_address = serializers.CharField(source='institute.address', read_only=True)
    degree_name = serializers.CharField(source='degree.degree_name.name', read_only=True)
    degree_type = serializers.CharField(source='degree.degree_type', read_only=True)
    specialization = serializers.CharField(source='degree.specialization', read_only=True)

    # Write-only fields for creating/updating
    institute_id = serializers.PrimaryKeyRelatedField(
        queryset=EducationInstitue.objects.all(),
        source='institute',
        write_only=True,
        required=False,
        allow_null=True
    )
    degree_id = serializers.PrimaryKeyRelatedField(
        queryset=Degree.objects.all(),
        source='degree',
        write_only=True
    )

    # Custom institute name for "Other" option
    custom_institute_name = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=500
    )

    class Meta:
        model = EducationDetails
        fields = [
            'id', 'institute_id', 'institute_name', 'institute_address',
            'degree_id', 'degree_name', 'degree_type', 'specialization',
            'from_date', 'to_date', 'score', 'current_education',
            'custom_institute_name'
        ]

    def validate(self, data):
        """Validate education details"""
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        current_education = data.get('current_education', False)
        institute = data.get('institute')
        custom_institute_name = data.get('custom_institute_name', '').strip()

        # Validate institute - either select existing or provide custom name
        if not institute and not custom_institute_name:
            raise serializers.ValidationError({
                'institute_id': 'Please select an institute or enter a custom institute name'
            })

        # If custom institute name provided, create or get the institute
        if custom_institute_name and not institute:
            institute, created = EducationInstitue.objects.get_or_create(
                name__iexact=custom_institute_name,
                defaults={'name': custom_institute_name, 'address': ''}
            )
            data['institute'] = institute

        # Remove custom_institute_name from data as it's not a model field
        data.pop('custom_institute_name', None)

        # If current education, to_date should be None
        if current_education and to_date:
            raise serializers.ValidationError({
                'to_date': 'Current education should not have an end date'
            })

        # If not current, to_date should be >= from_date
        if not current_education and to_date and from_date:
            if to_date < from_date:
                raise serializers.ValidationError({
                    'to_date': 'End date must be after start date'
                })

        return data


class ProjectSerializer(serializers.ModelSerializer):
    """Project serializer"""
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.filter(status='Active'),
        source='skills',
        many=True,
        write_only=True
    )
    location = CitySerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.filter(status='Enabled'),
        source='location',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'from_date', 'to_date', 'skills', 'skill_ids',
            'description', 'location', 'location_id', 'role', 'size'
        ]


class CertificationSerializer(serializers.ModelSerializer):
    """Certification serializer"""

    class Meta:
        model = Certification
        fields = [
            'id', 'name', 'organization', 'credential_id', 'credential_url',
            'issued_date', 'expiry_date', 'does_not_expire', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProfileSerializer(serializers.ModelSerializer):
    """
    Job Seeker Profile Serializer for GET/PUT operations

    This serializer handles the job seeker's complete profile including:
    - Personal information
    - Contact details
    - Location preferences
    - Skills and experience
    - Employment history
    - Education
    - Projects and certifications
    """

    # Read-only computed fields
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    profile_completion_percentage = serializers.IntegerField(read_only=True)
    is_gp_connected = serializers.BooleanField(read_only=True)

    # Nested read serializers for related data
    city = CitySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    country = CountrySerializer(read_only=True)
    current_city = CitySerializer(read_only=True)
    preferred_city = CitySerializer(many=True, read_only=True)

    # Skills
    skills = TechnicalSkillSerializer(many=True, read_only=True)

    # Employment, Education, Projects, Certifications
    employment_history = EmploymentHistorySerializer(many=True, read_only=True)
    education = EducationDetailsSerializer(many=True, read_only=True)
    project = ProjectSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(source='user_certifications', many=True, read_only=True)

    # Write-only fields for updating relationships
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.filter(status='Enabled'),
        source='city',
        write_only=True,
        required=False,
        allow_null=True
    )
    state_id = serializers.PrimaryKeyRelatedField(
        queryset=State.objects.filter(status='Enabled'),
        source='state',
        write_only=True,
        required=False,
        allow_null=True
    )
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.filter(status='Enabled'),
        source='country',
        write_only=True,
        required=False,
        allow_null=True
    )
    current_city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.filter(status='Enabled'),
        source='current_city',
        write_only=True,
        required=False,
        allow_null=True
    )
    preferred_city_ids = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.filter(status='Enabled'),
        source='preferred_city',
        many=True,
        write_only=True,
        required=False
    )

    # File fields
    profile_pic_url = serializers.SerializerMethodField()
    resume_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            # Basic Info
            'id', 'email', 'username', 'first_name', 'last_name',
            'user_type', 'user_type_display', 'profile_completion_percentage',

            # Profile Picture & Photo
            'profile_pic', 'profile_pic_url', 'photo',

            # Contact Info
            'mobile', 'alternate_mobile', 'show_email',

            # Personal Info
            'gender', 'dob', 'marital_status', 'nationality',

            # Location Info
            'address', 'permanent_address', 'pincode',
            'city', 'city_id', 'state', 'state_id', 'country', 'country_id',
            'current_city', 'current_city_id', 'preferred_city', 'preferred_city_ids',

            # Professional Info
            'job_role', 'profile_description', 'year', 'month',
            'current_salary', 'expected_salary', 'notice_period',
            'relocation', 'is_looking_for_job', 'is_open_to_offers',

            # Resume
            'resume', 'resume_url', 'resume_title', 'resume_text',

            # Related Data
            'skills', 'employment_history', 'education', 'project', 'certifications',

            # Account Status
            'is_active', 'email_verified', 'mobile_verified',
            'is_gp_connected', 'date_joined', 'profile_updated',

            # Email Preferences
            'email_notifications', 'is_unsubscribe',
        ]
        read_only_fields = [
            'id', 'email', 'username', 'user_type', 'date_joined',
            'email_verified', 'mobile_verified', 'profile_updated',
            'is_active'
        ]

    def get_profile_pic_url(self, obj):
        """Get absolute URL for profile picture"""
        if obj.profile_pic:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_pic.url)
            return obj.profile_pic.url
        return obj.photo if obj.photo else None

    def get_resume_url(self, obj):
        """Get absolute URL for resume"""
        if obj.resume:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.resume.url)
            return obj.resume.url
        return None

    def validate_mobile(self, value):
        """Validate mobile number format"""
        if value and not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("Mobile number must contain only digits, spaces, hyphens, or plus sign")
        return value

    def validate(self, data):
        """Cross-field validation"""
        # Ensure experience year/month are valid
        year = data.get('year', self.instance.year if self.instance else None)
        month = data.get('month', self.instance.month if self.instance else None)

        if year:
            try:
                year_int = int(year)
                if year_int < 0 or year_int > 50:
                    raise serializers.ValidationError({
                        'year': 'Experience years must be between 0 and 50'
                    })
            except ValueError:
                raise serializers.ValidationError({
                    'year': 'Experience years must be a valid number'
                })

        if month:
            try:
                month_int = int(month)
                if month_int < 0 or month_int > 11:
                    raise serializers.ValidationError({
                        'month': 'Experience months must be between 0 and 11'
                    })
            except ValueError:
                raise serializers.ValidationError({
                    'month': 'Experience months must be a valid number'
                })

        return data

    def update(self, instance, validated_data):
        """Update user profile with many-to-many relationships"""
        # Handle many-to-many fields separately
        preferred_city = validated_data.pop('preferred_city', None)

        # Update scalar fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Update many-to-many relationships
        if preferred_city is not None:
            instance.preferred_city.set(preferred_city)

        return instance


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for partial profile updates
    Useful for updating specific fields without sending entire profile
    """

    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.filter(status='Enabled'),
        source='city',
        required=False,
        allow_null=True
    )
    current_city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.filter(status='Enabled'),
        source='current_city',
        required=False,
        allow_null=True
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'mobile', 'gender', 'dob',
            'marital_status', 'nationality', 'address', 'permanent_address',
            'pincode', 'city_id', 'current_city_id', 'job_role',
            'profile_description', 'year', 'month', 'current_salary',
            'expected_salary', 'notice_period', 'relocation',
            'is_looking_for_job', 'is_open_to_offers', 'resume_title',
            'email_notifications', 'show_email'
        ]
