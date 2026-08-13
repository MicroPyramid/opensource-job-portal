"""Tests for the shared lookup helpers in ``api/v1/common/``."""

from django.test import TestCase

from api.v1.common.search import fuzzy_name_filter
from peeldb.models import Skill


class FuzzyNameFilterTests(TestCase):
    """Substring matching first, trigram similarity only as a rescue.

    The ordering difference between the two paths is deliberate and easy to
    regress, so it is asserted directly.
    """

    @classmethod
    def setUpTestData(cls):
        for name in ("Python", "Django", "JavaScript", "Core Java", "Bangalore Ops"):
            Skill.objects.create(name=name, slug=name.lower().replace(" ", "-"))

    def names(self, term):
        return list(
            fuzzy_name_filter(Skill.objects.all(), term).values_list("name", flat=True)
        )

    def test_substring_fragment_matches(self):
        """A fragment is what an autocomplete actually sends.

        Trigram similarity scores "pyt" against "Python" poorly, which is why
        substring matching has to stay the primary path.
        """
        self.assertEqual(self.names("pyt"), ["Python"])

    def test_matching_is_case_insensitive(self):
        self.assertEqual(self.names("PYTHON"), ["Python"])

    def test_substring_hits_are_alphabetical(self):
        self.assertEqual(self.names("java"), ["Core Java", "JavaScript"])

    def test_typo_falls_back_to_similarity(self):
        self.assertEqual(self.names("Djanog"), ["Django"])

    def test_fuzzy_path_orders_by_closeness_not_name(self):
        """Alphabetical order on the fallback path would bury the answer."""
        Skill.objects.create(name="Djangoish Tooling", slug="djangoish-tooling")

        self.assertEqual(self.names("Djanog")[0], "Django")

    def test_fuzzy_does_not_run_when_substring_matches(self):
        """ "Java" must not also drag in loosely-similar names."""
        self.assertNotIn("Bangalore Ops", self.names("java"))

    def test_nonsense_matches_nothing(self):
        self.assertEqual(self.names("qqzzxx"), [])

    def test_blank_term_returns_everything_alphabetically(self):
        names = self.names("   ")

        self.assertEqual(len(names), Skill.objects.count())
        self.assertEqual(names, sorted(names))
