from django.test import TestCase
from django.test import Client
from django.urls import reverse
from datetime import datetime
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
    InterviewLocation,
)
from django.core import management


class BaseTest(TestCase):

    """
    Common class with setUp method for all test cases
    """

    def setUp(self):
        self.client = Client()
        self.country = Country.objects.create(name="India")
        self.state = State.objects.create(
            name="Telangana", country_id=self.country.id, slug="telangana"
        )
        self.city = City.objects.create(
            name="Hyderabad", state_id=self.state.id, slug="hyderabad"
        )
        self.industry = Industry.objects.create(name="Software", slug="software")
        self.skill = Skill.objects.create(name="Python", slug="python")
        self.functional_area = FunctionalArea.objects.create(name="functional_area")
        self.qualification = Qualification.objects.create(name="btech")
        self.user = User.objects.create(email="test@mp.com", username="test")
        current_date = datetime.strptime(
            str(datetime.now().date()), "%Y-%m-%d"
        ).strftime("%Y-%m-%d")

        self.recruiter = User.objects.create(
            email="recruiter@mp.com",
            username="recruiter",
            user_type="RR",
            is_active=True,
            mobile_verified=True,
        )
        self.recruiter.set_password("mp")
        self.recruiter.save()

        self.user.set_password("mp")
        self.user.save()

        self.admin_user = User.objects.create(email="mp@mp.com", username="mp@mp.com")
        self.admin_user.set_password("mp")
        self.admin_user.is_active = True
        self.admin_user.is_staff = True
        self.admin_user.save()

        for each in range(0, 15):
            self.jobpost = JobPost.objects.create(
                user=self.user,
                country=self.country,
                title="test-jobpost_" + str(each),
                vacancies="6",
                description="job post description",
                job_type="full-time",
                status="Live",
                published_message="test message",
                company_address="company address",
                company_description="company description",
                last_date=current_date,
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

        for each in range(0, 15):
            self.jobpost = JobPost.objects.create(
                user=self.user,
                country=self.country,
                title="test-jobpost_" + str(each),
                vacancies="6",
                description="job post description",
                job_type="internship",
                status="Live",
                published_message="test message",
                company_address="company address",
                company_description="company description",
                last_date=current_date,
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

        for each in range(0, 15):
            self.jobpost = JobPost.objects.create(
                user=self.user,
                country=self.country,
                title="test-jobpost_" + str(each),
                vacancies="6",
                description="job post description",
                job_type="walk-in",
                walkin_from_date=current_date,
                walkin_to_date=current_date,
                status="Live",
                published_message="test message",
                company_address="company address",
                company_description="company description",
                last_date=current_date,
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

        for each in range(0, 15):
            self.jobpost = JobPost.objects.create(
                user=self.user,
                country=self.country,
                title="test-jobpost_" + str(each),
                vacancies="6",
                description="job post description",
                job_type="government",
                status="Live",
                published_message="test message",
                company_address="company address",
                company_description="company description",
                last_date=current_date,
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
        management.call_command("rebuild_index", interactive=False)


class all_views_get_for_job_seeker(BaseTest):
    def test_views_get(self):

        response = self.client.get(reverse("jobs:index"))
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, 'jobs/jobs_list.html')

        response = self.client.get(reverse("jobs:index") + "?page=1")
        self.assertEqual(response.status_code, 301)
        # self.assertTemplateUsed(response, 'jobs/jobs_list.html')

        response = self.client.get(reverse("jobs:index") + "?page=100")
        self.assertEqual(response.status_code, 301)
        # self.assertTemplateUsed(response, 'jobs/jobs_list.html')

        response = self.client.get(reverse("jobs_by_skill"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_by_skills.html")

        response = self.client.get(reverse("jobs_by_skill") + "?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_by_skills.html")

        response = self.client.get(reverse("jobs_by_skill") + "?page=100")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_by_skills.html")

        response = self.client.get(
            reverse("jobs_by_location", kwargs={"job_type": "jobs"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_by_location.html")

        response = self.client.get(
            reverse("jobs_by_location", kwargs={"job_type": "jobs"}) + "?page=1"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_by_location.html")

        response = self.client.get(
            reverse("jobs_by_location", kwargs={"job_type": "jobs"}) + "?page=100"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_by_location.html")

        response = self.client.get(reverse("jobs_by_industry"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_by_industries.html")

        response = self.client.get(reverse("jobs_by_industry") + "?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_by_industries.html")

        response = self.client.get(reverse("jobs_by_industry") + "?page=100")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_by_industries.html")

        response = self.client.get(reverse("walkin_jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(reverse("walkin_jobs") + "?page=1")
        self.assertEqual(response.status_code, 301)
        # self.assertTemplateUsed(response, 'jobs/jobs_list.html')

        response = self.client.get(reverse("walkin_jobs") + "?page=100")
        self.assertEqual(response.status_code, 301)
        # self.assertTemplateUsed(response, 'jobs/jobs_list.html')

        response = self.client.get(reverse("full_time_jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(reverse("full_time_jobs") + "?page=1")
        self.assertEqual(response.status_code, 301)
        # self.assertTemplateUsed(response, 'jobs/jobs_list.html')

        response = self.client.get(reverse("full_time_jobs") + "?page=100")
        self.assertEqual(response.status_code, 301)
        # self.assertTemplateUsed(response, 'jobs/jobs_list.html')

        response = self.client.get(reverse("internship_jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "internship.html")

        response = self.client.get(reverse("internship_jobs") + "?page=1")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("internship_jobs") + "?page=100")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("city_internship_jobs", kwargs={"location": self.city.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(
            reverse("city_internship_jobs", kwargs={"location": self.city.slug})
            + "?page=1"
        )
        self.assertEqual(response.status_code, 301)
        # self.assertTemplateUsed(response, 'jobs/jobs_list.html')

        response = self.client.get(
            reverse("city_internship_jobs", kwargs={"location": self.city.slug})
            + "?page=100"
        )
        self.assertEqual(response.status_code, 301)
        # self.assertTemplateUsed(response, 'jobs/jobs_list.html')

        response = self.client.get(
            reverse("job_industries", kwargs={"industry": self.industry.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(
            reverse("job_industries", kwargs={"industry": self.industry.slug})
            + "?page=1"
        )
        self.assertEqual(response.status_code, 301)
        # self.assertTemplateUsed(response, 'jobs/jobs_list.html')

        response = self.client.get(
            reverse("job_industries", kwargs={"industry": self.industry.slug})
            + "?page=100"
        )
        self.assertEqual(response.status_code, 301)
        response = self.client.get(
            reverse("job_locations", kwargs={"location": self.city.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(
            reverse("job_locations", kwargs={"location": self.city.slug}) + "?page=1"
        )
        self.assertEqual(response.status_code, 301)
        # self.assertTemplateUsed(response, 'jobs/jobs_list.html')

        response = self.client.get(
            reverse("job_locations", kwargs={"location": self.city.slug}) + "?page=100"
        )
        self.assertEqual(response.status_code, 301)

        response = self.client.get(reverse("recruiters"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/recruiters_list.html")

        response = self.client.get(
            reverse("recruiter_profile", kwargs={"recruiter_name": self.user.username})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/recruiter_profile.html")

        response = self.client.get(
            reverse("recruiter_profile", kwargs={"recruiter_name": "recruiter_name"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

        response = self.client.get(reverse("sitemap_xml"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/contact-us.html")

        response = self.client.get(reverse("sitemap"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "sitemap.html")

        response = self.client.get(reverse("pages", kwargs={"page_name": "about-us"}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/about-us.html")

        response = self.client.get(reverse("pages", kwargs={"page_name": "about"}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_recruiter_login_get(self):
        user_login = self.client.login(email="recruiter@mp.com", password="mp")
        self.assertTrue(user_login)

        response = self.client.get(reverse("pages", kwargs={"page_name": "about-us"}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/about-us.html")

        response = self.client.get(reverse("pages", kwargs={"page_name": "about"}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "recruiter/recruiter_404.html")

        response = self.client.get(reverse("jobs:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(reverse("walkin_jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")
        response = self.client.get(reverse("full_time_jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(reverse("internship_jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "internship.html")

        response = self.client.get(reverse("government_jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(
            reverse("city_internship_jobs", kwargs={"location": self.city.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(
            reverse("job_industries", kwargs={"industry": self.industry.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")
        response = self.client.get(
            reverse("job_locations", kwargs={"location": self.city.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(reverse("get_out"))
        self.assertEqual(response.status_code, 302)

    def test_admin_login_get(self):

        response = self.client.get(reverse("get_out"))
        self.assertEqual(response.status_code, 302)

        user_login = self.client.login(email="mp@mp.com", password="mp")
        self.assertTrue(user_login)

        response = self.client.get(reverse("pages", kwargs={"page_name": "about-us"}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/about-us.html")

        response = self.client.get(reverse("pages", kwargs={"page_name": "about"}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

        response = self.client.get(reverse("jobs:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(reverse("walkin_jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(reverse("full_time_jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(reverse("internship_jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "internship.html")

        response = self.client.get(reverse("government_jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(
            reverse("city_internship_jobs", kwargs={"location": self.city.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")

        response = self.client.get(
            reverse("job_industries", kwargs={"industry": self.industry.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")
        response = self.client.get(
            reverse("job_locations", kwargs={"location": self.city.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobs/jobs_list.html")


class calendar_views_get(BaseTest):
    def test_views_get(self):
        response = self.client.get(
            reverse("year_calendar", kwargs={"year": datetime.now().year})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "calendar/year_calendar.html")

        response = self.client.get(
            reverse(
                "month_calendar",
                kwargs={"year": datetime.now().year, "month": datetime.now().month},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "calendar/year_calendar.html")

        response = self.client.get(
            reverse(
                "week_calendar",
                kwargs={
                    "year": datetime.now().year,
                    "month": datetime.now().month,
                    "week": "1",
                },
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "calendar/year_calendar.html")

        response = self.client.get(
            reverse(
                "jobposts_by_date",
                kwargs={
                    "year": datetime.now().year,
                    "month": datetime.now().month,
                    "date": datetime.now().date().day,
                },
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "calendar/calendar_day_results.html")
