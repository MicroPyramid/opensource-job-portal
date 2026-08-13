"""
Tests for the Job Seeker profile sub-resources.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from peeldb.models import Language, User, UserLanguage


class UserLanguageAPITests(TestCase):
    """
    Languages a job seeker speaks.

    Replaces `candidate.views.add_language` / `edit_language` /
    `delete_language` and their three `-modal` twins.
    """

    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse("api:v1:profile:language-list")
        self.options_url = reverse("api:v1:profile:language-option-list")

        self.english = Language.objects.create(name="English")
        self.hindi = Language.objects.create(name="Hindi")

        self.user = User.objects.create_user(
            username="seeker@example.com",
            email="seeker@example.com",
            password="Str0ng!Passw0rd",
        )
        self.user.user_type = "JS"
        self.user.is_active = True
        self.user.save()

        self.client.force_authenticate(user=self.user)

    def _detail_url(self, pk):
        return reverse("api:v1:profile:language-detail", args=[pk])

    def _add(self, language=None, **flags):
        payload = {"language": (language or self.english).id, "read": True}
        payload.update(flags)
        return self.client.post(self.list_url, payload, format="json")

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)

        self.assertEqual(
            self.client.get(self.list_url).status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_catalogue_lists_languages(self):
        response = self.client.get(self.options_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [entry["name"] for entry in response.data], ["English", "Hindi"]
        )

    def test_add_and_list(self):
        create = self._add(speak=True)
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create.data["language_name"], "English")

        listing = self.client.get(self.list_url)
        self.assertEqual(len(listing.data), 1)

    def test_duplicate_language_rejected(self):
        self._add()

        response = self._add()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.user.language.count(), 1)

    def test_no_proficiency_rejected(self):
        response = self._add(read=False, write=False, speak=False)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_proficiency(self):
        created = self._add()

        response = self.client.patch(
            self._detail_url(created.data["id"]), {"write": True}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["write"])

    def test_delete_removes_the_row_not_just_the_link(self):
        created = self._add()
        row_id = created.data["id"]

        response = self.client.delete(self._detail_url(row_id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user.language.count(), 0)
        # A UserLanguage belongs to exactly one user, so detaching without
        # deleting would strand a row nothing can reach again.
        self.assertFalse(UserLanguage.objects.filter(id=row_id).exists())

    def test_cannot_touch_another_users_language(self):
        created = self._add()
        row_id = created.data["id"]

        other = User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="Str0ng!Passw0rd",
        )
        other.user_type = "JS"
        other.save()
        self.client.force_authenticate(user=other)

        response = self.client.delete(self._detail_url(row_id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(UserLanguage.objects.filter(id=row_id).exists())

    def test_recruiters_are_rejected(self):
        self.user.user_type = "RR"
        self.user.save()

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
