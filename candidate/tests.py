"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase

from .forms import *
from peeldb.models import *


class personalinfo_form_test(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="India")
        self.state = State.objects.create(name="Telangana", country_id=self.country.id)
        self.city = City.objects.create(name="hyderabad", state_id=self.state.id)

    def test_personalinfo_for_valid(self):
        form = PersonalInfoForm(
            data={
                "first_name": "mp",
                "last_name": "mp",
                "nationality": "indian",
                "address": "hyd",
                "permanent_address": "hyd",
                "mobile": "8977455970",
                "gender": "F",
                "pincode": "505301",
                "current_city": self.city.id,
                "preferred_city": self.city.id,
                "dob": "12/12/2222",
                "marital_status": "Single",
                "resume_title": "resume title",
                "user_id": 2,
            }
        )
        self.assertTrue(form.is_valid())

    def test_personalinfo_form_invalid(self):
        form = PersonalInfoForm(
            data={
                "first_name": "",
                "last_name": "",
                "nationality": "indian",
                "address": "hyd",
                "permanent_address": "hyd",
                "mobile": "8977455970",
                "gender": "",
                "pincode": "505301",
                "current_city": self.city.id,
                "prefered_city": self.city.id,
                "dob": "2015-07-24",
                "marital_status": "Single",
            }
        )
        self.assertFalse(form.is_valid())


class professionalinfo_form_test(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="India")
        self.state = State.objects.create(name="Telangana", country_id=self.country.id)
        self.city = City.objects.create(name="hyderabad", state_id=self.state.id)
        self.industry = Industry.objects.create(name="Software")

    def test_personalinfo_for_valid(self):
        form = ProfessinalInfoForm(
            data={
                "current_salary": "5000",
                "expected_salary": "5000",
                "relocation": "",
                "year": "2015",
                "month": "12",
                "notice_period": "3",
                "job_role": "developer",
                "prefered_industry": self.industry.id,
            }
        )
        self.assertTrue(form.is_valid())

    def test_personalinfo_form_invalid(self):
        form = ProfessinalInfoForm(
            data={
                "first_name": "",
                "last_name": "",
                "nationality": "indian",
                "address": "hyd",
                "permanent_address": "hyd",
                "mobile": "8977455970",
                "gender": "",
                "pincode": "505301",
                "current_city": self.city.id,
                "prefered_city": self.city.id,
                "dob": "2015-07-24",
                "marital_status": "Single",
            }
        )
        self.assertFalse(form.is_valid())


class profiledescription_form_test(TestCase):
    def test_profiledescription_for_valid(self):
        form = ProfileDescriptionForm(data={"profile_description": "hello"})
        self.assertTrue(form.is_valid())

    def test_profiledescription_form_invalid(self):
        form = ProfileDescriptionForm(data={"profile_description": ""})
        self.assertFalse(form.is_valid())


class WorkExperienceForm_form_test(TestCase):
    def test_experienceinfo_for_valid(self):
        form = WorkExperienceForm(
            data={
                "to_date": "11/07/2017",
                "company": "abc",
                "from_date": "11/08/2016",
                "designation": "developer",
                "salary": "5000",
                "current_job": "",
            }
        )
        self.assertTrue(form.is_valid())

    def test_experienceinfo_form_invalid(self):
        form = WorkExperienceForm(
            data={
                "to_date": "12/12/2222",
                "company": "",
                "from_date": "",
                "designation": "",
                "salary": "",
                "current_job": "",
            }
        )
        self.assertFalse(form.is_valid())


class EducationForm_form_test(TestCase):
    def test_educationinfo_for_valid(self):
        form = EducationForm(
            data={"from_date": "11/11/2011", "to_date": "11/12/2011", "score": "50"}
        )
        self.assertTrue(form.is_valid())

    def test_educationinfo_form_invalid(self):
        form = EducationForm(data={"from_date": "", "to_date": "", "score": ""})
        self.assertFalse(form.is_valid())


class DegreeForm_form_test(TestCase):
    def setUp(self):
        self.qualification = Qualification.objects.create(name="btech")

    def test_degreeinfo_for_valid(self):
        form = DegreeForm(
            data={
                "degree_name": self.qualification.id,
                "degree_type": "Permanent",
                "specialization": "special",
            }
        )
        self.assertTrue(form.is_valid())

    def test_degreeinfo_form_invalid(self):
        form = DegreeForm(
            data={"degree_name": "", "degree_type": "", "specialization": ""}
        )
        self.assertFalse(form.is_valid())


class EducationInstitueForm_form_test(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="India")
        self.state = State.objects.create(name="Telangana", country_id=self.country.id)
        self.city = City.objects.create(name="hyderabad", state_id=self.state.id)

    def test_educationinstituteinfo_for_valid(self):
        form = EducationInstitueForm(
            data={"name": "srinidhi", "address": "hyd", "city": self.city.id}
        )
        self.assertTrue(form.is_valid())

    def test_educationinstituteinfo_form_invalid(self):
        form = EducationInstitueForm(data={"name": "", "address": "", "city": ""})
        self.assertFalse(form.is_valid())


class ProjectForm_form_test(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="India")
        self.state = State.objects.create(name="Telangana", country_id=self.country.id)
        self.city = City.objects.create(name="hyderabad", state_id=self.state.id)
        self.skill = Skill.objects.create(name="Python")

    def test_projectinfo_for_valid(self):
        form = ProjectForm(
            data={
                "name": "mp",
                "from_date": "12/09/2011",
                "to_date": "11/10/2012",
                "description": "mp",
                "skills": [self.skill.id],
                "location": self.city.id,
                "role": "developer",
                "size": 5,
            }
        )
        self.assertTrue(form.is_valid())

    def test_projectinfo_form_invalid(self):
        form = ProjectForm(
            data={
                "name": "",
                "duration": "",
                "description": "",
                "skills": "",
                "location": "",
                "role": "",
                "size": "",
            }
        )
        self.assertFalse(form.is_valid())


class TechnicalSkillForm_form_test(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="India")
        self.state = State.objects.create(name="Telangana", country_id=self.country.id)
        self.city = City.objects.create(name="hyderabad", state_id=self.state.id)
        self.skill = Skill.objects.create(name="Python")

    def test_skillinfo_for_valid(self):
        form = TechnicalSkillForm(
            data={
                "skill": self.skill.id,
                "year": 2015,
                "month": 12,
                "last_used": "12/12/2015",
                "version": "1.1",
                "proficiency": "Good",
            }
        )
        self.assertTrue(form.is_valid())

    def test_skillinfo_form_invalid(self):
        form = TechnicalSkillForm(
            data={
                "skill": "",
                "year": "",
                "month": "",
                "last_used": "",
                "version": "",
                "proficiency": "",
            }
        )
        self.assertFalse(form.is_valid())


class JobAlertForm_form_test(TestCase):
    def setUp(self):
        self.skill = Skill.objects.create(name="Python")

    def test_job_alert_form_for_valid(self):
        form = JobAlertForm(
            data={
                "skill": [self.skill.id],
                "name": "testalert",
                "max_salary": "",
                "email": "r@gmail.com",
            }
        )
        self.assertTrue(form.is_valid())

    def test_job_alert_form_invalid(self):
        form = JobAlertForm(
            data={"skill": [self.skill.id], "name": "", "max_salary": ""}
        )
        self.assertFalse(form.is_valid())


class JobAlertEditForm_form_test(TestCase):
    def setUp(self):
        self.skill = Skill.objects.create(name="Python")

    def test_job_alert_edit_form_valid(self):
        form = JobAlertForm(
            data={
                "skill": [self.skill.id],
                "max_salary": "",
                "name": "testalert",
                "email": "r@gmail.com",
            }
        )
        self.assertTrue(form.is_valid())

    def test_job_alert_edit_form_invalid(self):
        form = JobAlertForm(data={"skill": "", "max_salary": ""})
        self.assertFalse(form.is_valid())


class applicant_get_views_test(TestCase):
    def setUp(self):
        self.applicant = User.objects.create(
            email="applicant@mp.com",
            username="applicant",
            user_type="JS",
            is_active=True,
            mobile_verified=True,
            registered_from="Email",
        )
        self.applicant.set_password("mp")
        self.applicant.save()

        self.company = Company.objects.create(
            name="testing", website="testingsite.com", is_active=True
        )
        self.new_recruiter = User.objects.create(
            email="new_recruiter@mp.com",
            username="new_recruiter",
            user_type="RR",
            is_active=True,
            mobile_verified=True,
            company=self.company,
            is_admin=True,
        )
        self.new_recruiter.set_password("mp")
        self.new_recruiter.save()

    def test_index(self):
        user_login = self.client.login(email="applicant@mp.com", password="mp")
        self.assertTrue(user_login)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_recruiter_index(self):
        user_login = self.client.login(email="new_recruiter@mp.com", password="mp")
        self.assertTrue(user_login)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
