"""
Tests for the job-seeker job endpoints.

Covers ``GET /api/v1/jobs/applied/``, added so the /applications/ page in
``site/`` had something real to render — it previously shipped a hardcoded
list of fake applications.
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


def make_user(email, user_type="JS", company=None):
    return User.objects.create(
        username=email.split("@")[0],
        email=email,
        first_name=email.split("@")[0].title(),
        last_name="Tester",
        user_type=user_type,
        company=company,
    )


class AppliedJobsListTests(NoSearchIndexMixin, TestCase):
    """GET /api/v1/jobs/applied/ returns only the caller's applications."""

    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="Acme", slug="acme")
        self.recruiter = make_user("owner@acme.test", "EM", self.company)

        self.seeker = make_user("seeker@example.test")
        self.other_seeker = make_user("other@example.test")

        self.job_a = JobPost.objects.create(
            user=self.recruiter,
            title="Backend Engineer",
            slug="/backend-engineer/",
            status="Live",
            vacancies=1,
            company=self.company,
        )
        self.job_b = JobPost.objects.create(
            user=self.recruiter,
            title="Frontend Engineer",
            slug="/frontend-engineer/",
            status="Live",
            vacancies=1,
            company=self.company,
        )

        self.url = reverse("api:v1:jobs:job-applied-jobs")

    def test_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_returns_an_empty_list_when_nothing_applied(self):
        self.client.force_authenticate(user=self.seeker)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_returns_the_users_applications_with_the_nested_job(self):
        AppliedJobs.objects.create(
            job_post=self.job_a, user=self.seeker, status="Pending"
        )
        self.client.force_authenticate(user=self.seeker)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        row = response.data[0]
        self.assertEqual(row["status"], "Pending")
        self.assertEqual(row["job"]["id"], self.job_a.id)
        self.assertEqual(row["job"]["title"], "Backend Engineer")
        self.assertIn("applied_on", row)

    def test_does_not_leak_other_users_applications(self):
        AppliedJobs.objects.create(
            job_post=self.job_a, user=self.other_seeker, status="Pending"
        )
        self.client.force_authenticate(user=self.seeker)

        response = self.client.get(self.url)

        self.assertEqual(response.data, [])

    def test_newest_application_comes_first(self):
        AppliedJobs.objects.create(
            job_post=self.job_a, user=self.seeker, status="Pending"
        )
        AppliedJobs.objects.create(
            job_post=self.job_b, user=self.seeker, status="Pending"
        )
        self.client.force_authenticate(user=self.seeker)

        response = self.client.get(self.url)

        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["job"]["id"], self.job_b.id)

    def test_status_filter(self):
        AppliedJobs.objects.create(
            job_post=self.job_a, user=self.seeker, status="Pending"
        )
        AppliedJobs.objects.create(
            job_post=self.job_b, user=self.seeker, status="Hired"
        )
        self.client.force_authenticate(user=self.seeker)

        response = self.client.get(self.url, {"status": "Hired"})

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["job"]["id"], self.job_b.id)
