"""
Job Alert Serializers for API v1

`JobAlert` has **no user foreign key** — it is keyed on an email address, so
alerts are an anonymous subscription rather than a profile feature. That is why
this replaces six authenticated `candidate/` routes with one public form plus a
verification callback.
"""

from django.utils.crypto import get_random_string
from rest_framework import serializers

from peeldb.models import City, Industry, JobAlert, Skill, User


class JobAlertSubscribeSerializer(serializers.Serializer):
    """Create a job alert for an email address."""

    email = serializers.EmailField()
    name = serializers.CharField(max_length=2000)
    skills = serializers.SlugRelatedField(
        many=True,
        slug_field="slug",
        queryset=Skill.objects.filter(status="Active"),
        required=False,
    )
    locations = serializers.SlugRelatedField(
        many=True,
        slug_field="slug",
        queryset=City.objects.filter(status="Enabled"),
        required=False,
    )
    industries = serializers.SlugRelatedField(
        many=True, slug_field="slug", queryset=Industry.objects.all(), required=False
    )
    min_year = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    max_year = serializers.IntegerField(required=False, allow_null=True, min_value=0)

    def validate_email(self, value):
        email = value.lower().strip()

        # The legacy subscribe view refused recruiter and staff accounts; an
        # alert digest of job posts is meaningless to the person posting them.
        user = User.objects.filter(email__iexact=email).first()
        if user and user.user_type != "JS":
            raise serializers.ValidationError(
                "This address belongs to an employer account."
            )

        return email

    def validate(self, data):
        if not any(data.get(field) for field in ("skills", "locations", "industries")):
            raise serializers.ValidationError(
                "Choose at least one skill, location or industry to be alerted about."
            )

        min_year, max_year = data.get("min_year"), data.get("max_year")
        if min_year is not None and max_year is not None and min_year > max_year:
            raise serializers.ValidationError(
                {"max_year": "Maximum experience cannot be less than the minimum."}
            )

        return data

    def create(self, validated_data):
        skills = validated_data.pop("skills", [])
        locations = validated_data.pop("locations", [])
        industries = validated_data.pop("industries", [])

        alert = JobAlert.objects.create(
            email=validated_data["email"],
            name=validated_data["name"],
            min_year=validated_data.get("min_year"),
            max_year=validated_data.get("max_year"),
            subscribe_code=get_random_string(32),
            unsubscribe_code=get_random_string(32),
        )
        alert.skill.set(skills)
        alert.location.set(locations)
        alert.industry.set(industries)
        return alert


class JobAlertSerializer(serializers.ModelSerializer):
    """What a caller gets back about an alert. No codes — those are secrets."""

    skills = serializers.SlugRelatedField(
        source="skill", many=True, slug_field="name", read_only=True
    )
    locations = serializers.SlugRelatedField(
        source="location", many=True, slug_field="name", read_only=True
    )
    industries = serializers.SlugRelatedField(
        source="industry", many=True, slug_field="name", read_only=True
    )

    class Meta:
        model = JobAlert
        fields = [
            "id",
            "email",
            "name",
            "skills",
            "locations",
            "industries",
            "min_year",
            "max_year",
            "is_verified",
            "is_unsubscribe",
        ]
        read_only_fields = fields


class VerifyAlertSerializer(serializers.Serializer):
    """Redeem the confirmation code mailed to the subscriber."""

    code = serializers.CharField(allow_blank=False)


class UnsubscribeSerializer(serializers.Serializer):
    """
    Stop email for one of the three things that can be unsubscribed.

    `type` mirrors the `email_type` segment of the legacy
    `/unsubscribe_email/<email_type>/<message_id>/` links, which are live in
    mail already sent — so the values have to stay as they are.
    """

    TYPE_CHOICES = ("alert", "subscriber", "user")

    type = serializers.ChoiceField(choices=TYPE_CHOICES)
    code = serializers.CharField(allow_blank=False)
    reason = serializers.CharField(required=False, allow_blank=True, default="")
