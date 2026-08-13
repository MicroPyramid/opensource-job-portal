"""
Recruiter Serializers for API v1

Backs the public recruiter directory. Everything here is crawler-visible, so
the field lists are deliberately narrow: no email, no mobile, no internal
flags. The legacy templates rendered the same public subset.
"""

from rest_framework import serializers

from peeldb.models import User


class RecruiterListSerializer(serializers.ModelSerializer):
    """One row in the /recruiters/ directory."""

    name = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    company_slug = serializers.SerializerMethodField()
    company_logo = serializers.SerializerMethodField()
    job_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "name",
            "profile_pic",
            "company_name",
            "company_slug",
            "company_logo",
            "job_count",
        ]
        read_only_fields = fields

    def get_name(self, obj):
        full_name = f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        # Fall back to the username rather than rendering an empty heading;
        # `username` mirrors the email for most accounts, so strip the domain.
        return full_name or (obj.username or "").split("@")[0]

    def get_company_name(self, obj):
        return obj.company.name if obj.company else ""

    def get_company_slug(self, obj):
        return obj.company.slug if obj.company else ""

    def get_profile_pic(self, obj):
        # FileField.url raises when the field is empty, and most recruiter rows
        # have no picture.
        return str(obj.profile_pic) if obj.profile_pic else ""

    def get_company_logo(self, obj):
        # Company.get_logo_url() already falls back to the CDN placeholder.
        return obj.company.get_logo_url() if obj.company else ""


class RecruiterDetailSerializer(RecruiterListSerializer):
    """A single recruiter's public profile."""

    class Meta(RecruiterListSerializer.Meta):
        fields = RecruiterListSerializer.Meta.fields + [
            "job_title",
            "profile_description",
        ]
        read_only_fields = fields
