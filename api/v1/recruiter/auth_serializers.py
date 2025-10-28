"""
Authentication Serializers for Recruiter/Employer
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from peeldb.models import User, Company, Google, TeamInvitation
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from .serializers import CompanyBasicSerializer, AcceptInvitationSerializer


class RegisterSerializer(serializers.Serializer):
    """
    Registration serializer for new recruiter/company accounts
    """
    # Account Type
    account_type = serializers.ChoiceField(
        choices=['company', 'recruiter'],
        help_text="'company' for company admin, 'recruiter' for independent recruiter"
    )

    # Company Info (required if account_type='company')
    company_name = serializers.CharField(max_length=500, required=False)
    company_website = serializers.URLField(required=False, allow_blank=True)
    company_industry = serializers.CharField(max_length=500, required=False, allow_blank=True)
    company_size = serializers.ChoiceField(
        choices=['1-10', '11-20', '21-50', '50-200', '200+'],
        required=False
    )

    # Personal Info
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    job_title = serializers.CharField(max_length=200, required=False, allow_blank=True)

    # Account Security
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)
    agree_to_terms = serializers.BooleanField()

    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists")
        return value.lower()

    def validate(self, data):
        """Cross-field validation"""
        # Check passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})

        # Validate password strength
        try:
            validate_password(data['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        # If company account, require company fields
        if data['account_type'] == 'company':
            if not data.get('company_name'):
                raise serializers.ValidationError({"company_name": "Company name is required for company accounts"})
            if not data.get('company_website'):
                raise serializers.ValidationError({"company_website": "Company website is required for company accounts"})

        # Require terms acceptance
        if not data.get('agree_to_terms'):
            raise serializers.ValidationError({"agree_to_terms": "You must agree to the terms of service"})

        return data

    def create(self, validated_data):
        """Create user and optionally company"""
        from django.template.defaultfilters import slugify

        account_type = validated_data['account_type']
        email = validated_data['email']

        # Generate username from email
        username = email.split('@')[0] + '_' + get_random_string(6)

        # Create company if account_type is 'company'
        company = None
        if account_type == 'company':
            company_slug = slugify(validated_data['company_name'])
            # Ensure unique slug
            base_slug = company_slug
            counter = 1
            while Company.objects.filter(slug=company_slug).exists():
                company_slug = f"{base_slug}-{counter}"
                counter += 1

            company = Company.objects.create(
                name=validated_data['company_name'],
                website=validated_data.get('company_website', ''),
                size=validated_data.get('company_size', ''),
                company_type='Company',
                slug=company_slug,
                profile='',  # Will be filled during onboarding
                address='',
                phone_number=validated_data.get('phone', ''),
                email=email,
                is_active=True
            )

        # Generate activation code
        activation_code = get_random_string(32)

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            user_type='EM',
            company=company,
            is_admin=True if account_type == 'company' else False,
            job_title=validated_data.get('job_title', ''),
            mobile=validated_data.get('phone', ''),
            is_active=False,  # Requires email verification
            email_verified=False,
            activation_code=activation_code
        )

        return {
            'user': user,
            'company': company,
            'activation_code': activation_code
        }


class LoginSerializer(serializers.Serializer):
    """Login serializer"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(default=False)

    def validate(self, data):
        """Authenticate user"""
        email = data.get('email', '').lower()
        password = data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)

            if user:
                # Check if user is employer type
                if user.user_type != 'EM':
                    raise serializers.ValidationError(
                        "This email is registered as a job seeker. Please use the job seeker login."
                    )

                # Check if email is verified
                if not user.is_active:
                    raise serializers.ValidationError(
                        "Please verify your email address first. Check your inbox for the verification link."
                    )

                data['user'] = user
            else:
                raise serializers.ValidationError("Invalid email or password")
        else:
            raise serializers.ValidationError("Must provide email and password")

        return data


class VerifyEmailSerializer(serializers.Serializer):
    """Email verification serializer"""
    token = serializers.CharField(max_length=100)

    def validate_token(self, value):
        """Validate verification token"""
        try:
            user = User.objects.get(
                activation_code=value,
                user_type='EM',
                is_active=False
            )
            self.context['user'] = user
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired verification link")


class ResendVerificationSerializer(serializers.Serializer):
    """Resend verification email"""
    email = serializers.EmailField()

    def validate_email(self, value):
        """Check if user exists and needs verification"""
        try:
            user = User.objects.get(
                email=value.lower(),
                user_type='EM',
                is_active=False
            )
            self.context['user'] = user
            return value.lower()
        except User.DoesNotExist:
            # Don't reveal if email exists (security)
            return value.lower()


class ForgotPasswordSerializer(serializers.Serializer):
    """Request password reset"""
    email = serializers.EmailField()

    def validate_email(self, value):
        """Find user (don't reveal if exists)"""
        try:
            user = User.objects.get(email=value.lower(), user_type='EM')
            self.context['user'] = user
        except User.DoesNotExist:
            pass  # Don't reveal if user exists
        return value.lower()


class ResetPasswordSerializer(serializers.Serializer):
    """Reset password with token"""
    token = serializers.CharField(max_length=100)
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate_token(self, value):
        """Validate reset token"""
        # TODO: Implement proper password reset token model
        # For now, using activation_code field (should create separate PasswordReset model)
        try:
            user = User.objects.get(
                activation_code=value,
                user_type='EM'
            )
            self.context['user'] = user
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired reset link")

    def validate(self, data):
        """Validate passwords match"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})

        try:
            validate_password(data['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Change password for authenticated user"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate_old_password(self, value):
        """Check old password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value

    def validate(self, data):
        """Validate new passwords match"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})

        try:
            validate_password(data['new_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return data


class GoogleAuthUrlSerializer(serializers.Serializer):
    """Get Google OAuth URL"""
    redirect_uri = serializers.URLField()
    account_type = serializers.ChoiceField(choices=['company', 'recruiter'])


class GoogleCallbackSerializer(serializers.Serializer):
    """Handle Google OAuth callback"""
    code = serializers.CharField()
    account_type = serializers.ChoiceField(choices=['company', 'recruiter'])
    redirect_uri = serializers.URLField()


class GoogleCompleteSerializer(serializers.Serializer):
    """Complete Google OAuth registration"""
    session_token = serializers.CharField(max_length=100)
    account_type = serializers.ChoiceField(choices=['company', 'recruiter'])

    # Company fields (required if account_type='company')
    company_name = serializers.CharField(max_length=500, required=False)
    company_website = serializers.URLField(required=False)
    company_industry = serializers.CharField(max_length=500, required=False)
    company_size = serializers.ChoiceField(
        choices=['1-10', '11-20', '21-50', '50-200', '200+'],
        required=False
    )

    phone = serializers.CharField(max_length=20, required=False)
    job_title = serializers.CharField(max_length=200, required=False)
    agree_to_terms = serializers.BooleanField()

    def validate(self, data):
        """Validate company fields if account_type='company'"""
        if data['account_type'] == 'company':
            if not data.get('company_name'):
                raise serializers.ValidationError({"company_name": "Company name is required"})
            if not data.get('company_website'):
                raise serializers.ValidationError({"company_website": "Company website is required"})

        if not data.get('agree_to_terms'):
            raise serializers.ValidationError({"agree_to_terms": "You must agree to the terms"})

        return data


class UserSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    company = CompanyBasicSerializer(read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'username',
            'user_type', 'is_active', 'email_verified', 'company',
            'is_admin', 'job_title', 'mobile', 'profile_pic',
            'date_joined', 'last_login', 'permissions'
        ]

    def get_permissions(self, obj):
        """Get user permissions"""
        return {
            'can_post_jobs': obj.user_type == 'EM',
            'can_manage_team': obj.is_company_admin,
            'can_edit_company': obj.is_company_admin,
            'is_company_admin': obj.is_company_admin,
            'is_company_member': obj.is_company_member,
            'is_independent_recruiter': obj.is_independent_recruiter
        }


class UpdateProfileSerializer(serializers.Serializer):
    """Update recruiter profile"""
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    job_title = serializers.CharField(max_length=200, required=False, allow_blank=True)
    mobile = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_mobile(self, value):
        """Validate mobile number format"""
        if value and not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("Please enter a valid phone number")
        return value

    def update(self, instance, validated_data):
        """Update user profile"""
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
