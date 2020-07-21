"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase

# from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import (
    ChangePasswordForm,
    CountryForm,
    CityForm,
    StateForm,
    SkillForm,
    LanguageForm,
    QualificationForm,
    IndustryForm,
    FunctionalAreaForm,
    UserForm,
)
from peeldb.models import Country, State


class ChangePasswordForm_form_test(TestCase):
    def test_personalinfo_for_valid(self):
        form = ChangePasswordForm(
            data={
                "oldpassword": "mp",
                "newpassword": "mp123",
                "retypepassword": "mp123",
            }
        )
        self.assertTrue(form.is_valid())

    def test_personalinfo_form_invalid(self):
        form = ChangePasswordForm(
            data={"oldpassword": "", "newpassword": "", "retypepassword": ""}
        )
        self.assertFalse(form.is_valid())


class CountryForm_form_test(TestCase):
    def test_country_for_valid(self):
        form = CountryForm(data={"name": "India"})
        self.assertTrue(form.is_valid())

    def test_country_form_invalid(self):
        form = CountryForm(data={"name": ""})
        self.assertFalse(form.is_valid())


class CityForm_form_test(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="India")
        self.state = State.objects.create(name="Telangana", country_id=self.country.id)

    def test_cityinfo_for_valid(self):
        form = CityForm(data={"name": "hyd", "state": self.state.id})
        self.assertTrue(form.is_valid())

    def test_cityinfo_form_invalid(self):
        form = CityForm(data={"name": "", "statte": self.state.id})
        self.assertFalse(form.is_valid())


class StateForm_form_test(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="India")

    def test_stateinfo_for_valid(self):
        form = StateForm(data={"name": "ap", "country": self.country.id})
        self.assertTrue(form.is_valid())

    def test_stateinfo_form_invalid(self):
        form = StateForm(data={"name": "", "country": ""})
        self.assertFalse(form.is_valid())


class SkillForm_form_test(TestCase):
    def test_country_for_valid(self):
        form = SkillForm(data={"name": "mba"})
        self.assertTrue(form.is_valid())

    def test_country_form_invalid(self):
        form = SkillForm(data={"name": ""})
        self.assertFalse(form.is_valid())


class LanguageForm_form_test(TestCase):
    def test_language_for_valid(self):
        form = LanguageForm(data={"name": "telugu"})
        self.assertTrue(form.is_valid())

    def test_language_form_invalid(self):
        form = LanguageForm(data={"name": ""})
        self.assertFalse(form.is_valid())


class QualificationForm_form_test(TestCase):
    def test_qualification_for_valid(self):
        form = QualificationForm(data={"name": "qualification"})
        self.assertTrue(form.is_valid())

    def test_qualification_form_invalid(self):
        form = QualificationForm(data={"name": ""})
        self.assertFalse(form.is_valid())


class IndustryForm_form_test(TestCase):
    def test_industry_for_valid(self):
        form = IndustryForm(data={"name": "industry"})
        self.assertTrue(form.is_valid())

    def test_industry_form_invalid(self):
        form = IndustryForm(data={"name": ""})
        self.assertFalse(form.is_valid())


class FunctionalAreaForm_form_test(TestCase):
    def test_functinalarea_for_valid(self):
        form = FunctionalAreaForm(data={"name": "functinalarea"})
        self.assertTrue(form.is_valid())

    def test_functinalarea_form_invalid(self):
        form = FunctionalAreaForm(data={"name": ""})
        self.assertFalse(form.is_valid())


class user_form_test(TestCase):
    def test_user_form_for_valid(self):
        upload_file = open("static/img/report.png", "rb")
        file_dict = {
            "profile_pic": SimpleUploadedFile(upload_file.name, upload_file.read())
        }
        data = {
            "email": "mp@mp.com",
            "first_name": "hello",
            "address": "hyd",
            "permanent_address": "hyd",
            "mobile": "1234567890",
            "gender": "F",
            "last_name": "mp",
            "user_type": "RA",
            "password": "userpwd",
        }
        form = UserForm(data, file_dict)
        self.assertTrue(form.is_valid())

    def test_user_form_invalid(self):
        form = UserForm(
            data={
                "email": "",
                "first_name": "hello",
                "address": "hyd",
                "permanent_address": "hyd",
                "mobile": "1234567890",
                "gender": "F",
                "last_name": "mp",
                "user_type": "",
                "password": "",
            }
        )
        self.assertFalse(form.is_valid())
