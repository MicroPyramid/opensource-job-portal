"""
Tests for the gaps closed when finishing the Django → SvelteKit/DRF migration.

Covers the three behaviours that were shipped in the UI but not wired to the
API: the job email-notification toggle, team member activate/deactivate, and
job view counting.
"""

from unittest import mock

from django.core import signing
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from peeldb.models import AppliedJobs, Company, Google, JobPost, User

from .auth_views import GOOGLE_SIGNUP_SALT


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


class JobEmailNotificationTests(TestCase):
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


class TeamMemberStatusToggleTests(TestCase):
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


class JobViewCountTests(TestCase):
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


class JobApplicantsListTests(TestCase):
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


class ChangePasswordTests(TestCase):
    """
    The endpoint existed but had no caller, so it had never been exercised.
    Wiring the account page to it makes these the first checks it has.
    """

    def setUp(self):
        self.client = APIClient()
        self.recruiter = make_recruiter("pwd@acme.test")
        self.recruiter.set_password("OriginalPass123")
        self.recruiter.save()
        self.url = reverse("api:v1:recruiter:change-password")

    def test_requires_authentication(self):
        response = self.client.post(
            self.url,
            {
                "old_password": "OriginalPass123",
                "new_password": "BrandNewPass456",
                "confirm_password": "BrandNewPass456",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_changes_the_password(self):
        self.client.force_authenticate(user=self.recruiter)

        response = self.client.post(
            self.url,
            {
                "old_password": "OriginalPass123",
                "new_password": "BrandNewPass456",
                "confirm_password": "BrandNewPass456",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.recruiter.refresh_from_db()
        self.assertTrue(self.recruiter.check_password("BrandNewPass456"))
        self.assertFalse(self.recruiter.check_password("OriginalPass123"))

    def test_rejects_a_wrong_current_password(self):
        self.client.force_authenticate(user=self.recruiter)

        response = self.client.post(
            self.url,
            {
                "old_password": "NotMyPassword",
                "new_password": "BrandNewPass456",
                "confirm_password": "BrandNewPass456",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.recruiter.refresh_from_db()
        self.assertTrue(self.recruiter.check_password("OriginalPass123"))

    def test_rejects_mismatched_confirmation(self):
        self.client.force_authenticate(user=self.recruiter)

        response = self.client.post(
            self.url,
            {
                "old_password": "OriginalPass123",
                "new_password": "BrandNewPass456",
                "confirm_password": "SomethingElse789",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.recruiter.refresh_from_db()
        self.assertTrue(self.recruiter.check_password("OriginalPass123"))


class GoogleSignupTokenTests(TestCase):
    """
    google_callback hands the pending signup to the client as a signed blob and
    google_complete reads it back.

    It used to go through ``request.session``, which could never work: the only
    caller is the SvelteKit server, which holds no session cookie, so every
    request built a fresh empty session and google_complete always answered
    "Invalid or expired session token". These pin the stateless replacement.
    """

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("api:v1:recruiter:google-complete")
        self.google_identity = {
            "google_id": "109876543210",
            "email": "newrecruiter@acme.test",
            "first_name": "New",
            "last_name": "Recruiter",
            "picture": "",
        }

    def sign(self, **overrides):
        return signing.dumps(
            {**self.google_identity, **overrides}, salt=GOOGLE_SIGNUP_SALT
        )

    def test_creates_the_account_from_a_signed_token(self):
        response = self.client.post(
            self.url,
            {
                "session_token": self.sign(),
                "account_type": "company",
                "company_name": "Acme Hiring",
                "company_website": "https://acme.test",
                "agree_to_terms": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)

        user = User.objects.get(email="newrecruiter@acme.test")
        self.assertEqual(user.user_type, "EM")
        self.assertEqual(user.company.name, "Acme Hiring")
        self.assertTrue(Google.objects.filter(user=user).exists())

    def test_rejects_a_tampered_token(self):
        """The whole point of signing: a forged email must not create an account."""
        tampered = self.sign()[:-4] + "AAAA"

        response = self.client.post(
            self.url,
            {
                "session_token": tampered,
                "account_type": "recruiter",
                "agree_to_terms": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="newrecruiter@acme.test").exists())

    def test_rejects_a_token_signed_with_another_salt(self):
        """A signed blob from elsewhere in the project must not be replayable here."""
        foreign = signing.dumps(self.google_identity, salt="some-other-flow")

        response = self.client.post(
            self.url,
            {
                "session_token": foreign,
                "account_type": "recruiter",
                "agree_to_terms": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="newrecruiter@acme.test").exists())

    def test_rejects_an_expired_token(self):
        with mock.patch("api.v1.recruiter.auth_views.GOOGLE_SIGNUP_MAX_AGE", -1):
            response = self.client.post(
                self.url,
                {
                    "session_token": self.sign(),
                    "account_type": "recruiter",
                    "agree_to_terms": True,
                },
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="newrecruiter@acme.test").exists())

    def test_rejects_a_token_longer_than_the_old_100_char_cap(self):
        """
        The serializer used to cap session_token at 100 characters, which a
        signed payload always exceeds — the flow would have 400'd on length
        before the signature was ever checked.
        """
        self.assertGreater(len(self.sign()), 100)

    def test_refuses_an_email_that_already_exists(self):
        make_recruiter("newrecruiter@acme.test")

        response = self.client.post(
            self.url,
            {
                "session_token": self.sign(),
                "account_type": "recruiter",
                "agree_to_terms": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordStrengthTests(TestCase):
    """
    AUTH_PASSWORD_VALIDATORS was absent from settings. Django treats a missing
    setting as an empty list, so every validate_password() call ran zero checks
    and "password123" sailed through registration, reset and change-password.

    These pin the four validators. If the setting is dropped again, or a
    serializer stops passing the user, one of these fails.
    """

    def setUp(self):
        self.client = APIClient()
        self.recruiter = make_recruiter("strength@acme.test")
        self.recruiter.set_password("OriginalPass123")
        self.recruiter.save()
        self.client.force_authenticate(user=self.recruiter)
        self.url = reverse("api:v1:recruiter:change-password")

    def change_to(self, new_password):
        return self.client.post(
            self.url,
            {
                "old_password": "OriginalPass123",
                "new_password": new_password,
                "confirm_password": new_password,
            },
            format="json",
        )

    def assert_unchanged(self, response):
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.recruiter.refresh_from_db()
        self.assertTrue(self.recruiter.check_password("OriginalPass123"))

    def test_rejects_a_common_password(self):
        """CommonPasswordValidator — the case that exposed the missing setting."""
        self.assert_unchanged(self.change_to("password123"))

    def test_rejects_an_all_numeric_password(self):
        """NumericPasswordValidator."""
        self.assert_unchanged(self.change_to("859213476"))

    def test_rejects_a_password_resembling_the_email(self):
        """
        UserAttributeSimilarityValidator, which only runs when
        validate_password() is handed the user — so this also pins that the
        serializer passes `self.context["request"].user`.
        """
        self.assert_unchanged(self.change_to("strength@acme.test"))

    def test_accepts_a_strong_password(self):
        response = self.change_to("Tr0ubad0ur-Vex9")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recruiter.refresh_from_db()
        self.assertTrue(self.recruiter.check_password("Tr0ubad0ur-Vex9"))

    def test_registration_rejects_a_common_password(self):
        """The same validators must apply on the way in, not just on change."""
        response = self.client.post(
            reverse("api:v1:recruiter:register"),
            {
                "account_type": "recruiter",
                "first_name": "Weak",
                "last_name": "Signup",
                "email": "weak-signup@acme.test",
                "password": "password123",
                "confirm_password": "password123",
                "agree_to_terms": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="weak-signup@acme.test").exists())

    def test_registration_rejects_a_password_matching_the_email(self):
        """Pins the unsaved-User instance passed from RegisterSerializer."""
        response = self.client.post(
            reverse("api:v1:recruiter:register"),
            {
                "account_type": "recruiter",
                "first_name": "Same",
                "last_name": "Asemail",
                "email": "sameasemail@acme.test",
                "password": "sameasemail@acme.test",
                "confirm_password": "sameasemail@acme.test",
                "agree_to_terms": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="sameasemail@acme.test").exists())


class CompanyScopedJobAccessTests(TestCase):
    """
    A company admin owns what their team posts.

    The legacy dashboard scoped on ``user__company`` for admins
    (``recruiter/views.py:748`` at ``ad39524``); every DRF view was rewritten
    with a hardcoded ``user=request.user``. Team management shipped anyway, so
    an admin could invite a recruiter and then see nothing they posted.
    """

    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="Acme", slug="acme")
        self.rival = Company.objects.create(name="Rival", slug="rival")

        self.admin = make_recruiter("admin@acme.test", self.company, is_admin=True)
        self.member = make_recruiter("member@acme.test", self.company)
        self.outsider = make_recruiter("boss@rival.test", self.rival, is_admin=True)

        self.member_job = JobPost.objects.create(
            user=self.member,
            title="Member's Job",
            slug="/members-job/",
            status="Draft",
            vacancies=1,
        )
        self.admin_job = JobPost.objects.create(
            user=self.admin,
            title="Admin's Job",
            slug="/admins-job/",
            status="Live",
            vacancies=1,
        )

    def _titles(self, response):
        payload = response.data
        results = payload["results"] if isinstance(payload, dict) else payload
        return {job["title"] for job in results}

    def test_admin_lists_the_whole_companys_jobs(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse("api:v1:recruiter:jobs-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._titles(response), {"Member's Job", "Admin's Job"})

    def test_member_lists_only_their_own_jobs(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.get(reverse("api:v1:recruiter:jobs-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._titles(response), {"Member's Job"})

    def test_admin_opens_a_teammates_job(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("api:v1:recruiter:jobs-detail", args=[self.member_job.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Member's Job")

    def test_admin_edits_a_teammates_draft(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("api:v1:recruiter:jobs-update", args=[self.member_job.id])

        response = self.client.patch(url, {"title": "Retitled"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.member_job.refresh_from_db()
        self.assertEqual(self.member_job.title, "Retitled")

    def test_admin_sees_applicants_on_a_teammates_job(self):
        applicant = User.objects.create(
            username="seeker", email="seeker@example.test", user_type="JS"
        )
        AppliedJobs.objects.create(
            user=applicant, job_post=self.member_job, status="Pending"
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse("api:v1:recruiter:jobs-applicants", args=[self.member_job.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_applicants"], 1)
        self.assertEqual(len(response.data["applications"]), 1)

    def test_member_cannot_open_a_teammates_job(self):
        self.client.force_authenticate(user=self.member)
        url = reverse("api:v1:recruiter:jobs-detail", args=[self.admin_job.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_another_companys_admin_is_still_shut_out(self):
        """The widened scope must stop at the company boundary."""
        self.client.force_authenticate(user=self.outsider)

        detail = self.client.get(
            reverse("api:v1:recruiter:jobs-detail", args=[self.member_job.id])
        )
        listing = self.client.get(reverse("api:v1:recruiter:jobs-list"))

        self.assertEqual(detail.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self._titles(listing), set())

    def test_dashboard_stats_cover_the_company_for_an_admin(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse("api:v1:recruiter:dashboard-stats"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stats"]["total_jobs"], 2)

    def test_dashboard_stats_stay_personal_for_a_member(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.get(reverse("api:v1:recruiter:dashboard-stats"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stats"]["total_jobs"], 1)

    def test_analytics_cover_the_company_for_an_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("api:v1:recruiter:job-analytics", args=[self.member_job.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_an_admin_without_a_company_falls_back_to_their_own_jobs(self):
        """``is_company_admin`` requires a company; the scope must not widen."""
        stray = make_recruiter("stray@nowhere.test", None, is_admin=True)
        JobPost.objects.create(
            user=stray, title="Stray's Job", slug="/strays-job/", vacancies=1
        )
        self.client.force_authenticate(user=stray)

        response = self.client.get(reverse("api:v1:recruiter:jobs-list"))

        self.assertEqual(self._titles(response), {"Stray's Job"})


class WalkinAndGovernmentJobTests(TestCase):
    """
    The two job types the dashboard could not post.

    The serializer has always accepted these fields; no form rendered them, so
    `walk-in` — 1,973 posts in the data, with its own landing pages on the job
    seeker site — could only be created from the platform-admin dashboard.
    These pin the payloads the rebuilt forms send.
    """

    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="Acme", slug="acme")
        self.recruiter = make_recruiter("poster@acme.test", self.company, is_admin=True)
        self.client.force_authenticate(user=self.recruiter)

    def test_a_walkin_job_keeps_its_walkin_fields(self):
        response = self.client.post(
            reverse("api:v1:recruiter:jobs-create"),
            {
                "title": "Walk-in: Support Engineer",
                "job_type": "walk-in",
                "walkin_contactinfo": "Ask for Priya, Gate 2",
                "walkin_show_contact_info": True,
                "walkin_from_date": "2026-09-01",
                "walkin_to_date": "2026-09-05",
                "walkin_time": "10:00:00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        job = JobPost.objects.get(title="Walk-in: Support Engineer")
        self.assertEqual(job.job_type, "walk-in")
        self.assertEqual(job.walkin_contactinfo, "Ask for Priya, Gate 2")
        self.assertTrue(job.walkin_show_contact_info)
        self.assertEqual(str(job.walkin_from_date), "2026-09-01")
        self.assertEqual(str(job.walkin_to_date), "2026-09-05")
        self.assertEqual(str(job.walkin_time), "10:00:00")

    def test_a_government_job_keeps_its_government_fields(self):
        response = self.client.post(
            reverse("api:v1:recruiter:jobs-create"),
            {
                "title": "Junior Assistant",
                "job_type": "government",
                "govt_job_type": "Central",
                "application_fee": "500",
                "selection_process": "Written exam, then interview",
                "how_to_apply": "Apply on the official portal",
                "important_dates": "Admit card: 2026-10-01",
                "govt_from_date": "2026-09-01",
                "govt_to_date": "2026-09-30",
                "govt_exam_date": "2026-11-15",
                "age_relaxation": "5 years for SC/ST",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        job = JobPost.objects.get(title="Junior Assistant")
        self.assertEqual(job.job_type, "government")
        self.assertEqual(job.govt_job_type, "Central")
        self.assertEqual(job.application_fee, 500)
        self.assertEqual(job.selection_process, "Written exam, then interview")
        self.assertEqual(job.age_relaxation, "5 years for SC/ST")
        self.assertEqual(str(job.govt_exam_date), "2026-11-15")

    def test_editing_a_walkin_draft_can_change_its_dates(self):
        job = JobPost.objects.create(
            user=self.recruiter,
            title="Walk-in Draft",
            slug="/walkin-draft/",
            status="Draft",
            job_type="walk-in",
            vacancies=1,
            walkin_from_date="2026-09-01",
        )

        response = self.client.patch(
            reverse("api:v1:recruiter:jobs-update", args=[job.id]),
            {"walkin_from_date": "2026-09-08", "walkin_time": "09:30:00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        job.refresh_from_db()
        self.assertEqual(str(job.walkin_from_date), "2026-09-08")
        self.assertEqual(str(job.walkin_time), "09:30:00")


class PartialJobUpdatePreservesUnsentFieldsTests(TestCase):
    """
    A PATCH must leave out what it does not send.

    The edit form used to emit `false` for every boolean it does not render —
    PATCH is partial, but a key that is present is a key that gets written. So
    editing a title cleared show_salary (which defaults to *true*), fresher and
    relocation_required, demoted hiring_priority to Normal and reset
    application_method to portal. These pin the contract the fixed form relies
    on: omit the key, keep the value.
    """

    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="Acme", slug="acme")
        self.recruiter = make_recruiter("editor@acme.test", self.company, is_admin=True)
        self.client.force_authenticate(user=self.recruiter)
        self.job = JobPost.objects.create(
            user=self.recruiter,
            title="Original",
            slug="/original/",
            status="Draft",
            vacancies=1,
            show_salary=True,
            relocation_required=True,
            hiring_priority="High",
            application_method="external",
            application_url="https://acme.test/apply",
            salary_type="Month",
            company_description="Acme builds anvils.",
        )

    def test_a_title_only_patch_touches_nothing_else(self):
        response = self.client.patch(
            reverse("api:v1:recruiter:jobs-update", args=[self.job.id]),
            {"title": "Renamed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.title, "Renamed")
        self.assertTrue(self.job.show_salary)
        self.assertTrue(self.job.relocation_required)
        self.assertEqual(self.job.hiring_priority, "High")
        self.assertEqual(self.job.application_method, "external")
        self.assertEqual(self.job.salary_type, "Month")
        self.assertEqual(self.job.company_description, "Acme builds anvils.")

    def test_the_application_method_can_be_changed(self):
        """
        Newly reachable: the edit form had no application-method control, so
        this field could only ever be reset by the `|| 'portal'` default it
        used to send.
        """
        response = self.client.patch(
            reverse("api:v1:recruiter:jobs-update", args=[self.job.id]),
            {"application_method": "portal"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.application_method, "portal")

    def test_an_explicit_false_still_wins(self):
        """Omission preserves; sending the field must still write it."""
        response = self.client.patch(
            reverse("api:v1:recruiter:jobs-update", args=[self.job.id]),
            {"show_salary": False, "salary_type": "Year"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertFalse(self.job.show_salary)
        self.assertEqual(self.job.salary_type, "Year")
