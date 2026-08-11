"""
Serializers for Recruiter/Employer API endpoints
"""

import contextlib
from datetime import timedelta

from django.utils import timezone
from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer
from rest_framework import serializers

from peeldb.models import Company, TeamInvitation, User


class CompanyBasicSerializer(serializers.ModelSerializer):
    """Basic company information"""

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "slug",
            "profile_pic",
            "website",
            "company_type",
            "size",
        ]


class TeamMemberStatsSerializer(serializers.Serializer):
    """Statistics for team member"""

    jobs_posted = serializers.IntegerField()
    active_jobs = serializers.IntegerField()
    total_applicants = serializers.IntegerField()


class TeamMemberRecentJobSerializer(serializers.Serializer):
    """One entry of ``TeamMemberDetailSerializer.get_recent_jobs`` (5 most recent)."""

    id = serializers.IntegerField()
    title = serializers.CharField()
    status = serializers.CharField()
    posted_date = serializers.DateField()
    applicants_count = serializers.IntegerField()


class TeamMemberSerializer(serializers.ModelSerializer):
    """Team member details"""

    stats = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "job_title",
            "is_admin",
            "date_joined",
            "last_login",
            "profile_pic",
            "stats",
        ]

    @extend_schema_field(TeamMemberStatsSerializer)
    def get_stats(self, obj):
        """Calculate team member statistics"""
        from peeldb.models import JobPost

        jobs = JobPost.objects.filter(user=obj)
        active_jobs = jobs.filter(status="Live")

        total_applicants = 0
        for job in jobs:
            # Get applicant count from AppliedJobs
            total_applicants += job.appliedjobs_set.count()

        return {
            "jobs_posted": jobs.count(),
            "active_jobs": active_jobs.count(),
            "total_applicants": total_applicants,
        }


class TeamMemberDetailSerializer(TeamMemberSerializer):
    """Detailed team member information with recent jobs"""

    recent_jobs = serializers.SerializerMethodField()

    class Meta(TeamMemberSerializer.Meta):
        fields = TeamMemberSerializer.Meta.fields + ["recent_jobs"]

    @extend_schema_field(TeamMemberRecentJobSerializer(many=True))
    def get_recent_jobs(self, obj):
        """Get recent jobs posted by this member"""
        from peeldb.models import JobPost

        jobs = JobPost.objects.filter(user=obj).order_by("-created_on")[:5]
        return [
            {
                "id": job.id,
                "title": job.title,
                "status": job.status,
                "posted_date": job.created_on,
                "applicants_count": job.appliedjobs_set.count(),
            }
            for job in jobs
        ]


class TeamInvitationSerializer(serializers.ModelSerializer):
    """Team invitation details"""

    invited_by_name = serializers.SerializerMethodField()
    invited_by_email = serializers.CharField(source="invited_by.email", read_only=True)
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = TeamInvitation
        fields = [
            "id",
            "email",
            "role_title",
            "status",
            "invited_by_name",
            "invited_by_email",
            "created_at",
            "expires_at",
            "days_remaining",
        ]

    def get_invited_by_name(self, obj) -> str:
        return f"{obj.invited_by.first_name} {obj.invited_by.last_name}".strip()

    def get_days_remaining(self, obj) -> int:
        """Calculate days until expiration"""
        if obj.status != "pending":
            return 0
        delta = obj.expires_at - timezone.now()
        return max(0, delta.days)


class SendInvitationSerializer(serializers.Serializer):
    """Serializer for sending team invitation"""

    email = serializers.EmailField()
    job_title = serializers.CharField(max_length=200, required=False, allow_blank=True)
    message = serializers.CharField(max_length=1000, required=False, allow_blank=True)

    def validate_email(self, value):
        """Check if email already exists or has pending invitation"""
        # Check if user already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists")

        # Check if pending invitation exists
        company = self.context.get("company")
        if company:
            existing = TeamInvitation.objects.filter(
                company=company, email=value, status="pending"
            ).first()
            if existing and not existing.is_expired():
                raise serializers.ValidationError(
                    "An invitation has already been sent to this email"
                )

        return value

    def create(self, validated_data):
        """Create team invitation"""
        company = self.context["company"]
        invited_by = self.context["user"]

        # Generate unique token
        token = get_random_string(64)

        # Create invitation
        invitation = TeamInvitation.objects.create(
            company=company,
            invited_by=invited_by,
            email=validated_data["email"],
            token=token,
            role_title=validated_data.get("job_title", ""),
            expires_at=timezone.now() + timedelta(days=7),
        )

        # TODO: Send invitation email

        return invitation


class UpdateTeamMemberSerializer(serializers.Serializer):
    """Serializer for updating team member"""

    job_title = serializers.CharField(max_length=200, required=False, allow_blank=True)
    is_admin = serializers.BooleanField(required=False)

    def validate_is_admin(self, value):
        """Prevent demoting last admin"""
        if value is False:
            user = self.context.get("user_to_update")
            company = self.context.get("company")

            if user and company and user.is_admin:
                # Check if this is the last admin
                admin_count = User.objects.filter(
                    company=company, is_admin=True, user_type="EM"
                ).count()

                if admin_count <= 1:
                    raise serializers.ValidationError(
                        "Cannot demote the last admin. Promote another member first."
                    )

        return value


class AcceptInvitationSerializer(serializers.Serializer):
    """Serializer for accepting team invitation during signup"""

    token = serializers.CharField(max_length=100)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate_token(self, value):
        """Validate invitation token"""
        try:
            invitation = TeamInvitation.objects.get(token=value, status="pending")
            if invitation.is_expired():
                raise serializers.ValidationError("This invitation has expired")
            self.context["invitation"] = invitation
            return value
        except TeamInvitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation token")

    def validate(self, data):
        """Validate passwords match"""
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )
        return data

    def create(self, validated_data):
        """Create user from invitation"""
        invitation = self.context["invitation"]

        # Create user
        user = User.objects.create_user(
            username=invitation.email,
            email=invitation.email,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
            user_type="EM",
            company=invitation.company,
            is_admin=False,
            job_title=invitation.role_title,
            email_verified=True,  # Pre-verified since invited by admin
            is_active=True,
        )

        # Accept invitation
        invitation.accept(user)

        return user


@extend_schema_serializer(component_name="RecruiterCompanyDetail")
class CompanyDetailSerializer(serializers.ModelSerializer):
    """Detailed company information for recruiters"""

    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "slug",
            "website",
            "address",
            "profile",
            "phone_number",
            "email",
            "size",
            "company_type",
            "profile_pic",
            "logo_url",
            "registered_date",
        ]
        read_only_fields = ["id", "slug", "registered_date"]

    def get_logo_url(self, obj) -> str:
        """Get company logo URL"""
        if obj.profile_pic:
            request = self.context.get("request")
            if request:
                with contextlib.suppress(Exception):
                    return request.build_absolute_uri(obj.profile_pic.url)
        return "https://cdn.peeljobs.com/static/company_logo.png"


class CompanyUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating company profile"""

    class Meta:
        model = Company
        fields = [
            "name",
            "website",
            "address",
            "profile",
            "phone_number",
            "email",
            "size",
            "profile_pic",
        ]

    def validate_name(self, value):
        """Validate company name"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Company name must be at least 2 characters"
            )
        return value.strip()

    def validate_website(self, value):
        """Validate website URL"""
        if value:
            value = value.strip()
            if not value.startswith(("http://", "https://")):
                value = "https://" + value
        return value

    def validate_email(self, value):
        """Validate email format"""
        if value:
            value = value.strip().lower()
        return value


# --- Response serializers ---------------------------------------------------
#
# Envelopes returned by api/v1/recruiter/views.py. Documentation only — DRF does
# not validate outgoing responses against these.


class TeamMemberListResponseSerializer(serializers.Serializer):
    """200 response from ``list_team_members``."""

    company = CompanyBasicSerializer()
    members = TeamMemberSerializer(many=True)
    total_members = serializers.IntegerField()


class TeamInvitationMutationResponseSerializer(serializers.Serializer):
    """Shared shape for ``invite_team_member`` and ``resend_invitation``."""

    success = serializers.BooleanField()
    invitation = TeamInvitationSerializer()
    message = serializers.CharField()


class TeamInvitationListResponseSerializer(serializers.Serializer):
    """200 response from ``list_invitations``, with counts by state."""

    invitations = TeamInvitationSerializer(many=True)
    total = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    expired_count = serializers.IntegerField()


class TeamMemberUpdateResponseSerializer(serializers.Serializer):
    """200 response from ``update_team_member``."""

    success = serializers.BooleanField()
    user = TeamMemberSerializer()
    message = serializers.CharField()


class CompanyProfileUpdateResponseSerializer(serializers.Serializer):
    """200 response from ``update_company_profile``.

    Note the key order differs from the team endpoints: message precedes the
    payload here. Only the shape matters to clients, but it is mirrored as-is.
    """

    success = serializers.BooleanField()
    message = serializers.CharField()
    company = CompanyDetailSerializer()
