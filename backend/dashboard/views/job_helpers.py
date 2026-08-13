"""
Helpers for job posting operations.

Moved out of recruiter/views/ 2026-08-12: dashboard/views/job_management.py was
the only caller, and the file already imported dashboard.tasks, so it was
pointing back at its own consumer.
"""

import json

from django.conf import settings
from django.template import loader
from django.template.defaultfilters import slugify

from dashboard.tasks import send_email
from peeldb.models import (
    InterviewLocation,
    Qualification,
    Skill,
)


def add_other_skills(job_post, data, user):
    temp = loader.get_template("recruiter/email/add_other_fields.html")
    subject = "PeelJobs New JobPost"
    mto = [settings.DEFAULT_FROM_EMAIL]
    for skill in data:
        for value in skill.values():
            other_skills = value.replace(" ", "").split(",")
            for value in other_skills:
                if value != "":
                    skills = Skill.objects.filter(name__iexact=value)
                    if skills:
                        job_post.skills.add(skills[0])
                    else:
                        skill = Skill.objects.create(
                            name=value,
                            status="InActive",
                            slug=slugify(value),
                            skill_type="Technical",
                        )
                        c = {
                            "job_post": job_post,
                            "user": user,
                            "item": value,
                            "type": "Skill",
                            "value": skill.name,
                        }
                        rendered = temp.render(c)
                        send_email.delay(mto, subject, rendered)
                        job_post.skills.add(skill)


def add_other_qualifications(job_post, data, user):
    temp = loader.get_template("recruiter/email/add_other_fields.html")
    subject = "PeelJobs New JobPost"
    mto = [settings.DEFAULT_FROM_EMAIL]
    for qualification in data:
        for value in qualification.values():
            other_skills = value.replace(" ", "").split(",")
            for value in other_skills:
                if value != "":
                    qualification = Qualification.objects.filter(name__iexact=value)
                    if qualification:
                        job_post.edu_qualification.add(qualification[0])
                    else:
                        qualification = Qualification.objects.create(
                            name=value, status="InActive", slug=slugify(value)
                        )
                        job_post.edu_qualification.add(qualification)
                        c = {
                            "job_post": job_post,
                            "user": user,
                            "item": value,
                            "type": "Qualification",
                            "value": qualification.name,
                        }
                        rendered = temp.render(c)
                        send_email.delay(mto, subject, rendered)


def add_interview_location(data, job_post, no_of_locations):
    for i in range(1, no_of_locations):
        current_interview_city = "final_location_" + str(i)
        current_venue_details = "venue_details_" + str(i)
        # current_show_location = 'show_location_' + str(i)
        # show_location = False
        interview_venue_details = ""
        latitude = ""
        longitude = ""
        for key in data:
            if str(current_interview_city) == str(key):
                interview_city = list(json.loads(data[key]))
                latitude = interview_city[0]
                longitude = interview_city[1]

            if str(current_venue_details) == str(key):
                interview_venue_details = data[key]

            # if str(current_show_location) == str(key):
            #     show_location = True

        if interview_venue_details or latitude or longitude:
            # interview_location = InterviewLocation.objects.create(
            # venue_details=interview_venue_details, latitude=latitude,
            # longitude=longitude)
            interview_location = InterviewLocation.objects.create(
                venue_details=interview_venue_details
            )
            # interview_location.show_location = show_location
            interview_location.save()
            job_post.job_interview_location.add(interview_location)
