from django.test import TestCase
from .forms import *


class ticket_form_test(TestCase):

    def test_ticket_for_valid(self):
        form = TicketForm(
            data={'title': 'test', 'description': 'test-ticket', 'priority': 'High', 'ticket_type': 'Enhancement'})
        print (form.errors)
        self.assertTrue(form.is_valid())

    def test_ticket_form_invalid(self):
        form = TicketForm(
            data={'title': 'test', 'description': '', 'priority': '', 'ticket_type': ''})
        self.assertFalse(form.is_valid())


class comment_form_test(TestCase):

    def test_ticket_for_valid(self):
        form = CommentForm(
            data={'comment': 'mp'})
        self.assertTrue(form.is_valid())

    def test_ticket_form_invalid(self):
        form = CommentForm(
            data={'comment': ''})
        self.assertFalse(form.is_valid())

# Create your tests here.
