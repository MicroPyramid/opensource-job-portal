"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase

# from django.test import Client
from .forms import SimpleContactForm, SubscribeForm


class SimpleContactForm_form_test(TestCase):
    def test_contactinfo_for_valid(self):
        form = SimpleContactForm(
            data={
                "first_name": "hello",
                "last_name": "mp",
                "comment": "my job post comment",
                "email": "mp@mp.com",
                "enquery_type": "Suggestion",
            }
        )
        self.assertTrue(form.is_valid())

    def test_contactinfo_form_invalid(self):
        form = SimpleContactForm(
            data={
                "first_name": "",
                "last_name": "",
                "comment": "",
                "email": "",
                "enquery_type": "",
            }
        )
        self.assertFalse(form.is_valid())


class SubscribeForm_test(TestCase):
    def test_subscribe_for_valid(self):
        form = SubscribeForm(data={"email": "mp@mp.com", "subscribe_from": "all"})
        self.assertTrue(form.is_valid())

    def test_subscribe_form_invalid(self):
        form = SubscribeForm(data={"email": ""})
        self.assertFalse(form.is_valid())
