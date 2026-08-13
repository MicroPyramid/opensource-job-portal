"""
Inbound webhooks from the mail provider.

This is the SES bounce handler that used to live at `candidate.views.bounces`,
moved here when `candidate/` was deleted. AWS SNS posts here, so the legacy
`/bounces/` path is kept alongside the versioned one — an SNS subscription
created against the old URL keeps working.

SECURITY, UNRESOLVED: SNS message signatures are not verified, so this endpoint
takes an unauthenticated caller's word for which address bounced, and acting on
that deletes rows. That was true of the legacy handler too and is carried over
rather than quietly changed. Closing it means either adding `cryptography` and
validating `SigningCertURL`/`Signature`, or moving the endpoint behind a secret
path that only the SNS subscription knows.
"""

import json

from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from peeldb.models import JobAlert, Subscriber, User


def _load_sns_envelope(body):
    """
    Parse the SNS envelope and its embedded message.

    Returns `None` for anything unparseable. The legacy handler indexed
    `js["Type"]` directly, so a malformed body raised and SNS saw a 500 — which
    it treats as retryable and redelivers.
    """
    try:
        envelope = json.loads(body.decode("utf8").replace("\n", ""))
    except (UnicodeDecodeError, ValueError):
        return None

    if not isinstance(envelope, dict):
        return None
    return envelope


@extend_schema(exclude=True)
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def ses_bounce(request):
    """
    Record hard bounces reported by SES.

    A bounced address is dead weight that damages sending reputation, so the
    user is flagged and every list they are on is cleared.
    """
    envelope = _load_sns_envelope(request.body)
    if envelope is None:
        return Response(
            {"error": "Body is not valid SNS JSON"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # SNS confirms a new subscription before it delivers anything. Answering 200
    # keeps it from retrying; confirming the subscription itself is a manual
    # step, deliberately — fetching `SubscribeURL` on an unauthenticated POST
    # would let anyone make this server issue a request of their choosing.
    if envelope.get("Type") != "Notification":
        return Response({"status": "ignored"}, status=status.HTTP_200_OK)

    try:
        message = json.loads((envelope.get("Message") or "").replace("\n", ""))
    except ValueError:
        return Response(
            {"error": "Message is not valid JSON"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not isinstance(message, dict) or message.get("notificationType") != "Bounce":
        return Response({"status": "ignored"}, status=status.HTTP_200_OK)

    recipients = message.get("bounce", {}).get("bouncedRecipients") or []
    addresses = [r.get("emailAddress") for r in recipients if r.get("emailAddress")]

    if addresses:
        User.objects.filter(email__in=addresses).update(is_bounce=True)
        JobAlert.objects.filter(email__in=addresses).delete()
        Subscriber.objects.filter(email__in=addresses).delete()

    return Response({"status": "ok", "bounced": len(addresses)})
