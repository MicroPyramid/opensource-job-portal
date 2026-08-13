"""
Tests for the SES bounce webhook.
"""

import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from peeldb.models import JobAlert, Skill, Subscriber, User

BOUNCED = "gone@example.com"
LIVE = "still-here@example.com"


def sns_body(notification_type="Bounce", addresses=(BOUNCED,)):
    """An SNS envelope shaped the way SES actually delivers one."""
    message = {
        "notificationType": notification_type,
        "bounce": {
            "bounceType": "Permanent",
            "bouncedRecipients": [{"emailAddress": a} for a in addresses],
        },
    }
    return {"Type": "Notification", "Message": json.dumps(message)}


class SESBounceWebhookTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("api:v1:webhooks:ses-bounce")
        self.skill = Skill.objects.create(name="Java", slug="java", status="Active")

    def _post(self, payload):
        return self.client.post(
            self.url, json.dumps(payload), content_type="application/json"
        )

    def _seed(self, email):
        user = User.objects.create_user(username=email, email=email, password="x")
        JobAlert.objects.create(email=email, name="Java jobs")
        Subscriber.objects.create(email=email, skill=self.skill)
        return user

    def test_bounce_flags_the_user_and_clears_their_lists(self):
        user = self._seed(BOUNCED)

        response = self._post(sns_body())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_bounce)
        # A dead address that keeps receiving is what wrecks sending reputation.
        self.assertFalse(JobAlert.objects.filter(email=BOUNCED).exists())
        self.assertFalse(Subscriber.objects.filter(email=BOUNCED).exists())

    def test_only_the_bounced_address_is_touched(self):
        bystander = self._seed(LIVE)
        self._seed(BOUNCED)

        self._post(sns_body())

        bystander.refresh_from_db()
        self.assertFalse(bystander.is_bounce)
        self.assertTrue(JobAlert.objects.filter(email=LIVE).exists())
        self.assertTrue(Subscriber.objects.filter(email=LIVE).exists())

    def test_multiple_recipients_in_one_notification(self):
        self._seed(BOUNCED)
        self._seed(LIVE)

        response = self._post(sns_body(addresses=(BOUNCED, LIVE)))

        self.assertEqual(response.data["bounced"], 2)
        self.assertEqual(User.objects.filter(is_bounce=True).count(), 2)

    def test_complaints_are_ignored(self):
        user = self._seed(BOUNCED)

        response = self._post(sns_body(notification_type="Complaint"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertFalse(user.is_bounce)

    def test_subscription_confirmation_is_acknowledged(self):
        # SNS sends this first. A non-200 makes it retry forever.
        response = self._post(
            {"Type": "SubscriptionConfirmation", "SubscribeURL": "https://sns/confirm"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_malformed_body_is_rejected_not_raised(self):
        # The legacy handler indexed into the payload directly, so junk here
        # became a 500 — which SNS treats as retryable and redelivers.
        response = self.client.post(
            self.url, "not json at all", content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_notification_with_unparseable_message_is_rejected(self):
        response = self._post({"Type": "Notification", "Message": "{oops"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_legacy_bounces_path_still_works(self):
        # AWS holds the old URL in a live subscription; changing it silently
        # would stop bounce handling.
        user = self._seed(BOUNCED)

        response = self.client.post(
            "/bounces/", json.dumps(sns_body()), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_bounce)
