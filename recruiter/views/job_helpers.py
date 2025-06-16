"""
Job Helper Functions
Helper functions and utilities for job posting operations
"""
import json
import urllib
import requests
import math
import random
import time
from mpcomp.s3_utils import S3Connection
import csv
from collections import OrderedDict

from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.template import loader, Template, Context
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.hashers import check_password
from django.db.models import Q, Count
from django.contrib.auth import update_session_auth_hash
from django.template.defaultfilters import slugify
from django.contrib.auth.models import Permission, ContentType
from django.db.models import Case, When
import boto3
from django.contrib.auth import load_backend


from mpcomp.aws import AWS
from dashboard.tasks import sending_mail, send_email
from django.utils.crypto import get_random_string
from mpcomp.facebook import GraphAPI, get_access_token_from_code
from mpcomp.views import get_absolute_url
from pjob.views import save_codes_and_send_mail
from peeldb.models import (
    Country,
    JobPost,
    MetaData,
    State,
    City,
    Skill,
    Industry,
    Qualification,
    AppliedJobs,
    User,
    JOB_TYPE,
    FunctionalArea,
    Keyword,
    UserEmail,
    MARTIAL_STATUS,
    Google,
    Facebook,
    Company,
    MailTemplate,
    SentMail,
    InterviewLocation,
    COMPANY_TYPES,
    Menu,
    Ticket,
    AGENCY_INVOICE_TYPE,
    AGENCY_JOB_TYPE,
    AgencyCompany,
    AgencyRecruiterJobposts,
    AGENCY_RECRUITER_JOB_TYPE,
    AgencyApplicants,
    AgencyResume,
    POST,
    UserMessage,
)
from recruiter.forms import (
    JobPostForm,
    YEARS,
    MONTHS,
    Company_Form,
    User_Form,
    ChangePasswordForm,
    PersonalInfoForm,
    MobileVerifyForm,
    MailTemplateForm,
    EditCompanyForm,
    RecruiterForm,
    MenuForm,
    ApplicantResumeForm,
    ResumeUploadForm,
)

from mpcomp.views import (
    rand_string,
    recruiter_login_required,
    get_prev_after_pages_count,
    agency_admin_login_required,
    get_next_month,
    get_aws_file_path,
    get_resume_data,
    handle_uploaded_file,
)


# Job Helper Functions will be moved here
# TODO: Move the following functions from the main views.py:
# - add_other_skills()
# - add_other_qualifications()
# - add_other_functional_area()
# - adding_keywords()
# - add_interview_location()
# - add_other_locations()
# - set_other_fields()
# - adding_other_fields_data()
# - save_job_post()
# - checking_error_value()
# - retreving_form_errors()


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





def add_other_functional_area(job_post, data, user):
    temp = loader.get_template("recruiter/email/add_other_fields.html")
    subject = "PeelJobs New JobPost"
    mto = [settings.DEFAULT_FROM_EMAIL]

    for functional_area in data:
        for value in functional_area.values():
            other_areas = value.replace(" ", "").split(",")
            for value in other_areas:
                if value != "":
                    functional_area = FunctionalArea.objects.filter(name__iexact=value)
                    if functional_area:
                        job_post.functional_area.add(functional_area[0])
                    else:
                        functional_area = FunctionalArea.objects.create(
                            name=value, status="InActive"
                        )
                        job_post.functional_area.add(functional_area)
                        c = {
                            "job_post": job_post,
                            "user": user,
                            "item": value,
                            "type": "Functional Area",
                            "value": functional_area.name,
                        }
                        rendered = temp.render(c)
                        send_email.delay(mto, subject, rendered)




def adding_keywords(keywords, post):
    for kw in keywords:
        key = Keyword.objects.filter(name__iexact=kw)
        if not kw == "":
            if not key:
                keyword = Keyword.objects.create(name=kw)
                post.keywords.add(keyword)
            else:
                post.keywords.add(key[0])





def add_interview_location(data, job_post, no_of_locations):
    for i in range(1, no_of_locations):
        current_interview_city = "final_location_" + str(i)
        current_venue_details = "venue_details_" + str(i)
        # current_show_location = 'show_location_' + str(i)
        # show_location = False
        interview_venue_details = ""
        latitude = ""
        longitude = ""
        for key in data.keys():
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




def add_other_locations(post, data, user):
    pass


def set_other_fields(post, data, user):
    if data.get("last_date"):
        last_date = datetime.strptime(data.get("last_date"), "%m/%d/%Y").strftime(
            "%Y-%m-%d"
        )
        post.last_date = last_date
    else:
        post.last_date = get_next_month()

    post.fresher = data.get("min_year") == 0
    if data.get("visa_required"):
        post.visa_required = True
        visa_country = Country.objects.get(id=data.get("visa_country"))
        post.visa_country = visa_country
        post.visa_type = data.get("visa_type")
    else:
        post.visa_required = False
        post.visa_type = ""
        post.visa_country = None

    if data.get("published_date"):
        start_date = datetime.strptime(
            data.get("published_date"), "%m/%d/%Y %H:%M:%S"
        ).strftime("%Y-%m-%d %H:%M:%S")
        date_format = "%Y-%m-%d %H:%M:%S"
        post.published_date = datetime.strptime(start_date, date_format)
    if data.get("status") == "Pending":

        if data.get("fb_post") == "on":
            post.post_on_fb = True
            post.fb_groups = data.getlist("fb_groups")
        post.post_on_tw = data.get("tw_post") == "on"
        post.post_on_ln = data.get("ln_post") == "on"
    if data.get("job_type") == "walk-in":
        post.vacancies = 0
        post.walkin_contactinfo = data.get("walkin_contactinfo")
        walkin_from_date = datetime.strptime(
            data.get("walkin_from_date"), "%m/%d/%Y"
        ).strftime("%Y-%m-%d")
        post.walkin_show_contact_info = data.get("walkin_show_contact_info") == "on"
        post.walkin_from_date = walkin_from_date
        walkin_to_date = datetime.strptime(
            data.get("walkin_to_date"), "%m/%d/%Y"
        ).strftime("%Y-%m-%d")

        post.walkin_to_date = walkin_to_date
        if data.get("walkin_time"):
            post.walkin_time = data.get("walkin_time")

        post.last_date = walkin_to_date
    post.save()

    if user.agency_admin or user.has_perm("jobposts_edit"):
        post.agency_job_type = data.get("agency_job_type")
        post.agency_invoice_type = data.get("agency_invoice_type")
        if data.get("agency_client"):
            client = AgencyCompany.objects.get(id=data.get("agency_client"))
            post.agency_client = client
        # if data.get('agency_category'):
        #     agency_category = AgencyCompanyCatogery.objects.get(
        #         id=data.get('agency_category'))
        #     post.agency_category = agency_category
        post.save()

        agency_resumes = AgencyResume.objects.filter(uploaded_by__company=user.company)
        agency_resumes = agency_resumes.filter(skill__in=post.skills.all())

        for each_resume in agency_resumes:
            AgencyApplicants.objects.create(applicant=each_resume, job_post=post)
        # post.agency_recruiters.clear()
        # post.agency_recruiters.add(*data.getlist('agency_recruiters'))
        for each_recruiter in data.getlist("agency_recruiters"):
            user = get_object_or_404(User, id=each_recruiter)
            AgencyRecruiterJobposts.objects.create(job_post=post, user=user)




def adding_other_fields_data(data, post, user):
    if "final_skills" in data.keys():
        add_other_skills(post, json.loads(data["final_skills"]), user)
    if "final_edu_qualification" in data.keys():
        add_other_qualifications(
            post, json.loads(data["final_edu_qualification"]), user
        )
    if "final_functional_area" in data.keys():
        add_other_functional_area(post, json.loads(data["final_functional_area"]), user)
    if "other_location" in data.keys():
        add_other_locations(post, data, user)

    no_of_locations = int(json.loads(data["no_of_interview_location"])) + 1
    add_interview_location(data, post, no_of_locations)

    adding_keywords(data.getlist("keywords"), post)
    post.send_email_notifications = data.get("send_email_notifications") == "True"

    post.status = data.get("status")
    post.published_message = data.get("published_message")
    post.job_type = data.get("job_type")
    post.save()
    set_other_fields(post, data, user)



def save_job_post(validate_post, request):
    validate_post.agency_amount = validate_post.agency_amount or ""
    validate_post.user = request.user
    validate_post.published_on = datetime.now()
    validate_post.vacancies = request.POST.get("vacancies") or 0
    validate_post.pincode = request.POST.get("pincode", "")
    if request.POST.get("major_skill"):
        skill = Skill.objects.filter(id=request.POST.get("major_skill"))
        if skill:
            validate_post.major_skill = skill[0]
    company = Company.objects.filter(name__iexact=request.POST["company_name"])
    if company:
        job_post_company = company[0]
        job_post_company.name = request.POST["company_name"]
        job_post_company.slug = slugify(request.POST["company_name"])
        job_post_company.address = request.POST["company_address"]
        job_post_company.profile = request.POST["company_description"]
        job_post_company.website = request.POST["company_website"]
        if "company_logo" in request.FILES:
            file_path = get_aws_file_path(
                request.FILES.get("company_logo"),
                "company/logo/",
                slugify(request.POST["company_name"]),
            )
            job_post_company.profile_pic = file_path
        job_post_company.save()
    else:
        job_post_company = Company.objects.create(
            name=request.POST["company_name"],
            address=request.POST["company_address"],
            profile=request.POST["company_description"],
            slug=slugify(request.POST["company_name"]),
            company_type="Company",
            email=request.user.email,
            created_from="job_post",
            website=request.POST["company_website"],
        )
        if request.FILES.get("company_logo"):
            file_path = get_aws_file_path(
                request.FILES.get("company_logo"),
                "company/logo/",
                slugify(request.POST["company_name"]),
            )
            job_post_company.profile_pic = file_path
        job_post_company.save()
    validate_post.company = job_post_company
    validate_post.save()
    validate_post.slug = get_absolute_url(validate_post)
    validate_post.save()

    if request.user.is_admin and request.user.is_agency_recruiter:
        for recruiter in request.POST.getlist("agency_recruiters"):
            user = User.objects.get(id=recruiter)
            c = {"job_post": validate_post, "user": user}
            t = loader.get_template("email/assign_jobpost.html")
            subject = "PeelJobs New JobPost"
            rendered = t.render(c)
            user_active = True if user.is_active else False
            mto = [user.email]
            send_email.delay(mto, subject, rendered)



def checking_error_value(errors, key_item):
    for each in json.loads(key_item):
        for key, value in each.items():
            if not value:
                errors[key] = "This field is required."
    return errors



def retreving_form_errors(request, post):
    errors = post.errors
    # no_of_locations = int(
    #     json.loads(request.POST['no_of_interview_location']))+1
    # for i in range(1, no_of_locations):
    #     # location = 'show_location_' + str(i)
    #     final_location = 'final_location_' + str(i)
    #     if final_location in request.POST.keys():
    #         if request.POST[final_location]:
    #             pass
    #         else:
    #             if not request.POST[final_location]:
    #                 errors[final_location] = 'This field is required.'

    if "final_industry" in request.POST.keys():
        errors = checking_error_value(errors, request.POST["final_industry"])

    if "final_functional_area" in request.POST.keys():
        errors = checking_error_value(errors, request.POST["final_functional_area"])

    if "final_edu_qualification" in request.POST.keys():
        errors = checking_error_value(errors, request.POST["final_edu_qualification"])

    if "final_skills" in request.POST.keys():
        errors = checking_error_value(errors, request.POST["final_skills"])

    return errors
