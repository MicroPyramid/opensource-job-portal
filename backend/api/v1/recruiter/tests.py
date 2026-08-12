"""
Tests for the gaps closed when finishing the Django → SvelteKit/DRF migration.

Covers the three behaviours that were shipped in the UI but not wired to the
API: the job email-notification toggle, team member activate/deactivate, and
job view counting.
"""

from django.apps import apps
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from peeldb.models import AppliedJobs, Company, JobPost, User


class NoSearchIndexMixin:
    """
    Detach Haystack's realtime signal processor for the duration of the test.

    Saving a JobPost otherwise tries to index it against Elasticsearch, which
    is not running (and is not something these tests need).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._signal_processor = apps.get_app_config("haystack").signal_processor
        cls._signal_processor.teardown()

    @classmethod
    def tearDownClass(cls):
        cls._signal_processor.setup()
        super().tearDownClass()


def make_recruiter(email, company=None, is_admin=False, is_active=True):
    return User.objects.create(
        username=email.split("@")[0],
        email=email,
        first_name=email.split("@")[0].title(),
        last_name="Tester",
        user_type="EM",
        company=company,
        is_admin=is_admin,
        is_active=is_active,
    )


class JobEmailNotificationTests(NoSearchIndexMixin, TestCase):
    """send_email_notifications must survive a round trip through the API."""

    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="Acme", slug="acme")
        self.recruiter = make_recruiter("owner@acme.test", self.company, is_admin=True)
        self.job = JobPost.objects.create(
            user=self.recruiter,
            title="Backend Engineer",
            slug="/backend-engineer/",
            status="Live",
            vacancies=1,
            send_email_notifications=False,
        )
        self.client.force_authenticate(user=self.recruiter)

    def test_detail_exposes_the_field(self):
        url = reverse("api:v1:recruiter:jobs-detail", args=[self.job.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("send_email_notifications", response.data)
        self.assertFalse(response.data["send_email_notifications"])

    def test_toggle_persists_on_a_live_job(self):
        """
        The toggle has to work while the job is Live — that is the only state
        where applicant notifications exist. jobs/<id>/update/ refuses Live
        jobs, which is why this has its own endpoint.
        """
        url = reverse("api:v1:recruiter:jobs-notifications", args=[self.job.id])

        response = self.client.patch(
            url, {"send_email_notifications": True}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertTrue(self.job.send_email_notifications)
        self.assertTrue(response.data["job"]["send_email_notifications"])

    def test_toggle_can_turn_notifications_back_off(self):
        self.job.send_email_notifications = True
        self.job.save(update_fields=["send_email_notifications"])
        url = reverse("api:v1:recruiter:jobs-notifications", args=[self.job.id])

        response = self.client.patch(
            url, {"send_email_notifications": False}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertFalse(self.job.send_email_notifications)

    def test_toggle_rejects_a_missing_value(self):
        url = reverse("api:v1:recruiter:jobs-notifications", args=[self.job.id])

        response = self.client.patch(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_another_recruiters_job_is_not_found(self):
        other = make_recruiter("other@acme.test", self.company)
        self.client.force_authenticate(user=other)
        url = reverse("api:v1:recruiter:jobs-notifications", args=[self.job.id])

        response = self.client.patch(
            url, {"send_email_notifications": True}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TeamMemberStatusToggleTests(NoSearchIndexMixin, TestCase):
    """POST team/<id>/toggle-status/ flips is_active, with the usual guards."""

    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="Acme", slug="acme")
        self.admin = make_recruiter("admin@acme.test", self.company, is_admin=True)
        self.second_admin = make_recruiter(
            "admin2@acme.test", self.company, is_admin=True
        )
        self.member = make_recruiter("member@acme.test", self.company)
        self.client.force_authenticate(user=self.admin)

    def url_for(self, user):
        return reverse("api:v1:recruiter:team-toggle-status", args=[user.id])

    def test_toggle_deactivates_then_reactivates(self):
        response = self.client.post(self.url_for(self.member))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_active)

        response = self.client.post(self.url_for(self.member))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.member.refresh_from_db()
        self.assertTrue(self.member.is_active)

    def test_response_reports_the_new_state(self):
        response = self.client.post(self.url_for(self.member))

        self.assertFalse(response.data["user"]["is_active"])
        self.assertIn("deactivated", response.data["message"])

    def test_team_list_exposes_is_active(self):
        self.member.is_active = False
        self.member.save(update_fields=["is_active"])

        response = self.client.get(reverse("api:v1:recruiter:team-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        members = {m["email"]: m for m in response.data["members"]}
        self.assertFalse(members["member@acme.test"]["is_active"])

    def test_cannot_toggle_self(self):
        response = self.client.post(self.url_for(self.admin))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_an_admin_can_deactivate_another_admin(self):
        """
        The caller cannot deactivate itself, so one active admin always
        survives — there is no separate last-admin guard to trip.
        """
        response = self.client.post(self.url_for(self.second_admin))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.second_admin.refresh_from_db()
        self.assertFalse(self.second_admin.is_active)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_non_admin_is_refused(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.post(self.url_for(self.second_admin))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_of_another_company_is_not_found(self):
        other_company = Company.objects.create(name="Globex", slug="globex")
        outsider = make_recruiter("outsider@globex.test", other_company)

        response = self.client.post(self.url_for(outsider))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class JobViewCountTests(NoSearchIndexMixin, TestCase):
    """The public job-detail endpoint counts views, excluding the job's owner."""

    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="Acme", slug="acme")
        self.owner = make_recruiter("owner@acme.test", self.company, is_admin=True)
        self.job = JobPost.objects.create(
            user=self.owner,
            title="Backend Engineer",
            slug="/backend-engineer/",
            status="Live",
            vacancies=1,
        )
        self.public_url = reverse("api:v1:jobs:job-detail", args=[self.job.id])

    def test_anonymous_views_are_counted(self):
        for _ in range(3):
            self.client.get(self.public_url)

        self.job.refresh_from_db()
        self.assertEqual(self.job.views_count, 3)

    def test_owner_views_are_not_counted(self):
        self.client.force_authenticate(user=self.owner)

        self.client.get(self.public_url)

        self.job.refresh_from_db()
        self.assertEqual(self.job.views_count, 0)

    def test_other_recruiters_views_are_counted(self):
        other = make_recruiter("other@acme.test", self.company)
        self.client.force_authenticate(user=other)

        self.client.get(self.public_url)

        self.job.refresh_from_db()
        self.assertEqual(self.job.views_count, 1)

    def test_recruiter_job_list_reports_the_count(self):
        self.client.get(self.public_url)
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(reverse("api:v1:recruiter:jobs-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["views_count"], 1)


def make_seeker(email, first_name, last_name="Seeker"):
    return User.objects.create(
        username=email.split("@")[0],
        email=email,
        first_name=first_name,
        last_name=last_name,
        user_type="JS",
    )


class JobApplicantsListTests(NoSearchIndexMixin, TestCase):
    """
    The applicants endpoint backs both the on-screen list and the CSV export.

    Three defects lived here: `search` was accepted by the callers but never
    read, the tab counts were computed after the status filter (so choosing
    one tab zeroed the rest), and the "Hired" count queried a status value
    that does not exist in POST_STATUS.
    """

    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="Acme", slug="acme")
        self.recruiter = make_recruiter("owner@acme.test", self.company, is_admin=True)
        self.job = JobPost.objects.create(
            user=self.recruiter,
            title="Backend Engineer",
            slug="/backend-engineer/",
            status="Live",
            vacancies=1,
        )

        self.alice = make_seeker("alice@example.test", "Alice")
        self.bob = make_seeker("bob@example.test", "Bob")
        self.carol = make_seeker("carol@example.test", "Carol")
        self.dave = make_seeker("dave@example.test", "Dave")

        AppliedJobs.objects.create(job_post=self.job, user=self.alice, status="Pending")
        AppliedJobs.objects.create(
            job_post=self.job, user=self.bob, status="Shortlisted"
        )
        AppliedJobs.objects.create(job_post=self.job, user=self.carol, status="Hired")
        AppliedJobs.objects.create(job_post=self.job, user=self.dave, status="Rejected")

        self.url = reverse("api:v1:recruiter:jobs-applicants", args=[self.job.id])
        self.client.force_authenticate(user=self.recruiter)

    def _names(self, response):
        return " ".join(a["applicant"]["name"] for a in response.data["applications"])

    def test_returns_every_applicant_without_filters(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_applicants"], 4)
        self.assertEqual(len(response.data["applications"]), 4)

    def test_search_matches_first_name(self):
        response = self.client.get(self.url, {"search": "alice"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["applications"]), 1)
        self.assertIn("Alice", self._names(response))

    def test_search_matches_email(self):
        response = self.client.get(self.url, {"search": "carol@example"})

        self.assertEqual(len(response.data["applications"]), 1)
        self.assertIn("Carol", self._names(response))

    def test_search_that_matches_nothing_returns_nothing(self):
        """The old code ignored `search` entirely and returned all four."""
        response = self.client.get(self.url, {"search": "zzz-no-such-person"})

        self.assertEqual(len(response.data["applications"]), 0)
        self.assertEqual(response.data["total_applicants"], 0)

    def test_stats_do_not_collapse_when_a_status_filter_is_applied(self):
        """
        Picking one tab must not zero the other tabs' counts — they are
        counted before the status filter.
        """
        response = self.client.get(self.url, {"status": "Pending"})

        self.assertEqual(len(response.data["applications"]), 1)
        self.assertEqual(response.data["stats"]["pending"], 1)
        self.assertEqual(response.data["stats"]["shortlisted"], 1)
        self.assertEqual(response.data["stats"]["selected"], 1)
        self.assertEqual(response.data["stats"]["rejected"], 1)
        self.assertEqual(response.data["total_applicants"], 4)

    def test_hired_applicants_are_counted(self):
        """`selected` is the wire name; the stored status is "Hired"."""
        response = self.client.get(self.url)

        self.assertEqual(response.data["stats"]["selected"], 1)

    def test_stats_narrow_with_the_search(self):
        response = self.client.get(self.url, {"search": "carol"})

        self.assertEqual(response.data["total_applicants"], 1)
        self.assertEqual(response.data["stats"]["selected"], 1)
        self.assertEqual(response.data["stats"]["pending"], 0)

    def test_search_and_status_combine(self):
        response = self.client.get(self.url, {"search": "alice", "status": "Rejected"})

        self.assertEqual(len(response.data["applications"]), 0)
