"""
Tests for job alerts and email unsubscribe.
"""

from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from peeldb.models import City, Country, JobAlert, Skill, State, Subscriber, User


class JobAlertAPITests(TestCase):
    """
    Subscribing to and confirming an email job alert.

    `JobAlert` has no user foreign key, so these are deliberately public
    endpoints — the legacy feature was an anonymous email subscription.
    """

    def setUp(self):
        self.client = APIClient()
        self.subscribe_url = reverse("api:v1:alerts:subscribe")
        self.verify_url = reverse("api:v1:alerts:verify")

        self.skill = Skill.objects.create(name="Java", slug="java", status="Active")
        country = Country.objects.create(name="India", slug="india")
        state = State.objects.create(
            name="Telangana", slug="telangana", country=country
        )
        self.city = City.objects.create(
            name="Hyderabad", slug="hyderabad", state=state, status="Enabled"
        )

    def _subscribe(self, **overrides):
        payload = {
            "email": "seeker@example.com",
            "name": "Java jobs",
            "skills": ["java"],
        }
        payload.update(overrides)
        with patch("api.v1.alerts.views.send_alert_verification"):
            return self.client.post(self.subscribe_url, payload, format="json")

    def test_subscribe_creates_an_unverified_alert(self):
        response = self._subscribe()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        alert = JobAlert.objects.get(id=response.data["id"])
        # The weekly digest filters on is_verified, so a fresh alert must not
        # start switched on.
        self.assertFalse(alert.is_verified)
        self.assertTrue(alert.subscribe_code)

    def test_no_facets_rejected(self):
        response = self._subscribe(skills=[], locations=[], industries=[])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inverted_experience_range_rejected(self):
        response = self._subscribe(min_year=5, max_year=2)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_skill_rejected(self):
        response = self._subscribe(skills=["nosuchskill"])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_employer_address_rejected(self):
        employer = User.objects.create_user(
            username="boss@example.com", email="boss@example.com", password="x"
        )
        employer.user_type = "EM"
        employer.save()

        response = self._subscribe(email="boss@example.com")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_name_allowed(self):
        # `JobAlert.name` used to be unique=True, which meant the second person
        # to name an alert "Java jobs" got an IntegrityError.
        self._subscribe()

        response = self._subscribe(email="other@example.com")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(JobAlert.objects.filter(name="Java jobs").count(), 2)

    def test_verify_activates_and_burns_the_code(self):
        alert = JobAlert.objects.get(id=self._subscribe().data["id"])

        response = self.client.post(
            self.verify_url, {"code": alert.subscribe_code}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        alert.refresh_from_db()
        self.assertTrue(alert.is_verified)
        self.assertEqual(alert.subscribe_code, "")
        # Every digest email links to this, so it has to survive.
        self.assertTrue(alert.unsubscribe_code)

    def test_verify_cannot_be_replayed(self):
        alert = JobAlert.objects.get(id=self._subscribe().data["id"])
        code = alert.subscribe_code
        self.client.post(self.verify_url, {"code": code}, format="json")

        response = self.client.post(self.verify_url, {"code": code}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_response_never_leaks_the_codes(self):
        response = self._subscribe()

        self.assertNotIn("subscribe_code", response.data)
        self.assertNotIn("unsubscribe_code", response.data)


class UnsubscribeAPITests(TestCase):
    """
    Honouring unsubscribe links from mail already sent.

    A weekly Celery beat job mails a list of 64,673 alerts and 60,805
    subscribers, and 2,785 users have used unsubscribe — this path is an
    obligation, not a feature.
    """

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("api:v1:alerts:unsubscribe")

    def _post(self, **payload):
        return self.client.post(self.url, payload, format="json")

    def test_unsubscribes_a_user(self):
        user = User.objects.create_user(
            username="seeker@example.com", email="seeker@example.com", password="x"
        )
        user.unsubscribe_code = "CODE123"
        user.save()

        response = self._post(type="user", code="CODE123", reason="Too many emails")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_unsubscribe)
        self.assertEqual(user.unsubscribe_reason, "Too many emails")
        # Single-use: the code identifies the recipient and must not stay live
        # in an inbox.
        self.assertEqual(user.unsubscribe_code, "")

    def test_code_is_matched_case_insensitively(self):
        # The legacy handler used `unsubscribe_code__iexact`, so links already
        # delivered may carry any casing.
        user = User.objects.create_user(
            username="seeker@example.com", email="seeker@example.com", password="x"
        )
        user.unsubscribe_code = "CODE123"
        user.save()

        response = self._post(type="user", code="code123")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_unsubscribe)

    def test_unsubscribes_an_alert(self):
        alert = JobAlert.objects.create(
            email="seeker@example.com", name="Java", unsubscribe_code="ALERTCODE"
        )

        response = self._post(type="alert", code="ALERTCODE")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        alert.refresh_from_db()
        self.assertTrue(alert.is_unsubscribe)

    def test_unsubscribes_a_subscriber(self):
        skill = Skill.objects.create(name="Java", slug="java", status="Active")
        subscriber = Subscriber.objects.create(
            email="seeker@example.com", skill=skill, unsubscribe_code="SUBCODE"
        )

        response = self._post(type="subscriber", code="SUBCODE")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subscriber.refresh_from_db()
        self.assertTrue(subscriber.is_unsubscribe)

    def test_second_click_still_succeeds(self):
        user = User.objects.create_user(
            username="seeker@example.com", email="seeker@example.com", password="x"
        )
        user.unsubscribe_code = "CODE123"
        user.save()
        self._post(type="user", code="CODE123")

        response = self._post(type="user", code="CODE123")

        # An already-redeemed code means the person *is* unsubscribed. Erroring
        # would tell someone who clicked twice that it had not worked.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unknown_type_rejected(self):
        response = self._post(type="everything", code="CODE123")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
