from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
from django.urls import reverse
import json

from .forms import (
    JobPostForm,
    Company_Form,
    User_Form,
    ChangePasswordForm,
    PersonalInfoForm,
    MobileVerifyForm,
    MailTemplateForm,
    MenuForm,
    RecruiterForm,
    EditCompanyForm,
)
from peeldb.models import (
    User,
    Country,
    State,
    City,
    Skill,
    Qualification,
    Industry,
    FunctionalArea,
    JobPost,
    FacebookPost,
    Company,
    Menu,
    InterviewLocation,
    AgencyCompany,
    AgencyCompanyCatogery,
)


class job_post_form_test(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="micro_test")
        self.country = Country.objects.create(name="India")
        self.state = State.objects.create(name="Telangana", country_id=self.country.id)
        self.city = City.objects.create(name="hyderabad", state_id=self.state.id)
        self.industry = Industry.objects.create(name="Software")
        self.skill = Skill.objects.create(name="Python")
        self.functional_area = FunctionalArea.objects.create(name="functional_area")
        self.qualification = Qualification.objects.create(name="btech")
        upload_file = open("static/img/report.png", "rb")
        self.file_dict = SimpleUploadedFile(upload_file.name, upload_file.read())

    def test_job_post_for_valid(self):
        form = JobPostForm(
            data={
                "title": "java developer",
                "job_role": "developer",
                "functional_area": [self.functional_area.id],
                "vacancies": 1,
                "description": "swetha",
                "min_year": 1,
                "max_year": 1,
                "min_month": 2,
                "max_month": 2,
                "fresher": True,
                "edu_qualification": [self.qualification.id],
                "visa_required": True,
                "visa_country": self.country.id,
                "visa_type": "Permanent",
                "skills": [self.skill.id],
                "min_salary": 1000,
                "max_salary": 1200,
                "company_address": "abc",
                "company_name": "abc",
                "company_website": "http://abc.com",
                "company_logo": self.file_dict,
                "company_description": "abc",
                "last_date": "12/10/2024",
                "job_type": "Internship",
                "location": [self.city.id],
                "industry": [self.industry.id],
                "final_industry": "hello",
                "final_skills": "dcd",
                "final_functional_area": "fa",
                "final_edu_qualification": "dcs",
                "published_date": "12/10/2024 00:00:00",
                "salary_type": "Year",
                "published_message": "hellooo",
            },
            user=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_job_post_form_invalid(self):
        form = JobPostForm(
            data={
                "user": self.user.id,
                "job_role": "developer",
                "functional_area": self.functional_area.id,
                "vacancies": 1,
                "keywords": "",
                "description": "swetha",
                "min_year": 1,
                "max_year": 1,
                "min_month": 2,
                "max_month": 2,
                "qualification": [self.qualification.id],
                "fresher": True,
                "visa_required": True,
                "visa_country": self.country.id,
                "visa_type": "Permanent",
                "skills": [self.skill.id],
                "min_salary": 1000,
                "max_salary": 1200,
                "last_date": "2015-07-24",
                "posted_on": "2015-07-06 18:01:59.826458+05:30",
                "created_on": "2015-07-06 18:01:59.826458+05:30",
                "status": "Draft",
                "previous_status": "Draft",
                "post_on_fb": True,
                "post_on_ln": True,
                "post_on_tw": True,
                "fb_views": "10",
                "tw_views": "10",
                "ln_views": "10",
                "other_views": "10",
                "job_type": "Permanent",
                "location": [self.city.id],
                "industry": self.industry.id,
                "final_industry": "hello",
                "final_skills": "dcd",
                "final_functional_area": "fa",
                "final_edu_qualification": "dcs",
                "salary_type": "Year",
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())


class recruiter_Views_test(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="testuser@mp.com", password="test", is_active=True
        )
        self.country = Country.objects.create(name="India")
        self.state = State.objects.create(name="Telangana", country_id=self.country.id)
        self.city = City.objects.create(name="hyderabad", state_id=self.state.id)
        self.industry = Industry.objects.create(name="Software")
        self.skill = Skill.objects.create(name="Python")
        self.functional_area = FunctionalArea.objects.create(name="functional_area")
        self.qualification = Qualification.objects.create(name="btech")


class company_form_test(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="micro_test")

    def test_company_for_valid(self):
        form = Company_Form(
            data={
                "name": "company123",
                "email": "company123@gmail.com",
                "short_code": "comp123",
                "website": "https://micropyramid.com",
                "phone_number": "9876543210",
                "company_type": "Company",
            }
        )
        self.assertTrue(form.is_valid())

    def test_company_form_invalid(self):
        form = Company_Form(
            data={
                "name": "",
                "email": "company123@gmail.com",
                "short_code": "comp123",
                "website": "",
                "phone_number": "",
            }
        )
        self.assertFalse(form.is_valid())


class user_form_test(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="micro_test")

    def test_company_for_valid(self):
        form = User_Form(
            data={
                "password": "Mp1234@",
                "email": "company123@gmail.com",
                "mobile": "9876543210",
                "client_type": "Consultant",
                "username": "myname",
            }
        )
        self.assertTrue(form.is_valid())

    def test_company_form_invalid(self):
        form = User_Form(
            data={
                "password": "Mp1234@",
                "email": "company123@gmail.com",
                "mobile": "987654321",
            }
        )
        self.assertFalse(form.is_valid())

        form = User_Form(
            data={"password": "Mp1234@", "email": "company123@gmail.com", "mobile": ""}
        )
        self.assertFalse(form.is_valid())


class change_password_form_test(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="micro_test")
        self.user.set_password("mp")
        self.user.save()

    def test_change_password_for_valid(self):
        form = ChangePasswordForm(
            data={
                "oldpassword": "mp",
                "newpassword": "mp123",
                "retypepassword": "mp123",
            },
            user=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_change_password_form_invalid(self):
        form = ChangePasswordForm(
            data={"oldpassword": "mp", "newpassword": "mp123", "retypepassword": ""},
            user=self.user,
        )
        self.assertFalse(form.is_valid())


class personal_info_form_test(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="micro_test")
        self.country = Country.objects.create(name="India")
        self.state = State.objects.create(name="Telangana", country_id=self.country.id)
        self.city = City.objects.create(name="hyderabad", state_id=self.state.id)
        self.industry = Industry.objects.create(name="Software")
        self.skill = Skill.objects.create(name="Python")
        self.functional_area = FunctionalArea.objects.create(name="functional_area")
        self.qualification = Qualification.objects.create(name="btech")

    def test_personal_info_for_valid(self):
        upload_file = open("static/img/report.png", "rb")
        file_dict = {
            "profile_pic": SimpleUploadedFile(upload_file.name, upload_file.read())
        }
        data = {
            "username": "mp",
            "first_name": "micropyramid",
            "last_name": "mp",
            "name": "micro",
            "city": self.city.id,
            "state": self.state.id,
            "country": self.country.id,
            "industry": [self.industry.id],
            "functional_area": [self.functional_area.id],
            "technical_skills": [self.skill.id],
            "nationality": self.country.id,
            "year": "2016",
            "month": "06",
            "profile_description": "hello",
            "job_role": "developer",
            "mobile": "9876543210",
            "company_type": "general",
            "user_id": self.user.id,
        }
        form = PersonalInfoForm(data, file_dict)
        self.assertTrue(form.is_valid())

    def test_personal_info_form_invalid(self):
        form = PersonalInfoForm(
            data={
                "username": "mp",
                "first_name": "micropyramid",
                "last_name": "mp",
                "name": "micro",
                "city": self.city.id,
                "state": self.state.id,
                "country": self.country.id,
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "technical_skills": [self.skill.id],
                "nationality": self.country.id,
                "year": "2016",
                "month": "06",
                "profile_description": "hello",
                "job_role": "developer",
                "mobile": "901074",
                "user_id": self.user.id,
            }
        )
        self.assertFalse(form.is_valid())


class mobile_verify_form_test(TestCase):
    def test_change_password_for_valid(self):
        form = MobileVerifyForm(data={"mobile_verification_code": "mp"})
        self.assertTrue(form.is_valid())

    def test_change_password_form_invalid(self):
        form = MobileVerifyForm(data={"mobile_verification_code": ""})
        self.assertFalse(form.is_valid())


class mail_template_form_test(TestCase):
    def test_mail_template_for_valid(self):
        form = MailTemplateForm(
            data={"subject": "mp", "message": "message", "title": "title"}
        )
        self.assertTrue(form.is_valid())

    def test_mail_template_form_invalid(self):
        form = MailTemplateForm(
            data={"subject": "mp", "message": "message", "title": ""}
        )
        self.assertFalse(form.is_valid())


class menu_form_test(TestCase):
    def test_menu_form_for_valid(self):
        form = MenuForm(data={"title": "mp", "url": "https://micropyramid.com"})
        self.assertTrue(form.is_valid())

    def test_menu_form_invalid(self):
        form = MenuForm(data={"title": "", "url": ""})
        self.assertFalse(form.is_valid())


class recruiter_form_test(TestCase):
    def test_recruiter_form_for_valid(self):
        form = RecruiterForm(
            data={
                "mobile": "8977455970",
                "email": "nikhila@micropyramid.com",
                "job_role": "developer",
                "first_name": "nikhila",
                "password": "Mp1234@",
            }
        )
        self.assertTrue(form.is_valid())

    def test_recruiter_form_for_valid_data(self):
        form = RecruiterForm(
            data={
                "mobile": "9101010747",
                "email": "nikhila@micropyramid.com",
                "job_role": "developer",
                "first_name": "nikhila",
                "password": "Mp1234@",
            }
        )
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_recruiter_form_invalid(self):
        form = RecruiterForm(
            data={
                "mobile": "12345",
                "email": "",
                "job_role": "",
                "profile_pic": "",
                "first_name": "",
            }
        )
        self.assertFalse(form.is_valid())


class edit_companyform_test(TestCase):
    def test_edit_company_form_for_valid(self):
        form = EditCompanyForm(
            data={
                "name": "testingcompany",
                "company_type": "Company",
                "website": "https://testingcompany.com",
                "profile": "testingcompany",
                "address": "hyd",
                "level": "1",
            }
        )
        self.assertTrue(form.is_valid())

    def test_edit_company_form_for_valid_data(self):
        form = EditCompanyForm(
            data={
                "name": "testingcompany",
                "company_type": "Company",
                "website": "https://testingcompany.com",
                "profile": "",
                "address": "",
                "level": "",
            }
        )
        self.assertFalse(form.is_valid())

    def test_edit_company_form_invalid(self):
        form = EditCompanyForm(
            data={
                "name": "testingcompany",
                "company_type": "Company",
                "website": "https://testingcompany.com",
                "profile": "",
                "address": "",
                "level": "",
            }
        )
        self.assertFalse(form.is_valid())


class recruiter_get_views_test(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="testing",
            website="testingsite.com",
            is_active=True,
            company_type="Consultant",
        )
        self.recruiter = User.objects.create(
            email="recruiter@mp.com",
            username="recruiter",
            user_type="AA",
            is_active=True,
            mobile_verified=True,
            company=self.company,
            is_admin=True,
            agency_admin=True,
        )
        self.recruiter.set_password("mp")
        self.recruiter.save()
        self.recruiter_mobile_not_verified = User.objects.create(
            email="recruiter_mobile@mp.com",
            username="recruiter_mobile",
            user_type="RR",
            is_active=True,
            mobile_verified=False,
            mobile_verification_code="123456",
            company=self.company,
        )
        self.inactive_recruiter = User.objects.create(
            email="inactive_recruiter@mp.com",
            username="inactive_recruiter",
            user_type="RR",
            is_active=True,
            mobile_verified=False,
            mobile_verification_code="123456",
            company=self.company,
        )

        self.recruiter_mobile_not_verified.set_password("mp")
        self.recruiter_mobile_not_verified.save()
        self.inactive_recruiter.set_password("mp")
        self.inactive_recruiter.save()

        self.company_recruiter = User.objects.create(
            email="testing@mp.com",
            username="testing",
            user_type="RR",
            company=self.company,
            is_active=True,
            mobile_verified=True,
        )
        self.company_recruiter.set_password("mp")
        self.company_recruiter.save()

        self.country = Country.objects.create(name="India")
        self.agency_company = AgencyCompany.objects.create(
            name="testing",
            website="testing.com",
            decription="hello",
            company=self.company,
            created_by=self.recruiter,
        )
        self.agency_category = AgencyCompanyCatogery.objects.create(
            name="junior", percantage="1"
        )

        self.state = State.objects.create(name="Telangana", country_id=self.country.id)
        self.city = City.objects.create(name="hyderabad", state_id=self.state.id)
        self.industry = Industry.objects.create(name="Software")
        self.skill = Skill.objects.create(name="Python")
        self.functional_area = FunctionalArea.objects.create(name="functional_area")
        self.qualification = Qualification.objects.create(name="btech")
        self.current_date = datetime.strptime(
            str(datetime.now().date()), "%Y-%m-%d"
        ).strftime("%m/%d/%Y")

        self.walk_in_from_date = "06/24/2016"

        self.walk_in_to_date = "06/24/2026"

        for each in range(0, 15):
            self.jobpost = JobPost.objects.create(
                user=self.recruiter,
                title="test-jobpost_" + str(each),
                vacancies="6",
                description="job post description",
                job_type="Full_Time",
                status="Draft",
                published_message="test message",
                company_address="company address",
                company_description="company description",
                last_date="2016-09-09",
            )
            self.interview_location = InterviewLocation.objects.create(
                venue_details="hyderabad, India",
                latitude="14.8976",
                longitude="21.0967",
            )
            self.jobpost.job_interview_location.add(self.interview_location)
            self.jobpost.skills.add(self.skill)
            self.jobpost.industry.add(self.industry)
            self.jobpost.functional_area.add(self.functional_area)
            self.jobpost.location.add(self.city)
            FacebookPost.objects.create(
                job_post=self.jobpost,
                page_or_group="Page",
                page_or_group_id="1305678",
                post_id="8764567",
                post_status="Posted",
            )
            FacebookPost.objects.create(
                job_post=self.jobpost,
                page_or_group="Group",
                page_or_group_id="1305678",
                post_id="8764567",
                post_status="Posted",
            )
            # TwitterPost.objects.create(job_post=self.jobpost, page_or_profile='Profile', post_id='126789', post_status='Posted')
        self.other_edu = ['[{"other_edu_qualification_1":"h"}]']
        self.fa = ['[{"other_functional_area_1":"ot"}]']
        self.other_ind = ['[{"other_industry_name_1":"hello industry"}]']
        self.other_skill = ['[{"other_skill_name_1":"test skill"}]']
        upload_file = open("static/img/report.png", "rb")
        self.file_dict = SimpleUploadedFile(upload_file.name, upload_file.read())

    def test_views_with_employee(self):
        response = self.client.get(
            reverse("recruiter:account_activation", kwargs={"user_id": "100"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "recruiter/recruiter_404.html")

    def test_views_with_employee_login(self):
        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)

        response = self.client.get("/recruiter/")
        self.assertEqual(response.status_code, 302)

        response = self.client.get("/recruiter/job/list/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/job/list.html")

        response = self.client.get("/recruiter/job/list/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/job/list.html")

        response = self.client.get(reverse("recruiter:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/user/profile.html")

        response = self.client.get("/recruiter/job/full-time/new/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/recruiter/job/full-time/new/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/recruiter/job/internship/new/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/job/new.html")

        response = self.client.get("/recruiter/job/walk-in/new/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/job/new.html")

        response = self.client.get("/recruiter/change-password/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/user/change_password.html")

        response = self.client.get("/recruiter/thank-you-message/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/registration_success.html")

        response = self.client.get("/recruiter/how-it-works/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/how_it_works.html")

        response = self.client.post(
            "/recruiter/job/full-time/new/",
            data={
                "title": "test-job-post",
                "job_type": "full-time",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "salary_type": "Year",
                "min_salary": "123",
                "max_salary": "1234",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": ['[{"other_industry_name_1":"h"}]'],
                "final_skills": ['[{"other_skill_name_1":"test"}]'],
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "published_message": "hellooo",
            },
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/recruiter/job/full-time/new/",
            data={
                "title": "",
                "job_type": "full-time",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "salary_type": "Year",
                "min_salary": "1",
                "max_salary": "22",
                "no_of_interview_location": "0",
                "published_message": "hellooo",
            },
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/recruiter/job/full-time/new/",
            data={
                "title": "",
                "job_type": "full-time",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "salary_type": "Year",
                "min_salary": "1",
                "max_salary": "3",
                "published_message": "hellooo",
            },
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/recruiter/job/full-time/new/",
            data={
                "title": "",
                "job_type": "full-time",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "2",
                "final_location_1": ["[13.1543, 77.783]"],
                "final_location_2": [""],
                "venue_details_2": [""],
                "venue_details_1": "mp",
                "show_location_1": "False",
                "show_location_2": "True",
                "salary_type": "Year",
                "min_salary": "1",
                "max_salary": "22",
                "published_message": "hellooo",
            },
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/recruiter/job/full-time/new/",
            data={
                "title": "test-job-post",
                "job_type": "full-time",
                "status": "Draft",
                "vacancies": "1",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "0",
                "max_year": "1",
                "salary_type": "Year",
                "min_salary": "1",
                "max_salary": "22",
                "published_message": "hellooo",
            },
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/recruiter/job/full-time/new/",
            data={
                "title": "test-job-post",
                "job_type": "full-time",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "1",
                "max_year": "0",
                "salary_type": "Year",
                "min_salary": "1",
                "max_salary": "22",
                "published_message": "hellooo",
            },
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/recruiter/job/full-time/new/",
            data={
                "title": "test-job-post",
                "job_type": "full-time",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "1",
                "max_year": "0",
                "visa_required": ["True"],
                "salary_type": "Year",
                "min_salary": "1",
                "max_salary": "22",
                "published_message": "hellooo",
            },
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/recruiter/job/full-time/new/",
            data={
                "title": "test-job-post",
                "job_type": "full-time",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "1",
                "max_year": "0",
                "visa_required": ["True"],
                "visa_country": ["1"],
                "visa_type": ["hello"],
                "published_message": "hellooo",
                "salary_type": "Year",
            },
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/recruiter/job/full-time/new/",
            data={
                "title": "test-job-post",
                "job_type": "full-time",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "salary_type": "Month",
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "1",
                "max_year": "0",
                "visa_required": ["True"],
                "visa_country": ["1"],
                "visa_type": ["hello"],
                "published_message": "hellooo",
            },
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/recruiter/job/full-time/new/",
            data={
                "title": "new-test-job-post",
                "job_type": "Walk-in",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": "10/10/2016",
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "1",
                "max_year": "0",
                "visa_required": ["True"],
                "visa_country": self.country.id,
                "country": self.country.id,
                "visa_type": ["hello"],
                "code": "code",
                "job_role": "developer",
                "min_month": "1",
                "max_month": "2",
                "company_name": "micro",
                "company_website": "http://abc.com",
                "company_logo": self.file_dict,
                "published_date": "06/23/2018 13:36:28",
                "keywords": ["key1", "key2"],
                "walkin_from_date": self.walk_in_from_date,
                "walkin_to_date": self.walk_in_to_date,
                "walkin_time": "00:00",
                "walkin_contactinfo": "hyderabad, india",
                "salary_type": "Year",
                "min_salary": "1000",
                "published_message": "hellooo",
                "max_salary": "2000",
                "agency_amount": "10000",
                "agency_client": self.agency_company.id,
                "agency_category": self.agency_category.id,
                "agency_invoice_type": "Recurring",
                "agency_job_type": "Permanent",
                "agency_recruiters": [self.recruiter.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        # error_data = json.loads(str(response.content, encoding='utf-8'))

        response = self.client.post(
            "/recruiter/job/full-time/new/",
            data={
                "title": "new-test-job-post",
                "job_type": "Walk-in",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": "10/10/2016",
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "1",
                "max_year": "0",
                "visa_required": ["True"],
                "visa_country": self.country.id,
                "country": self.country.id,
                "visa_type": ["hello"],
                "code": "code",
                "job_role": "developer",
                "min_month": "1",
                "max_month": "2",
                "company_name": "micro",
                "company_website": "http://abc.com",
                "company_logo": self.file_dict,
                "published_date": "06/23/2018 13:36:28",
                "keywords": ["key1", "key2"],
                "walkin_from_date": self.walk_in_from_date,
                "walkin_to_date": self.walk_in_to_date,
                "walkin_time": "00:00",
                "walkin_contactinfo": "hyderabad, india",
                "salary_type": "Year",
                "min_salary": "1000",
                "max_salary": "2000",
                "agency_amount": "10000",
                "published_message": "hellooo",
                "agency_client": self.agency_company.id,
                "agency_category": self.agency_category.id,
                "agency_invoice_type": "Recurring",
                "agency_job_type": "Permanent",
                "agency_recruiters": [self.recruiter.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        # error_data = json.loads(str(response.content, encoding='utf-8'))

        response = self.client.post(
            "/recruiter/job/full-time/new/",
            data={
                "title": "new-test-job-post",
                "job_type": "Walk-in",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": "10/10/2016",
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "1",
                "max_year": "0",
                "visa_required": ["True"],
                "visa_country": self.country.id,
                "country": self.country.id,
                "visa_type": ["hello"],
                "code": "code",
                "job_role": "developer",
                "min_month": "1",
                "max_month": "2",
                "company_name": "micro",
                "company_website": "http://abc.com",
                "company_logo": self.file_dict,
                "published_date": "06/23/2018 13:36:28",
                "keywords": ["key1", "key2"],
                "walkin_from_date": self.walk_in_from_date,
                "walkin_to_date": self.walk_in_to_date,
                "walkin_time": "00:00",
                "walkin_contactinfo": "hyderabad, india",
                "salary_type": "Year",
                "min_salary": "1000",
                "max_salary": "2000",
                "agency_amount": "10000",
                "agency_client": self.agency_company.id,
                "agency_category": self.agency_category.id,
                "agency_invoice_type": "Recurring",
                "agency_job_type": "Permanent",
                "published_message": "hellooo",
                "agency_recruiters": [self.recruiter.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        # error_data = json.loads(str(response.content, encoding='utf-8'))

    def test_new_job_with_mobile_not_verified(self):
        user_login = self.client.login(email="recruiter_mobile@mp.com", password="mp")
        self.assertTrue(user_login)

        response = self.client.get("/recruiter/job/full-time/new/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "recruiter/recruiter_404.html")

    def test_edit_job_with_mobile_not_verified(self):
        user_login = self.client.login(email="recruiter_mobile@mp.com", password="mp")
        self.assertTrue(user_login)

        response = self.client.get(
            reverse("recruiter:edit", kwargs={"job_post_id": "1"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "recruiter/recruiter_404.html")

    def test_edit_job_with_mobile_verified(self):
        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)
        self.job_post = JobPost.objects.all()
        self.job_post_id = self.job_post.first().id
        self.edit_url = reverse(
            "recruiter:edit", kwargs={"job_post_id": self.job_post.first().id}
        )

        response = self.client.get(
            reverse("recruiter:edit", kwargs={"job_post_id": "250"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "recruiter/recruiter_404.html")

        response = self.client.get(
            reverse("recruiter:edit", kwargs={"job_post_id": self.job_post.first().id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/job/edit.html")

        response = self.client.post(
            self.edit_url,
            data={
                "title": "test-job-post",
                "job_type": "full-time",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "1",
                "max_year": "0",
                "visa_required": ["True"],
                "visa_country": ["self.country.id"],
                "visa_type": ["hello"],
                "code": "code",
                "job_role": "developer",
                "min_month": "2",
                "max_month": "1",
                "company_name": "micro",
                "company_website": "http://abc.com",
                "company_logo": self.file_dict,
                "published_date": "06/23/2018 13:36:28",
                "min_salary": "1000",
                "max_salary": "2000",
                "agency_amount": "10000",
                "agency_client": self.agency_company.id,
                "agency_category": self.agency_category.id,
                "agency_invoice_type": "Recurring",
                "agency_job_type": "Permanent",
                "agency_recruiters": [self.recruiter.id],
                "salary_type": "Year",
                "published_message": "hellooo",
            },
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {
            "error": True,
            "response": {
                "visa_country": [
                    "Select a valid choice. That choice is not one of the available choices."
                ]
            },
        }
        self.assertEqual(error_data, expected_errors)

        response = self.client.post(
            self.edit_url,
            data={
                "title": "test-job-post",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "min_year": "0",
                "max_year": "1",
                "visa_required": ["True"],
                "visa_country": self.country.id,
                "country": self.country.id,
                "visa_type": ["hello"],
                "job_type": "full-time",
                "code": "code",
                "job_role": "developer",
                "min_month": "1",
                "max_month": "2",
                "company_name": "micro",
                "company_website": "http://abc.com",
                "published_date": "06/23/2018 13:36:28",
                "keywords": ["key1", "key2"],
                "min_salary": "1000",
                "max_salary": "2000",
                "no_of_interview_location": "2",
                "final_location_1": ["[13.1543, 77.783]"],
                "final_location_2": ["[13.1543, 77.783]"],
                "venue_details_2": "hyd",
                "venue_details_1": "mp",
                "show_location_1": "False",
                "salary_type": "Year",
                "show_location_2": "True",
                "agency_amount": "10000",
                "agency_client": self.agency_company.id,
                "agency_category": self.agency_category.id,
                "agency_invoice_type": "Recurring",
                "agency_job_type": "Permanent",
                "agency_recruiters": [self.recruiter.id],
                "published_message": "hellooo",
            },
        )

        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        self.assertEqual(error_data["response"], "Jobpost Updated Successfully")

        response = self.client.post(
            self.edit_url,
            data={
                "title": "test-job-post",
                "job_type": "Walk-in",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "1",
                "max_year": "0",
                "visa_required": ["True"],
                "visa_country": self.country.id,
                "country": self.country.id,
                "visa_type": ["hello"],
                "code": "code",
                "job_role": "developer",
                "min_month": "1",
                "max_month": "2",
                "company_name": "micro",
                "company_website": "http://abc.com",
                "published_date": "06/23/2018 13:36:28",
                "keywords": ["key1", "key2"],
                "walkin_from_date": self.walk_in_from_date,
                "walkin_to_date": self.walk_in_to_date,
                "walkin_time": "00:00",
                "walkin_contactinfo": "hyderabad, india",
                "salary_type": "Year",
                "min_salary": "1000",
                "max_salary": "2000",
                "agency_amount": "10000",
                "agency_client": self.agency_company.id,
                "agency_category": self.agency_category.id,
                "agency_invoice_type": "Recurring",
                "agency_job_type": "Permanent",
                "agency_recruiters": [self.recruiter.id],
                "published_message": "hellooo",
            },
        )

        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        self.assertEqual(error_data["response"], "Jobpost Updated Successfully")

        response = self.client.post(
            self.edit_url,
            data={
                "title": "test-job-post",
                "job_type": "Walk-in",
                "status": "Pending",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "edu_qualification": [self.qualification.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "0",
                "max_year": "1",
                "visa_required": ["True"],
                "visa_country": self.country.id,
                "country": self.country.id,
                "visa_type": ["hello"],
                "code": "code",
                "job_role": "developer",
                "min_month": "1",
                "max_month": "2",
                "company_name": "micro",
                "company_website": "http://abc.com",
                "published_date": "06/23/2018 13:36:28",
                "keywords": ["key1", "key2"],
                "walkin_from_date": self.walk_in_from_date,
                "walkin_to_date": self.walk_in_to_date,
                "walkin_time": "00:00",
                "walkin_contactinfo": "hyderabad, india",
                "salary_type": "Year",
                "min_salary": "1",
                "max_salary": "3",
                "fb_post": "on",
                "tw_post": "on",
                "ln_post": "on",
                "agency_amount": "10000",
                "agency_client": self.agency_company.id,
                "agency_category": self.agency_category.id,
                "agency_invoice_type": "Recurring",
                "agency_job_type": "Permanent",
                "agency_recruiters": [self.recruiter.id],
                "published_message": "hellooo",
            },
        )

        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        self.assertEqual(error_data["response"], "Jobpost Updated Successfully")

        response = self.client.post(
            self.edit_url,
            data={
                "title": "test-job-post",
                "job_type": "Internship",
                "status": "Pending",
                "vacancies": "1",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "0",
                "max_year": "1",
                "visa_required": ["True"],
                "visa_country": self.country.id,
                "country": self.country.id,
                "visa_type": ["hello"],
                "code": "code",
                "job_role": "developer",
                "min_month": "1",
                "max_month": "2",
                "company_name": "micro",
                "company_website": "http://abc.com",
                "published_date": "06/23/2018 13:36:28",
                "keywords": ["key1", "key2"],
                "walkin_from_date": self.walk_in_from_date,
                "walkin_to_date": self.walk_in_to_date,
                "walkin_time": "00:00",
                "walkin_contactinfo": "hyderabad, india",
                "min_salary": "1000",
                "max_salary": "2000",
                "salary_type": "Month",
                "fb_post": "on",
                "tw_post": "on",
                "ln_post": "on",
                "agency_amount": "10000",
                "agency_client": self.agency_company.id,
                "agency_category": self.agency_category.id,
                "agency_invoice_type": "Recurring",
                "agency_job_type": "Permanent",
                "agency_recruiters": [self.recruiter.id],
                "published_message": "hellooo",
            },
        )

        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        self.assertEqual(error_data["response"], "Jobpost Updated Successfully")

    def test_view_job(self):
        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)
        self.job_post = JobPost.objects.all()

        response = self.client.get(
            reverse("recruiter:view", kwargs={"job_post_id": self.job_post.first().id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/job/view.html")

        response = self.client.get(
            reverse("recruiter:view", kwargs={"job_post_id": "100"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "recruiter/recruiter_404.html")

        response = self.client.get(
            reverse(
                "recruiter:preview",
                kwargs={"job_post_id": self.job_post.filter(status="Draft").first().id},
            )
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.get(
            reverse("recruiter:preview", kwargs={"job_post_id": "100"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "recruiter/recruiter_404.html")

        response = self.client.get(
            reverse(
                "recruiter:deactivate_job",
                kwargs={"job_post_id": self.job_post.first().id},
            )
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        self.assertEqual(error_data["response"], "Job Post Deactivated")

        response = self.client.get(
            reverse(
                "recruiter:enable", kwargs={"job_post_id": self.job_post.first().id}
            )
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        self.assertEqual(error_data["response"], "Job Post enabled Successfully")

        response = self.client.get(
            reverse("recruiter:delete", kwargs={"job_post_id": self.job_post.last().id})
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        self.assertEqual(error_data["response"], "Job Post deleted Successfully")

    def test_copy_job(self):
        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)
        self.job_post = JobPost.objects.filter()
        self.job_post_id = self.job_post.first().id
        self.url = (
            reverse("recruiter:copy", kwargs={"status": "full_time"})
            + "?jobpost_id="
            + str(self.job_post_id)
        )

        response = self.client.get(
            reverse("recruiter:copy", kwargs={"status": "full_time"})
            + "?jobpost_id="
            + str(100)
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "recruiter/recruiter_404.html")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/job/copy.html")

        response = self.client.post(
            self.url,
            data={
                "title": "test-job-post",
                "status": "Draft",
                "vacancies": "",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "1",
                "max_year": "0",
                "visa_required": ["True"],
                "visa_country": ["self.country.id"],
                "visa_type": ["hello"],
                "job_type": "full-time",
                "code": "code",
                "job_role": "developer",
                "min_month": "2",
                "max_month": "1",
                "company_name": "micro",
                "company_website": "http://abc.com",
                "published_date": "06/23/2018 13:36:28",
                "min_salary": "1000",
                "max_salary": "2000",
                "agency_amount": "10000",
                "agency_client": self.agency_company.id,
                "agency_category": self.agency_category.id,
                "agency_invoice_type": "Recurring",
                "agency_job_type": "Permanent",
                "agency_recruiters": [self.recruiter.id],
                "salary_type": "Year",
                "published_message": "hellooo",
            },
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {
            "error": True,
            "response": {
                "visa_country": [
                    "Select a valid choice. That choice is not one of the available choices."
                ]
            },
        }
        self.assertEqual(error_data, expected_errors)

        response = self.client.post(
            self.url,
            data={
                "title": "test-job-post",
                "status": "Draft",
                "vacancies": "9",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "min_year": "0",
                "max_year": "1",
                "visa_required": ["True"],
                "visa_country": self.country.id,
                "country": self.country.id,
                "visa_type": ["hello"],
                "job_type": "full-time",
                "code": "code",
                "job_role": "developer",
                "min_month": "1",
                "max_month": "2",
                "company_name": "micro",
                "company_website": "http://abc.com",
                "published_date": "06/23/2018 13:36:28",
                "keywords": ["key1", "key2"],
                "min_salary": "1000",
                "max_salary": "2000",
                "no_of_interview_location": "2",
                "final_location_1": ["[13.1543, 77.783]"],
                "final_location_2": ["[13.1543, 77.783]"],
                "venue_details_2": "hyd",
                "venue_details_1": "mp",
                "show_location_1": "False",
                "salary_type": "Year",
                "show_location_2": "True",
                "agency_amount": "10000",
                "agency_client": self.agency_company.id,
                "agency_category": self.agency_category.id,
                "agency_invoice_type": "Recurring",
                "agency_job_type": "Permanent",
                "agency_recruiters": [self.recruiter.id],
                "published_message": "hellooo",
            },
        )

        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        self.assertEqual(error_data["response"], "Job Post Created Successfully")

        response = self.client.post(
            self.url,
            data={
                "title": "new-copy-test-job-post",
                "job_type": "Walk-in",
                "status": "Draft",
                "vacancies": "9",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "1",
                "max_year": "0",
                "visa_required": ["True"],
                "visa_country": self.country.id,
                "country": self.country.id,
                "visa_type": ["hello"],
                "code": "code",
                "job_role": "developer",
                "min_month": "1",
                "max_month": "2",
                "company_name": "micro",
                "company_website": "http://abc.com",
                "published_date": "06/23/2018 13:36:28",
                "keywords": ["key1", "key2"],
                "walkin_from_date": self.walk_in_from_date,
                "walkin_to_date": self.walk_in_to_date,
                "walkin_time": "00:00",
                "walkin_contactinfo": "hyderabad, india",
                "salary_type": "Year",
                "min_salary": "1000",
                "max_salary": "2000",
                "agency_amount": "10000",
                "agency_client": self.agency_company.id,
                "agency_category": self.agency_category.id,
                "agency_invoice_type": "Recurring",
                "agency_job_type": "Permanent",
                "agency_recruiters": [self.recruiter.id],
                "published_message": "hellooo",
            },
        )

        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        self.assertEqual(error_data["response"], "Job Post Created Successfully")

        response = self.client.post(
            self.url,
            data={
                "title": "my-copy-test-job-post",
                "job_type": "Walk-in",
                "status": "Pending",
                "vacancies": "7",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "edu_qualification": [self.qualification.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "0",
                "max_year": "1",
                "visa_required": ["True"],
                "visa_country": self.country.id,
                # 'country': self.country.id,
                "visa_type": ["hello"],
                "code": "code",
                "job_role": "developer",
                "min_month": "1",
                "max_month": "2",
                "company_name": "micro",
                "company_website": "http://abc.com",
                "published_date": "06/23/2018 13:36:28",
                "keywords": ["key1", "key2"],
                "walkin_from_date": self.walk_in_from_date,
                "walkin_to_date": self.walk_in_to_date,
                "walkin_time": "00:00",
                "walkin_contactinfo": "hyderabad, india",
                "salary_type": "Year",
                "min_salary": "1",
                "max_salary": "3",
                "fb_post": "on",
                "tw_post": "on",
                "ln_post": "on",
                "agency_amount": "10000",
                "agency_client": self.agency_company.id,
                "agency_category": self.agency_category.id,
                "agency_invoice_type": "Recurring",
                "agency_job_type": "Permanent",
                "agency_recruiters": [self.recruiter.id],
                "published_message": "hellooo",
            },
        )

        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        self.assertEqual(error_data["response"], "Job Post Created Successfully")

        response = self.client.post(
            self.url,
            data={
                "title": "copy-test-job-post",
                "job_type": "Internship",
                "status": "Pending",
                "vacancies": "1",
                "description": "job post description",
                "published_message": "test message",
                "company_address": "company address",
                "company_description": "company description",
                "last_date": self.current_date,
                "skills": [self.skill.id],
                "location": [self.city.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "final_industry": self.other_ind,
                "final_skills": self.other_skill,
                "final_edu_qualification": self.other_edu,
                "final_functional_area": self.fa,
                "no_of_interview_location": "0",
                "min_year": "0",
                "max_year": "1",
                "visa_required": ["True"],
                "visa_country": self.country.id,
                # 'country': self.country.id,
                "visa_type": ["hello"],
                "code": "code",
                "job_role": "developer",
                "min_month": "1",
                "max_month": "2",
                "company_name": "micro",
                "company_website": "http://abc.com",
                "published_date": "06/23/2018 13:36:28",
                "keywords": ["key1", "key2"],
                "walkin_from_date": self.walk_in_from_date,
                "walkin_to_date": self.walk_in_to_date,
                "walkin_time": "00:00",
                "walkin_contactinfo": "hyderabad, india",
                "min_salary": "1000",
                "max_salary": "2000",
                "salary_type": "Year",
                "fb_post": "on",
                "tw_post": "on",
                "ln_post": "on",
                "agency_amount": "10000",
                "agency_client": self.agency_company.id,
                "agency_category": self.agency_category.id,
                "agency_invoice_type": "Recurring",
                "agency_job_type": "Permanent",
                "agency_recruiters": [self.recruiter.id],
                "published_message": "hellooo",
            },
        )

        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        self.assertEqual(error_data["response"], "Job Post Created Successfully")

    # def test_send_mobile_verification_code(self):
    #     user_login = self.client.login(email='recruiter@mp.com', password='mp')
    #     self.assertTrue(user_login)
    #     self.url = reverse('recruiter:send_mobile_verification_code')

    #     response = self.client.post(self.url, {'': ''})
    #     self.assertEqual(response.status_code, 302)
    #     error_data = json.loads(str(response.content, encoding='utf-8'))
    #     expected_errors = {
    #         'message': 'OTP Already sent to you, Please request new OTP', 'error': True}
    #     self.assertEqual(error_data, expected_errors)

    def test_change_password(self):
        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)
        self.url = reverse("recruiter:change_password")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/user/change_password.html")

        response = self.client.post(
            self.url,
            {"oldpassword": "mp", "newpassword": "pwd", "retypepassword": "pwd"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            str("Password changed successfully") in response.content.decode("utf8")
        )

        user_login = self.client.login(email="recruiter@mp.com", password="pwd")

        response = self.client.post(
            self.url,
            {"oldpassword": "micro123", "newpassword": "mp", "retypepassword": "mp"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            str("Password changed successfully") in response.content.decode("utf8")
        )

        response = self.client.post(
            self.url,
            {"oldpassword": "pwd", "newpassword": "micro123", "retypepassword": "mp"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            str("Password changed successfully") in response.content.decode("utf8")
        )

        response = self.client.post(
            self.url, {"newpassword": "pwd", "retypepassword": "pwd"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            str("Password changed successfully") in response.content.decode("utf8")
        )

        response = self.client.post(
            self.url,
            {"oldpassword": "pwd", "newpassword": "mp", "retypepassword": "mp"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            str("Password changed successfully") in response.content.decode("utf8")
        )

    def test_user_password_reset(self):
        self.url = reverse("recruiter:user_password_reset")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {"error": True, "email": "Method is not supported"}
        self.assertEqual(error_data, expected_errors)

        response = self.client.post(self.url, {"email": "recruiter@mp.com"})
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {
            "error": False,
            "info": "Sent a link to your email, reset your password by clicking that link",
        }
        self.assertEqual(error_data, expected_errors)

        response = self.client.post(self.url, {"email": "new_recruiter@mp.com"})
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {
            "error": True,
            "email": "User With this Email ID not Registered",
        }
        self.assertEqual(error_data, expected_errors)

    def test_verify_mobile(self):
        user_login = self.client.login(email="recruiter_mobile@mp.com", password="mp")
        self.assertTrue(user_login)
        self.url = reverse("recruiter:verify_mobile")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/user/mobile_verify.html")

        response = self.client.post(self.url, {"mobile_verification_code": "abcde"})
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {
            "error": True,
            "response": {
                "mobile_verification_code": "Otp didn't match, Try again later"
            },
        }
        self.assertEqual(error_data, expected_errors)

        response = self.client.post(self.url, {"mobile_verification_code": "123456"})
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {"error": False, "message": "Mobile Verified successfully"}
        self.assertEqual(error_data, expected_errors)

    def test_edit_profile(self):
        user_login = self.client.login(email="recruiter_mobile@mp.com", password="mp")
        self.assertTrue(user_login)
        self.url = reverse("recruiter:edit_profile")
        self.user = User.objects.get(email="recruiter_mobile@mp.com")
        self.user.mobile_verified = False
        self.last_mobile_code_verified_on = "06/23/2018 13:36:28"

        response = self.client.get(
            reverse(
                "recruiter:account_activation", kwargs={"user_id": self.recruiter.id}
            )
        )
        self.assertEqual(response.status_code, 404)

        self.user.mobile_verified = True

        response = self.client.get(
            reverse(
                "recruiter:account_activation", kwargs={"user_id": self.recruiter.id}
            )
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/user/details.html")

        response = self.client.post(
            self.url,
            {
                "username": "recruiter123",
                "first_name": "recruiter",
                "last_name": "recruiter",
                "nationality": "1",
                "mobile": "0987654321",
                "technical_skills": [self.skill.id],
                "industry": [self.industry.id],
                "functional_area": [self.functional_area.id],
                "year": "1990",
                "month": "5",
                "profile_description": "recruiter description",
                "job_role": "developer",
                "company_type": "startup",
                "city": self.city.id,
                "state": self.state.id,
                "user_id": self.user.id,
                "dob": "09/09/1970",
                "name": "microtest",
                "website": "microcompany.com",
                "address": "hello",
                "permanent_address": "jrlo",
                "marital_status": "Married",
            },
        )
        self.assertEqual(response.status_code, 200)

        # upload_file = open('static/img/report.png', 'rb')
        # file_dict = {'profile_pic': SimpleUploadedFile(
        #     upload_file.name, upload_file.read())}
        # data = {'username': 'recruiter', 'first_name': 'recruiter',
        #        'last_name': 'recruiter', 'nationality': '1',
        #        'mobile': '0987654321', 'technical_skills': [self.skill.id],
        #        'industry': [self.industry.id],
        #        'functional_area': [self.functional_area.id], 'year': '1990',
        #        'month': '5', 'profile_description': 'recruiter description',
        #        'job_role': 'developer', 'company_type': 'startup', 'name': 'mp',
        #        'city': self.city.id, 'state': self.state.id,
        #        'user_id': self.user.id, 'show_email': 'on', 'email_notifications': 'on', 'dob': '09-09-1990'}
        # response = self.client.post(self.url, data, file_dict, format='multipart/form-data')
        # self.assertEqual(response.status_code, 200)

    def test_index(self):
        self.url = reverse("recruiter:new_user")
        self.inactive_recruiter.is_active = False
        self.inactive_recruiter.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/register.html")

        response = self.client.post(
            self.url, {"email": self.inactive_recruiter.email, "password": "mp123"}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            self.url, {"email": self.inactive_recruiter.email, "password": "mp"}
        )
        self.assertEqual(response.status_code, 200)

        self.inactive_recruiter.is_active = True
        self.inactive_recruiter.save()

        response = self.client.post(
            self.url, {"email": self.inactive_recruiter.email, "password": "mp"}
        )
        self.assertEqual(response.status_code, 200)
        # error_data = json.loads(str(response.content, encoding='utf-8'))

    def test_company_add_menu(self):
        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)
        self.url = reverse("recruiter:add_menu")

        response = self.client.post(
            self.url, {"title": "company-menu", "url": "", "status": "True"}
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {
            "response": {"url": ["This field is required."]},
            "error": True,
        }
        self.assertEqual(error_data, expected_errors)

        response = self.client.post(
            self.url,
            {
                "title": "company-menu",
                "url": "http://testingsite.com/company",
                "status": "True",
            },
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {"error": False, "response": "Menu created successfully"}
        self.assertEqual(error_data, expected_errors)

        response = self.client.post(
            self.url,
            {
                "title": "company-menu-new",
                "url": "http://testing.com/company",
                "status": "True",
            },
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {"error": False, "response": "Menu created successfully"}
        self.assertEqual(error_data, expected_errors)

        response = self.client.post(
            self.url,
            {
                "title": "company-menu-other",
                "url": "http://testing.com/other-company",
                "status": "True",
            },
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {"error": False, "response": "Menu created successfully"}
        self.assertEqual(error_data, expected_errors)

    def test_company_edit_menu(self):
        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)
        self.menu = Menu.objects.create(
            title="menu-test",
            url="http://micropyramid.com/testing",
            lvl="123",
            company=self.recruiter.company,
        )
        self.url = reverse("recruiter:edit_menu", kwargs={"menu_id": self.menu.id})

        response = self.client.post(
            self.url, {"title": "company-menu", "url": "", "status": "True"}
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {
            "response": {"url": ["This field is required."]},
            "error": True,
        }
        self.assertEqual(error_data, expected_errors)

        response = self.client.post(
            self.url,
            {
                "title": "company new menu",
                "url": "http://testingsite.com/new-company",
                "status": "False",
            },
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {"error": False, "response": "Menu created successfully"}
        self.assertEqual(error_data, expected_errors)

    def test_company_menu_status(self):
        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)
        self.url = reverse("recruiter:menu_status", kwargs={"menu_id": "1"})

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(
            reverse("recruiter:menu_status", kwargs={"menu_id": "10"})
        )
        self.assertEqual(response.status_code, 302)

    def test_company_menu_order(self):

        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)
        self.url = reverse("recruiter:menu_order")

        response = self.client.get(reverse("jobs:index") + "?prev=1&current=2")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("jobs:index") + "?prev=2&current=1")
        self.assertEqual(response.status_code, 200)

    def test_company_delete_menu(self):

        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)
        self.menu = Menu.objects.create(
            title="test-mneu",
            url="http://micropyramid.com",
            lvl="123",
            company=self.recruiter.company,
        )
        self.url = reverse("recruiter:delete_menu", kwargs={"menu_id": self.menu.id})

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {"error": False, "response": "Menu Deleted Successfully"}
        self.assertEqual(error_data, expected_errors)

        response = self.client.get(
            reverse("recruiter:delete_menu", kwargs={"menu_id": "10"})
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {"error": True, "response": "Some Problem Occurs"}
        self.assertEqual(error_data, expected_errors)

    def test_company(self):
        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)

        response = self.client.get(reverse("recruiter:view_company"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/company/view_microsite_page.html")

        response = self.client.get(reverse("recruiter:company_recruiter_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/company/recruiter_list.html")

        response = self.client.get(
            reverse("recruiter:company_recruiter_list") + "?search=active"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/company/recruiter_list.html")

        response = self.client.get(
            reverse("recruiter:company_recruiter_list") + "?search=recruiter"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/company/recruiter_list.html")

        response = self.client.get(
            reverse("recruiter:company_recruiter_list") + "?page=1"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/company/recruiter_list.html")

        response = self.client.get(
            reverse(
                "recruiter:company_recruiter_profile",
                kwargs={"recruiter_id": self.recruiter.id},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/company/recruiter_profile.html")

        response = self.client.get(
            reverse(
                "recruiter:company_recruiter_profile", kwargs={"recruiter_id": "1000"}
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "recruiter/recruiter_404.html")

        response = self.client.get(
            reverse(
                "recruiter:company_recruiter_profile",
                kwargs={"recruiter_id": self.recruiter.id},
            )
            + "?job_status=Live"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/company/recruiter_profile.html")

        response = self.client.get(
            reverse(
                "recruiter:company_recruiter_profile",
                kwargs={"recruiter_id": self.recruiter.id},
            )
            + "?search_value=Internship"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/company/recruiter_profile.html")

        response = self.client.get(
            reverse(
                "recruiter:company_recruiter_profile",
                kwargs={"recruiter_id": self.recruiter.id},
            )
            + "?page=1"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/company/recruiter_profile.html")

        response = self.client.get(
            reverse(
                "recruiter:activate_company_recruiter",
                kwargs={"recruiter_id": self.recruiter.id},
            )
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get(
            reverse(
                "recruiter:activate_company_recruiter",
                kwargs={"recruiter_id": self.recruiter.id},
            )
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get(
            reverse(
                "recruiter:activate_company_recruiter", kwargs={"recruiter_id": "100"}
            )
        )
        self.assertEqual(response.status_code, 302)

    def test_company_recruiter_create(self):

        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)

        response = self.client.get(reverse("recruiter:company_recruiter_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/company/create_recruiter.html")

        response = self.client.post(
            reverse("recruiter:company_recruiter_create"),
            data={
                "mobile": "8977455970",
                "email": "testrecruiter@mp.com",
                "job_role": "developer",
                "first_name": "testreruiter",
                "password": "Mp1234@",
            },
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {"response": "Recruiter Created Successfully", "error": False}
        self.assertEqual(error_data, expected_errors)

        response = self.client.post(
            reverse("recruiter:company_recruiter_create"),
            data={
                "email": "testrecruiter1@mp.com",
                "job_role": "developer",
                "first_name": "testreruiter",
                "password": "Mp1234@",
                "mobile": "9010757124",
            },
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {
            "response": {"mobile": ["This field is required."]},
            "error": True,
        }
        self.assertTrue(error_data, expected_errors)

    def test_company_recruiter_edit(self):
        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)
        self.url = reverse(
            "recruiter:edit_company_recruiter",
            kwargs={"recruiter_id": self.company_recruiter.id},
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/company/create_recruiter.html")

        response = self.client.get(
            reverse("recruiter:edit_company_recruiter", kwargs={"recruiter_id": "100"})
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.post(
            reverse("recruiter:edit_company_recruiter", kwargs={"recruiter_id": "100"}),
            data={
                "mobile": "0987654321",
                "email": self.company_recruiter.email,
                "job_role": "developer123",
                "first_name": "testreruiter123",
                "password": "Mp1234@",
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_company_recruiter_delete(self):
        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)

        self.url = reverse(
            "recruiter:delete_company_recruiter",
            kwargs={"recruiter_id": self.company_recruiter.id},
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {"error": False, "response": "Recruiter Deleted Successfully"}
        self.assertEqual(error_data, expected_errors)

        response = self.client.get(
            reverse(
                "recruiter:delete_company_recruiter", kwargs={"recruiter_id": "100"}
            )
        )
        self.assertEqual(response.status_code, 200)
        error_data = json.loads(str(response.content, encoding="utf-8"))
        expected_errors = {"error": True, "response": "Some Problem Occurs"}
        self.assertEqual(error_data, expected_errors)

    def test_interview_location(self):
        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)

        response = self.client.post(
            reverse("recruiter:interview_location", kwargs={"location_count": "1"}),
            data={"selected_locations": "1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recruiter/job/add_interview_location.html")

    def test_twitter_logins(self):
        response = self.client.post(reverse("recruiter:twitter_login"))
        self.assertEqual(response.status_code, 302)

    def test_facebook_login(self):
        response = self.client.post(reverse("recruiter:facebook_login"))
        self.assertEqual(response.status_code, 302)

    def test_linkedin_login(self):
        response = self.client.post(reverse("recruiter:linkedin_login"))
        self.assertEqual(response.status_code, 302)

    def test_google_login(self):
        response = self.client.post(reverse("recruiter:google_connect"))
        self.assertEqual(response.status_code, 302)
