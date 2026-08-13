"""
Job Alerts and email unsubscribe for API v1

Replaces the six `candidate/alert/*` routes plus the inbound unsubscribe
handlers in `candidate/` and `pjob/`.

**These endpoints are load-bearing on a live system.** `CELERY_BEAT_SCHEDULE`
runs `dashboard.tasks.applicants_job_notifications` every Monday at 09:00, and
the templates it renders link to the unsubscribe handlers. Mail is going out to
a list of 64,673 alerts and 60,805 subscribers, and 2,785 users have already
used unsubscribe — so a working unsubscribe path is an obligation, not a
feature.
"""

from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from peeldb.models import JobAlert, Subscriber, User

from ..common.responses import VALIDATION_ERROR_RESPONSE, MessageResponseSerializer
from .serializers import (
    JobAlertSerializer,
    JobAlertSubscribeSerializer,
    UnsubscribeSerializer,
    VerifyAlertSerializer,
)


def send_alert_verification(alert):
    """Mail the confirm link for a newly created alert."""
    from datetime import datetime

    from django.conf import settings
    from django.template import loader

    from dashboard.tasks import send_email

    frontend_url = settings.SITE_FRONTEND_URL.rstrip("/")
    verification_url = f"{frontend_url}/job-alerts/verify/?code={alert.subscribe_code}"

    template = loader.get_template("jobseeker/email/verification.html")
    html_content = template.render(
        {
            "user": alert,
            "verification_url": verification_url,
            "current_year": datetime.now().year,
        }
    )

    send_email.delay(
        mto=[alert.email],
        msubject="Confirm your PeelJobs job alert",
        mbody=html_content,
    )


@extend_schema(
    tags=["Job Alerts"],
    summary="Subscribe to a job alert",
    description=(
        "Create an email job alert. The alert is inactive until the "
        "confirmation link is redeemed at `verify/` — the weekly digest only "
        "goes to verified alerts."
    ),
    request=JobAlertSubscribeSerializer,
    responses={201: JobAlertSerializer, 400: VALIDATION_ERROR_RESPONSE},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def subscribe(request):
    """Create a job alert for an email address."""
    serializer = JobAlertSubscribeSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    alert = serializer.save()

    try:
        send_alert_verification(alert)
    except Exception as exc:
        # Do not lose the alert because mail is down; it can be re-confirmed.
        print(f"Failed to send alert verification: {exc}")

    return Response(JobAlertSerializer(alert).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Job Alerts"],
    summary="Confirm a job alert",
    request=VerifyAlertSerializer,
    responses={200: JobAlertSerializer, 400: VALIDATION_ERROR_RESPONSE},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def verify(request):
    """Redeem the confirmation code mailed to a subscriber."""
    serializer = VerifyAlertSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    alert = JobAlert.objects.filter(
        subscribe_code=serializer.validated_data["code"]
    ).first()

    if not alert:
        return Response(
            {"error": "This link is invalid or has already been used."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    alert.is_verified = True
    alert.is_unsubscribe = False
    # Burn the code so the link is single-use, but keep `unsubscribe_code` —
    # every digest email links to it.
    alert.subscribe_code = ""
    if not alert.unsubscribe_code:
        alert.unsubscribe_code = get_random_string(32)
    alert.save(
        update_fields=[
            "is_verified",
            "is_unsubscribe",
            "subscribe_code",
            "unsubscribe_code",
        ]
    )

    return Response(JobAlertSerializer(alert).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Job Alerts"],
    summary="Unsubscribe from email",
    description=(
        "Stop email for a job alert, a skill subscription or an account. "
        "`type` mirrors the `email_type` segment of the "
        "`/unsubscribe_email/<email_type>/<message_id>/` links already sitting "
        "in delivered mail."
    ),
    request=UnsubscribeSerializer,
    responses={200: MessageResponseSerializer, 400: VALIDATION_ERROR_RESPONSE},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def unsubscribe(request):
    """Honour an unsubscribe link from a sent email."""
    serializer = UnsubscribeSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    code = serializer.validated_data["code"]
    model = {
        "alert": JobAlert,
        "subscriber": Subscriber,
        "user": User,
    }[serializer.validated_data["type"]]

    target = model.objects.filter(unsubscribe_code__iexact=code).first()

    if not target:
        # Deliberately a success: an already-redeemed code means the person is
        # unsubscribed, which is what they asked for. Returning an error would
        # push someone who clicked twice into thinking it had not worked.
        return Response(
            {"message": "You are unsubscribed. You will not receive these emails."},
            status=status.HTTP_200_OK,
        )

    target.is_unsubscribe = True
    target.unsubscribe_reason = serializer.validated_data.get("reason", "")
    # Single-use: the code identifies the recipient, so it must not stay live
    # in an inbox forever.
    target.unsubscribe_code = ""
    target.save(
        update_fields=["is_unsubscribe", "unsubscribe_reason", "unsubscribe_code"]
    )

    return Response(
        {"message": "You are unsubscribed. You will not receive these emails."},
        status=status.HTTP_200_OK,
    )
