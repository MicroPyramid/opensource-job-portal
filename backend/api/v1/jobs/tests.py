"""
Tests for the job-seeker job endpoints.

Covers ``GET /api/v1/jobs/applied/``, added so the /applications/ page in
``site/`` had something real to render — it previously shipped a hardcoded
list of fake applications.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from peeldb.models import AppliedJobs, Company, JobPost, User


def make_user(email, user_type="JS", company=None):
    return User.objects.create(
        username=email.split("@")[0],
        email=email,
        first_name=email.split("@")[0].title(),
        last_name="Tester",
        user_type=user_type,
        company=company,
    )


class AppliedJobsListTests(TestCase):
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


class CompanyFilterTests(TestCase):
    """
    `?company=` and `?company_slug=` scope the job list.

    Regression: `company` was being passed by site/'s company detail page but
    was never declared on `JobFilter`. django-filter silently ignores unknown
    params, so that page rendered every job on the board as if it belonged to
    the company being viewed.
    """

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("api:v1:jobs:job-list")

        self.acme = Company.objects.create(name="Acme Corp", slug="acme-corp")
        self.globex = Company.objects.create(name="Globex", slug="globex")
        recruiter = make_user("recruiter@acme.test", user_type="EM", company=self.acme)

        for i in range(3):
            JobPost.objects.create(
                user=recruiter,
                title=f"Acme Role {i}",
                slug=f"/acme-role-{i}/",
                status="Live",
                vacancies=1,
                company=self.acme,
            )
        JobPost.objects.create(
            user=recruiter,
            title="Globex Role",
            slug="/globex-role/",
            status="Live",
            vacancies=1,
            company=self.globex,
        )

    def test_unfiltered_returns_every_job(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4)

    def test_company_id_scopes_results(self):
        response = self.client.get(self.url, {"company": self.acme.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_company_slug_scopes_results(self):
        response = self.client.get(self.url, {"company_slug": "globex"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_company_slug_is_case_insensitive(self):
        response = self.client.get(self.url, {"company_slug": "GLOBEX"})
        self.assertEqual(response.data["count"], 1)

    def test_unknown_company_returns_nothing_not_everything(self):
        """The bug's signature: an unmatched filter must not fall open."""
        for params in ({"company": 99999999}, {"company_slug": "no-such-company"}):
            with self.subTest(params=params):
                response = self.client.get(self.url, params)
                self.assertEqual(response.data["count"], 0)


class FilterOptionsLimitTests(TestCase):
    """
    `?limit=` controls how many locations/skills come back.

    The SEO directory pages (/jobs-by-skill/) need every facet, not the top 50.
    """

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("api:v1:jobs:filter-options")

    def test_default_caps_at_fifty(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["skills"]), 50)
        self.assertLessEqual(len(response.data["locations"]), 50)

    def test_explicit_limit_is_honoured(self):
        response = self.client.get(self.url, {"limit": 3})
        self.assertLessEqual(len(response.data["skills"]), 3)
        self.assertLessEqual(len(response.data["locations"]), 3)

    def test_junk_limit_falls_back_to_default(self):
        """A bad limit must not 500 — it is reachable from a crawler."""
        for value in ("abc", "", "1.5"):
            with self.subTest(limit=value):
                response = self.client.get(self.url, {"limit": value})
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertLessEqual(len(response.data["skills"]), 50)

    def test_industries_and_education_are_never_capped(self):
        capped = self.client.get(self.url, {"limit": 1})
        self.assertEqual(capped.status_code, status.HTTP_200_OK)
        uncapped = self.client.get(self.url, {"limit": 0})
        self.assertEqual(
            len(capped.data["industries"]), len(uncapped.data["industries"])
        )
        self.assertEqual(len(capped.data["education"]), len(uncapped.data["education"]))


class JobSearchTests(TestCase):
    """`?search=` runs Postgres full-text search, not substring matching.

    The behaviours below are the ones that changed when Elasticsearch/Haystack
    came out and `JobPost.search_vector` went in, so each test names the defect
    it pins down rather than just asserting a count.
    """

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="Globex", slug="globex")
        cls.recruiter = make_user("hire@globex.test", "EM", cls.company)

        def job(title, **kwargs):
            return JobPost.objects.create(
                user=cls.recruiter,
                title=title,
                slug=f"/{title.lower().replace(' ', '-').replace('.', '')}/",
                status="Live",
                vacancies=1,
                company=cls.company,
                **kwargs,
            )

        # Word order reversed against the query, to prove tokenisation.
        cls.reversed_words = job("Developer - Python")
        cls.plain = job("Python Developer")
        # Only mentions the term in the description; must rank below a title hit.
        cls.body_only = job(
            "Backend Engineer", description="Some Python experience preferred"
        )
        # Stemming target: "manage" should reach "Managers".
        cls.stemmed = job("Engineering Managers Wanted")
        cls.unrelated = job("Pastry Chef")

        cls.url = reverse("api:v1:jobs:job-list")

    def titles(self, response):
        return [row["title"] for row in response.data["results"]]

    def test_matches_regardless_of_word_order(self):
        """The `icontains` version matched the literal phrase only.

        "Developer - Python" scored zero against "python developer" because the
        substring is not present; full-text search matches on tokens.
        """
        response = self.client.get(self.url, {"search": "python developer"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Developer - Python", self.titles(response))

    def test_title_hits_outrank_description_hits(self):
        """Weighting (title A, description D) is the point of the vector."""
        response = self.client.get(self.url, {"search": "python"})

        titles = self.titles(response)
        self.assertIn("Backend Engineer", titles)
        self.assertLess(
            titles.index("Python Developer"),
            titles.index("Backend Engineer"),
        )

    def test_stems_so_manage_finds_managers(self):
        response = self.client.get(self.url, {"search": "manage"})

        self.assertIn("Engineering Managers Wanted", self.titles(response))

    def test_excludes_unrelated_jobs(self):
        """Ranking must not turn into "everything matches, weakly"."""
        response = self.client.get(self.url, {"search": "python"})

        self.assertNotIn("Pastry Chef", self.titles(response))

    def test_typo_falls_back_to_fuzzy_matching(self):
        """A misspelling returns near matches instead of an empty page."""
        response = self.client.get(self.url, {"search": "developper"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data["count"], 0)
        for title in self.titles(response):
            self.assertIn("Developer", title)

    def test_fuzzy_does_not_run_when_full_text_matches(self):
        """Fallback, not blend — a good query stays free of trigram noise."""
        response = self.client.get(self.url, {"search": "chef"})

        self.assertEqual(self.titles(response), ["Pastry Chef"])

    def test_nonsense_returns_nothing(self):
        response = self.client.get(self.url, {"search": "qqzzxx"})

        self.assertEqual(response.data["count"], 0)

    def test_blank_search_returns_everything(self):
        """`?search=` with no value must not be treated as a search.

        It leaves the queryset unannotated, so relevance ordering has to stand
        down or ordering by `search_rank` would raise FieldError.
        """
        response = self.client.get(self.url, {"search": "  "})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], JobPost.objects.count())

    def test_explicit_ordering_beats_relevance(self):
        """Relevance is only the *default* while searching."""
        response = self.client.get(self.url, {"search": "python", "ordering": "title"})

        titles = self.titles(response)
        self.assertEqual(titles, sorted(titles))

    def test_search_composes_with_filters(self):
        """Search narrows the filtered set; it does not replace it."""
        response = self.client.get(
            self.url, {"search": "python", "company_slug": "globex"}
        )
        self.assertGreater(response.data["count"], 0)

        response = self.client.get(
            self.url, {"search": "python", "company_slug": "nonexistent"}
        )
        self.assertEqual(response.data["count"], 0)

    def test_search_vector_is_maintained_by_the_database(self):
        """No signal, no reindex task — Postgres fills it on write.

        This is the property that made the Elasticsearch index removable, so
        it is worth pinning: an edit through the ORM is searchable immediately,
        inside the same transaction.
        """
        job = JobPost.objects.create(
            user=self.recruiter,
            title="Kubernetes Administrator",
            slug="/kubernetes-administrator/",
            status="Live",
            vacancies=1,
        )
        response = self.client.get(self.url, {"search": "kubernetes"})
        self.assertIn("Kubernetes Administrator", self.titles(response))

        job.title = "Terraform Administrator"
        job.save()

        response = self.client.get(self.url, {"search": "kubernetes"})
        self.assertNotIn("Kubernetes Administrator", self.titles(response))
        response = self.client.get(self.url, {"search": "terraform"})
        self.assertIn("Terraform Administrator", self.titles(response))
