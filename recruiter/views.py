import json
import urllib
import requests
import math
import os
import random
import time
from bson import ObjectId
import tinys3
import csv
from collections import OrderedDict

from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from twython.api import Twython
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
from boto.s3.connection import S3Connection
from django.contrib.auth import load_backend


from peeldb.models import (
    Country,
    JobPost,
    State,
    City,
    Skill,
    Industry,
    Qualification,
    AppliedJobs,
    Twitter,
    User,
    JOB_TYPE,
    FacebookPost,
    TwitterPost,
    FunctionalArea,
    Keyword,
    UserEmail,
    MARTIAL_STATUS,
    Google,
    Facebook,
    Linkedin,
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
)
from .forms import (
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
from .tasks import (
    del_jobpost_tw,
    del_jobpost_fb,
    del_jobpost_peel_fb,
    add_twitter_friends_followers,
    add_google_friends,
    add_facebook_friends_pages_groups,
)
from dashboard.tasks import sending_mail
from mpcomp.views import (
    rand_string,
    Memail,
    recruiter_login_required,
    get_prev_after_pages_count,
    agency_admin_login_required,
    get_next_month,
    get_aws_file_path,
    mongoconnection,
    get_resume_data,
    handle_uploaded_file,
)
from mpcomp.facebook import GraphAPI, get_access_token_from_code
from mpcomp.aws import AWS
from django.utils.crypto import get_random_string
from mpcomp.views import get_absolute_url, save_codes_and_send_mail

db = mongoconnection()


@recruiter_login_required
def jobs_list(request):
    if request.user.agency_admin:
        active_jobs_list = (
            JobPost.objects.filter(user__company=request.user.company)
            .exclude(status="Disabled")
            .exclude(status="Expired")
            .prefetch_related("location", "agency_recruiters")
            .annotate(responses=Count("appliedjobs"))
            .order_by("-id")
        )
    elif request.user.is_agency_recruiter:
        active_jobs_list = (
            JobPost.objects.filter(
                Q(agency_recruiters__in=[request.user]) | Q(user=request.user)
            )
            .exclude(status="Disabled")
            .exclude(status="Expired")
            .prefetch_related("location", "agency_recruiters")
            .annotate(responses=Count("appliedjobs"))
            .order_by("-id")
            .distinct()
        )
    else:
        active_jobs_list = (
            JobPost.objects.filter(user=request.user)
            .exclude(status="Disabled")
            .exclude(status="Expired")
            .prefetch_related("location", "agency_recruiters")
            .annotate(responses=Count("appliedjobs"))
            .order_by("-id")
        )
    items_per_page = 10
    if request.POST.get("search_value"):
        if request.POST.get("search_value") == "all":
            pass
        else:
            active_jobs_list = active_jobs_list.filter(
                job_type__iexact=request.POST.get("search_value")
            )

    if "page" in request.POST and int(request.POST.get("page")) > 0:
        page = int(request.POST.get("page"))
    else:
        page = 1

    no_pages = int(math.ceil(float(active_jobs_list.count()) / items_per_page))
    active_jobs_list = active_jobs_list[
        (page - 1) * items_per_page : page * items_per_page
    ]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    return render(
        request,
        "recruiter/job/list.html",
        {
            "jobs_list": active_jobs_list,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "search_value": request.POST["search_value"]
            if "search_value" in request.POST
            else "All",
        },
    )


@recruiter_login_required
def inactive_jobs(request):
    inactive_jobs_list = JobPost.objects.filter(
        Q(user=request.user.id) & Q(status="Disabled") | Q(status="Expired")
    ).order_by("-id")
    inactive_jobs_list = inactive_jobs_list.filter(user=request.user)

    items_per_page = 10
    if request.POST.get("search_value"):
        if request.POST.get("search_value") == "all":
            pass
        else:
            inactive_jobs_list = inactive_jobs_list.filter(
                job_type__iexact=request.POST.get("search_value")
            )

    if "page" in request.POST and int(request.POST.get("page")) > 0:
        page = int(request.POST.get("page"))
    else:
        page = 1

    no_pages = int(math.ceil(float(inactive_jobs_list.count()) / items_per_page))
    inactive_jobs_list = inactive_jobs_list[
        (page - 1) * items_per_page : page * items_per_page
    ]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    return render(
        request,
        "recruiter/job/list.html",
        {
            "jobs_list": inactive_jobs_list,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "search_value": request.POST["search_value"]
            if "search_value" in request.POST.keys()
            else "All",
        },
    )


def add_other_skills(job_post, data, user):
    temp = loader.get_template("recruiter/email/add_other_fields.html")
    subject = "PeelJobs New JobPost"
    mto = [settings.DEFAULT_FROM_EMAIL]
    mfrom = settings.DEFAULT_FROM_EMAIL
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
                        Memail(mto, mfrom, subject, rendered, True)
                        job_post.skills.add(skill)


def add_other_qualifications(job_post, data, user):
    temp = loader.get_template("recruiter/email/add_other_fields.html")
    subject = "PeelJobs New JobPost"
    mto = [settings.DEFAULT_FROM_EMAIL]
    mfrom = settings.DEFAULT_FROM_EMAIL
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
                        Memail(mto, mfrom, subject, rendered, True)


def add_other_industry(job_post, data, user):
    temp = loader.get_template("recruiter/email/add_other_fields.html")
    subject = "PeelJobs New JobPost"
    mto = [settings.DEFAULT_FROM_EMAIL]
    mfrom = settings.DEFAULT_FROM_EMAIL

    for industry in data:
        for value in industry.values():
            o_industries = value.replace(" ", "").split(",")
            for value in o_industries:
                if value != "":
                    industry = Industry.objects.filter(name__iexact=value)
                    if industry:
                        job_post.industry.add(industry[0])
                    else:
                        industry = Industry.objects.create(
                            name=value, status="InActive", slug=slugify(value)
                        )
                        job_post.industry.add(industry)
                        c = {
                            "job_post": job_post,
                            "user": user,
                            "item": value,
                            "type": "Industry",
                            "value": industry.name,
                        }
                        rendered = temp.render(c)
                        Memail(mto, mfrom, subject, rendered, True)


def add_other_functional_area(job_post, data, user):
    temp = loader.get_template("recruiter/email/add_other_fields.html")
    subject = "PeelJobs New JobPost"
    mto = [settings.DEFAULT_FROM_EMAIL]
    mfrom = settings.DEFAULT_FROM_EMAIL

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
                        Memail(mto, mfrom, subject, rendered, True)


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


def add_other_locations(post, data, user):
    temp = loader.get_template("recruiter/email/add_other_fields.html")
    subject = "PeelJobs New JobPost"
    mto = [settings.DEFAULT_FROM_EMAIL]
    mfrom = settings.DEFAULT_FROM_EMAIL
    for location in data.getlist("other_location"):
        locations = [loc.strip() for loc in location.split(",") if loc.strip()]
        for location in locations:
            locations = City.objects.filter(name__iexact=location)
            if locations:
                post.location.add(locations[0])
            else:
                location = City.objects.create(
                    name=location,
                    status="Disabled",
                    slug=slugify(location),
                    state=State.objects.get(id=16),
                )
                post.location.add(location)
                c = {
                    "job_post": post,
                    "user": user,
                    "item": "Location",
                    "type": "Location",
                    "value": location.name,
                }
                rendered = temp.render(c)
                Memail(mto, mfrom, subject, rendered, True)


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
    if "final_industry" in data.keys():
        add_other_industry(post, json.loads(data["final_industry"]), user)
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
    validate_post.slug = get_absolute_url(validate_post)
    validate_post.save()

    if request.user.is_admin and request.user.is_agency_recruiter:
        for recruiter in request.POST.getlist("agency_recruiters"):
            user = User.objects.get(id=recruiter)
            c = {"job_post": validate_post, "user": user}
            t = loader.get_template("email/assign_jobpost.html")
            subject = "PeelJobs New JobPost"
            rendered = t.render(c)
            mfrom = settings.DEFAULT_FROM_EMAIL
            user_active = True if user.is_active else False
            Memail([user.email], mfrom, subject, rendered, user_active)


@recruiter_login_required
def new_job(request, status):
    if request.method == "GET":
        if request.GET.get("q"):
            companies = Company.objects.filter(
                name__icontains=request.GET.get("q"), is_active=True
            ).distinct()[:10]
            companies_names = []
            for each in companies:
                companies_names.append(each.name)
            if request.GET.get("register_name"):
                company = Company.objects.filter(
                    name=request.GET.get("register_name")
                ).first()
                if company:
                    each_obj = {}
                    each_obj["website"] = company.website
                    each_obj["company_type"] = company.company_type
                    each_obj["company_id"] = company.id
                    each_obj["company_address"] = company.address
                    each_obj["company_profile"] = company.profile
                    each_obj["company_profile_pic"] = company.profile_pic
                    data = {"company": each_obj}
                    return HttpResponse(json.dumps(data))
            data = {"response": companies_names}
            return HttpResponse(json.dumps(data))

        if request.user.is_active:
            if (
                request.user.is_company_recruiter
                and not request.user.is_admin
                and not request.user.has_perm("jobposts_edit")
            ):
                message = "You Don't have permission to create a new job"
                reason = "Please contact your agency admin"
                return render(
                    request,
                    "recruiter/recruiter_404.html",
                    {"message": message, "reason": reason},
                    status=404,
                )
            countries = Country.objects.all().order_by("name")
            skills = Skill.objects.all().exclude(status="InActive").order_by("name")
            functional_area = (
                FunctionalArea.objects.all().exclude(status="InActive").order_by("name")
            )
            industries = (
                Industry.objects.all().exclude(status="InActive").order_by("name")
            )
            qualifications = (
                Qualification.objects.all().exclude(status="InActive").order_by("name")
            )
            cities = City.objects.filter().exclude(status="Disabled")
            recruiters = User.objects.filter(company=request.user.company)
            if request.user.agency_admin or request.user.has_perm("jobposts_edit"):
                jobposts = JobPost.objects.filter(
                    job_type=status, user__company=request.user.company
                )
            else:
                jobposts = JobPost.objects.filter(job_type=status, user=request.user)

            clients = AgencyCompany.objects.filter(company=request.user.company)
            show_clients = True
            show_recruiters = True
            if request.user.is_agency_recruiter:
                show_clients = False if not clients else True
                show_recruiters = False if not recruiters else True
            return render(
                request,
                "recruiter/job/new.html",
                {
                    "job_types": JOB_TYPE,
                    "functional_area": functional_area,
                    "qualifications": qualifications,
                    "years": YEARS,
                    "months": MONTHS,
                    "industries": industries,
                    "countries": countries,
                    "skills": skills,
                    "jobposts": jobposts,
                    "cities": cities,
                    "status": status,
                    "agency_invoice_types": AGENCY_INVOICE_TYPE,
                    "agency_job_types": AGENCY_JOB_TYPE,
                    "recruiters": recruiters,
                    "clients": clients,
                    "show_clients": show_clients,
                    "show_recruiters": show_recruiters,
                },
            )
        else:
            message = "Sorry, Your account is not verified"
            reason = "Please verify your email id"
            return render(
                request,
                "recruiter/recruiter_404.html",
                {"message": message, "reason": reason},
                status=404,
            )
    validate_form = JobPostForm(request.POST, request.FILES, user=request.user)
    errors = retreving_form_errors(request, validate_form)
    if not errors:
        validate_post = validate_form.save(commit=False)
        save_job_post(validate_post, request)
        validate_form.save_m2m()
        adding_other_fields_data(request.POST, validate_post, request.user)
        c = {"job_post": validate_post, "user": request.user}
        t = loader.get_template("email/jobpost_notification.html")
        subject = "PeelJobs New JobPost"
        rendered = t.render(c)
        mto = ["anusha@micropyramid.com"]
        mfrom = settings.DEFAULT_FROM_EMAIL
        Memail(mto, mfrom, subject, rendered, True)
        data = {
            "error": False,
            "response": "New Post created",
            "post": validate_post.id,
        }
        return HttpResponse(json.dumps(data))
    data = {"error": True, "response": errors}
    return HttpResponse(json.dumps(data))


@recruiter_login_required
def edit_job(request, job_post_id):
    if request.user.agency_admin or request.user.has_perm("jobposts_edit"):
        job_post = JobPost.objects.filter(
            id=job_post_id, user__company=request.user.company
        ).first()
    else:
        job_post = JobPost.objects.filter(id=job_post_id, user=request.user).first()

    if request.method == "GET":
        if request.user.mobile_verified:
            if job_post:
                countries = Country.objects.all().order_by("name")
                skills = list(Skill.objects.filter(status="Active"))
                skills.extend(job_post.skills.filter(status="InActive"))

                industries = list(
                    Industry.objects.filter(status="Active").order_by("name")
                )
                industries.extend(job_post.industry.filter(status="InActive"))

                cities = list(City.objects.filter(status="Enabled").order_by("name"))
                cities.extend(job_post.location.filter(status="Disabled"))

                qualifications = list(
                    Qualification.objects.filter(status="Active").order_by("name")
                )
                qualifications.extend(
                    job_post.edu_qualification.filter(status="InActive")
                )

                recruiters = User.objects.filter(company=request.user.company)
                clients = AgencyCompany.objects.filter(company=request.user.company)

                functional_area = list(
                    FunctionalArea.objects.filter(status="Active").order_by("name")
                )
                functional_area.extend(
                    job_post.functional_area.filter(status="InActive")
                )
                fb_groups = FacebookPost.objects.filter(
                    job_post=job_post, page_or_group="group", post_status="Posted"
                ).order_by("-id")
                return render(
                    request,
                    "recruiter/job/edit.html",
                    {
                        "fb_groups": fb_groups,
                        "job_types": JOB_TYPE,
                        "qualifications": qualifications,
                        "functional_area": functional_area,
                        "years": YEARS,
                        "months": MONTHS,
                        "job_post": job_post,
                        "industries": industries,
                        "countries": countries,
                        "skills": skills,
                        "cities": cities,
                        "recruiters": recruiters,
                        "agency_invoice_types": AGENCY_INVOICE_TYPE,
                        "agency_job_types": AGENCY_JOB_TYPE,
                        "clients": clients,
                    },
                )
            else:
                message = "Sorry, No Job Posts Found"
                reason = "The URL may be misspelled or the job you're looking for is no longer available."
        else:
            message = "Sorry, Your mobile number is not verified"
            reason = "Please verify your mobile number"
        return render(
            request,
            "recruiter/recruiter_404.html",
            {"message": message, "reason": reason},
            status=404,
        )

    validate_form = JobPostForm(
        request.POST, request.FILES, instance=job_post, user=request.user
    )
    errors = retreving_form_errors(request, validate_form)
    if not errors:
        validate_post = validate_form.save(commit=False)
        save_job_post(validate_post, request)
        validate_form.save_m2m()
        validate_post.job_interview_location.clear()
        adding_other_fields_data(request.POST, validate_post, request.user)
        data = {
            "error": False,
            "response": "Jobpost Updated Successfully",
            "post": validate_post.id,
        }
        return HttpResponse(json.dumps(data))
    data = {"error": True, "response": errors}
    return HttpResponse(json.dumps(data))


@recruiter_login_required
def copy_job(request, status):
    if request.user.agency_admin or request.user.has_perm("jobposts_edit"):
        jobposts = JobPost.objects.filter(
            job_type=status, user__company=request.user.company
        )
        job_post = JobPost.objects.filter(
            id=request.GET.get("jobpost_id"), user__company=request.user.company
        ).first()
    else:
        jobposts = JobPost.objects.filter(job_type=status, user=request.user)
        job_post = JobPost.objects.filter(
            id=request.GET.get("jobpost_id"), user=request.user
        ).first()

    if request.method == "GET":
        if request.user.mobile_verified:
            if job_post:
                countries = Country.objects.all().order_by("name")
                skills = list(Skill.objects.filter(status="Active").order_by("name"))
                skills.extend(job_post.skills.filter(status="InActive"))

                cities = list(City.objects.filter(status="Enabled").order_by("name"))
                cities.extend(job_post.location.filter(status="Disabled"))

                industries = list(
                    Industry.objects.filter(status="Active").order_by("name")
                )
                industries.extend(job_post.industry.filter(status="InActive"))

                qualifications = list(
                    Qualification.objects.filter(status="Active").order_by("name")
                )
                qualifications.extend(
                    job_post.edu_qualification.filter(status="InActive")
                )

                recruiters = User.objects.filter(company=request.user.company)
                clients = AgencyCompany.objects.filter(company=request.user.company)

                functional_area = list(
                    FunctionalArea.objects.all()
                    .exclude(status="InActive")
                    .order_by("name")
                )
                functional_area.extend(
                    job_post.functional_area.filter(status="InActive")
                )

                return render(
                    request,
                    "recruiter/job/copy.html",
                    {
                        "job_types": JOB_TYPE,
                        "qualifications": qualifications,
                        "functional_area": functional_area,
                        "years": YEARS,
                        "months": MONTHS,
                        "job_post": job_post,
                        "industries": industries,
                        "countries": countries,
                        "skills": skills,
                        "jobposts": jobposts,
                        "cities": cities,
                        "status": status,
                        "recruiters": recruiters,
                        "agency_job_types": AGENCY_JOB_TYPE,
                        "agency_invoice_types": AGENCY_INVOICE_TYPE,
                        "clients": clients,
                    },
                )
            message = "Sorry, No Job Posts Found"
            reason = "The URL may be misspelled or the job you're looking for is no longer available."
            return render(
                request,
                "recruiter/recruiter_404.html",
                {"message_type": "404", "message": message, "reason": reason},
                status=404,
            )
        message = "Sorry, Your mobile number is not verified"
        reason = "Please verify your mobile number"
        return render(
            request,
            "recruiter/recruiter_404.html",
            {"message_type": "404", "message": message, "reason": reason},
            status=404,
        )

    validate_form = JobPostForm(request.POST, request.FILES, user=request.user)
    errors = retreving_form_errors(request, validate_form)
    if not errors:
        validate_post = validate_form.save(commit=False)
        save_job_post(validate_post, request)
        validate_form.save_m2m()
        adding_other_fields_data(request.POST, validate_post, request.user)
        c = {"job_post": validate_post, "user": request.user}
        t = loader.get_template("email/jobpost_notification.html")
        subject = "PeelJobs New JobPost"
        rendered = t.render(c)
        mto = ["anusha@micropyramid.com"]
        mfrom = settings.DEFAULT_FROM_EMAIL
        Memail(mto, mfrom, subject, rendered, True)
        data = {
            "error": False,
            "response": "Job Post Created Successfully",
            "post": validate_post.id,
        }
        return HttpResponse(json.dumps(data))
    return HttpResponse(json.dumps({"error": True, "response": errors}))


@recruiter_login_required
def view_job(request, job_post_id):
    if request.POST.get("post_message"):
        data = {
            "message": request.POST.get("message"),
            "message_from": request.user.id,
            "message_to": int(request.POST.get("message_to")),
            "created_on": datetime.now(),
            "job_id": int(request.POST.get("job_id")),
            "is_read": False,
        }
        msg_id = db.messages.insert(data)
        time = datetime.now().strftime("%b. %d, %Y, %l:%M %p")
        return HttpResponse(
            json.dumps(
                {
                    "error": False,
                    "message": request.POST.get("message"),
                    "msg_id": str(msg_id),
                    "time": time,
                }
            )
        )
    if request.POST.get("get_applicant"):
        if request.POST.get("user_type") == "resume_pool":
            user = AgencyResume.objects.filter(id=request.POST.get("user_id")).first()
            applicant = render_to_string(
                "recruiter/job/resume_applicant.html", {"user": user}
            )
        else:
            user = User.objects.filter(id=request.POST.get("user_id")).first()
            db.messages.update(
                {
                    "$and": [
                        {"message_to": request.user.id},
                        {"message_from": user.id},
                        {"job_id": int(job_post_id)},
                    ]
                },
                {"$set": {"is_read": True}},
                multi=True,
            )
            messages = db.messages.find(
                {
                    "$or": [
                        {
                            "$and": [
                                {"message_from": user.id},
                                {"message_to": request.user.id},
                                {"job_id": int(job_post_id)},
                            ]
                        },
                        {
                            "$and": [
                                {"message_to": user.id},
                                {"message_from": request.user.id},
                                {"job_id": int(job_post_id)},
                            ]
                        },
                    ]
                }
            )
            try:
                user_pic = user.profile_pic.url
            except:
                user_pic = user.photo
            try:
                profile_pic = request.user.profile_pic.url
            except:
                profile_pic = request.user.photo
            if not user_pic:
                user_pic = "https://cdn.peeljobs.com/dummy.jpg"
            if not profile_pic:
                profile_pic = "https://cdn.peeljobs.com/dummy.jpg"
            applicant = render_to_string(
                "recruiter/job/applicant_profile.html",
                {
                    "user": user,
                    "messages": list(messages),
                    "job_id": job_post_id,
                    "user_pic": user_pic,
                    "profile_pic": profile_pic,
                },
                request,
            )
        if user:
            return HttpResponse(json.dumps({"error": False, "profile": applicant}))
        return HttpResponse(
            json.dumps({"error": True, "response": "Profile Not Found!"})
        )
    if request.user.agency_admin:
        jobposts = JobPost.objects.filter(
            id=job_post_id, user__company=request.user.company
        )
    elif request.user.is_agency_recruiter:
        jobposts = JobPost.objects.filter(
            Q(user=request.user) | Q(agency_recruiters__in=[request.user])
        )
    else:
        jobposts = JobPost.objects.filter(id=job_post_id, user=request.user)
    if jobposts:
        jobpost = jobposts[0]
        all_applicants = (
            AppliedJobs.objects.filter(job_post=jobpost)
            .prefetch_related("user", "resume_applicant")
            .distinct()
        )
        shortlisted_applicants = all_applicants.filter(status="Shortlisted")
        rejected_applicants = all_applicants.filter(status="Rejected")
        selected_applicants = all_applicants.filter(status="Selected")
        process_applicants = all_applicants.filter(status="Process")
        pending_applicants = all_applicants.filter(status="Pending")
        if request.POST.get("search_value"):
            if request.POST.get("search_value") == "users":
                all_applicants = all_applicants.exclude(user=None)
                shortlisted_applicants = shortlisted_applicants.exclude(user=None)
                rejected_applicants = rejected_applicants.exclude(user=None)
                selected_applicants = selected_applicants.exclude(user=None)
                process_applicants = process_applicants.exclude(user=None)
                pending_applicants = pending_applicants.exclude(user=None)
            if request.POST.get("search_value") == "resume_pool":
                all_applicants = all_applicants.exclude(resume_applicant=None)
                shortlisted_applicants = shortlisted_applicants.exclude(
                    resume_applicant=None
                )
                rejected_applicants = rejected_applicants.exclude(resume_applicant=None)
                selected_applicants = selected_applicants.exclude(resume_applicant=None)
                process_applicants = process_applicants.exclude(resume_applicant=None)
                pending_applicants = pending_applicants.exclude(resume_applicant=None)
        search_location = request.POST.getlist("location")
        search_skills = request.POST.getlist("skills")
        if search_location or search_skills:
            all_applicants = all_applicants.filter(
                Q(user__current_city__id__in=search_location)
                | Q(user__skills__skill__id__in=search_skills)
            )
            shortlisted_applicants = shortlisted_applicants.filter(
                Q(user__current_city__id__in=search_location)
                | Q(user__skills__skill__id__in=search_skills)
            )
            rejected_applicants = rejected_applicants.filter(
                Q(user__current_city__id__in=search_location)
                | Q(user__skills__skill__id__in=search_skills)
            )
            selected_applicants = selected_applicants.filter(
                Q(user__current_city__id__in=search_location)
                | Q(user__skills__skill__id__in=search_skills)
            )
            process_applicants = process_applicants.filter(
                Q(user__current_city__id__in=search_location)
                | Q(user__skills__skill__id__in=search_skills)
            )
            pending_applicants = pending_applicants.filter(
                Q(user__current_city__id__in=search_location)
                | Q(user__skills__skill__id__in=search_skills)
            )
        # if request.user.agency_admin:
        #     work_logs = AgencyWorkLog.objects.filter(job_post=jobpost)
        # else:
        #     work_logs = AgencyWorkLog.objects.filter(user=request.user, job_post=jobpost)
        exclude_applicants = all_applicants.values_list("resume_applicant", flat=True)
        ids = filter(None, exclude_applicants)
        agency_resumes = AgencyResume.objects.filter(uploaded_by=request.user).exclude(
            id__in=ids
        )
        if request.POST.get("search_value") == "users":
            agency_resumes = []
        if request.POST.getlist("applicants"):
            validate_resume_applicant = ApplicantResumeForm(request.POST)
            if validate_resume_applicant.is_valid():
                for resume in request.POST.getlist("applicants"):
                    applied_jobs = AppliedJobs.objects.filter(
                        resume_applicant__id=resume,
                        job_post__id=request.POST.get("job_post"),
                    )
                    if not applied_jobs:
                        AppliedJobs.objects.create(
                            status=request.POST.get("status"),
                            resume_applicant_id=resume,
                            job_post_id=request.POST.get("job_post"),
                            ip_address=request.META["REMOTE_ADDR"],
                            user_agent=request.META["HTTP_USER_AGENT"],
                        )
                    else:
                        applied_jobs = applied_jobs[0]
                        applied_jobs.status = request.POST.get("status")
                        applied_jobs.save()
                data = {"error": False, "response": "JobPosts Added Successfully"}
                return HttpResponse(json.dumps(data))
            data = {"error": True, "response": validate_resume_applicant.errors}
            return HttpResponse(json.dumps(data))
        meta_title = meta_description = ""
        meta = db.meta_data.find_one({"name": "job_detail_page"})
        if meta:
            meta_title = Template(meta.get("meta_title")).render(
                Context({"job": jobpost})
            )
            meta_description = Template(meta.get("meta_description")).render(
                Context({"job": jobpost})
            )
        return render(
            request,
            "recruiter/job/view.html",
            {
                "jobpost": jobpost,
                "jobpost_assigned_status": AGENCY_RECRUITER_JOB_TYPE,
                "minified_url": jobpost.minified_url,
                "selected_applicants": selected_applicants,
                "shortlisted_applicants": shortlisted_applicants,
                "process_applicants": process_applicants,
                "pending_applicants": pending_applicants,
                "rejected_applicants": rejected_applicants,
                "agency_resumes": agency_resumes,
                "search_skills": search_skills if search_skills else "",
                "search_location": search_location if search_location else "",
                "meta_title": meta_title,
                "meta_description": meta_description,
            },
        )
    else:
        reason = "The URL may be misspelled or the job you're looking for is no longer available."
        return render(
            request,
            "recruiter/recruiter_404.html",
            {"message": "Sorry, No Job Posts Found", "reason": reason},
            status=404,
        )


@recruiter_login_required
def deactivate_job(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    if request.user.is_agency_admin or request.user == job_post.user:
        # need to delete job post on fb, twitter and linkedin
        posts = FacebookPost.objects.filter(job_post=job_post).exclude(
            post_status="Deleted"
        )
        for each in posts:
            del_jobpost_fb.delay(request.user.id, each.id)
            del_jobpost_peel_fb(request.user.id, each.id)
        posts = TwitterPost.objects.filter(job_post=job_post)
        for each in posts:
            del_jobpost_tw.delay(request.user.id, each.id)

        job_post.previous_status = job_post.status
        job_post.closed_date = datetime.now(timezone.utc)
        job_post.status = "Disabled"
        job_post.save()
        data = {"error": False, "response": "Job Post Deactivated"}
        return HttpResponse(json.dumps(data))
    data = {"error": True, "response": "You don't permissions to deactivate this Job"}
    return HttpResponse(json.dumps(data))


@recruiter_login_required
def delete_job(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id, user=request.user)
    posts = FacebookPost.objects.filter(job_post=job_post)
    for each in posts:
        del_jobpost_fb.delay(request.user.id, each.id)
        del_jobpost_peel_fb.delay(request.user.id, each.id)
    posts = TwitterPost.objects.filter(job_post=job_post)
    for each in posts:
        del_jobpost_tw.delay(request.user.id, each.id)

    job_post.status = "Disabled"
    job_post.closed_date = datetime.now(timezone.utc)
    job_post.save()

    data = {"error": False, "response": "Job Post deleted Successfully"}
    return HttpResponse(json.dumps(data))


@recruiter_login_required
def enable_job(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    job_post.status = "Pending"
    job_post.closed_date = None
    job_post.save()
    # postonpeel_fb.delay(request.user, job_post)
    # if job_post.post_on_fb:
    #     fbpost.delay(request.user, job_post)
    #     postonpage.delay(request.user, job_post)
    #     # need to check this condition
    #     # if emp['peelfbpost']:
    # posts = FacebookPost.objects.filter(job_post=job_post, page_or_group='group', is_active=True, post_status='Deleted')
    # for group in posts:
    #     fb_group = FacebookGroup.objects.get(user=request.user, group_id=group.page_or_group_id)
    #     is_active = True
    #     postongroup.delay(request.user, job_post, fb_group, is_active)
    #     # need to get accetoken for peeljobs twitter page
    # if job_post.post_on_tw:
    #     postontwitter.delay(request.user, job_post, 'Profile')
    #     # postontwitter(request.user, post, 'Page')

    data = {"error": False, "response": "Job Post enabled Successfully"}
    return HttpResponse(json.dumps(data))


@recruiter_login_required
def applicants(request, job_post_id):
    if request.method == "GET":
        reason = "The URL may be misspelled or the page you're looking for is no longer available."
        return render(
            request,
            "recruiter/recruiter_404.html",
            {
                "message_type": "404",
                "message": "Looks like you can't access this page",
                "reason": reason,
            },
            status=404,
        )
    jobpost = JobPost.objects.filter(id=job_post_id)
    if jobpost:
        user_id = request.POST.get("user_id").split("user_status_")[-1]
        if request.POST.get("type") == "resume":
            user = (
                AppliedJobs.objects.filter(
                    resume_applicant_id=user_id, job_post_id=job_post_id
                )
                .prefetch_related("resume_applicant")
                .first()
            )
        else:
            user = (
                AppliedJobs.objects.filter(user_id=user_id, job_post_id=job_post_id)
                .prefetch_related("user")
                .first()
            )
        prev_status = user.status
        user.status = request.POST.get("status")
        user.save()
        next_count = AppliedJobs.objects.filter(
            job_post_id=job_post_id, status=request.POST.get("status")
        ).count()
        prev_count = AppliedJobs.objects.filter(
            job_post_id=job_post_id, status=prev_status
        ).count()
        temp = loader.get_template("email/applicant_apply_job.html")
        subject = "Application Status - PeelJobs"
        if request.POST.get("type") == "resume":
            mto = [user.resume_applicant.email]
        else:
            mto = [user.user.email]
        if request.POST.get("type") == "resume":
            names_dict = {
                "job_post": jobpost[0],
                "user_email": user.resume_applicant.email,
                "user_status": user.status,
                "name": user.resume_applicant.candidate_name,
            }
        else:
            names_dict = {
                "job_post": jobpost[0],
                "user_email": user.user.email,
                "user_status": user.status,
                "name": user.user.get_full_name(),
            }
        rendered = temp.render(names_dict)
        Memail(mto, settings.DEFAULT_FROM_EMAIL, subject, rendered, False)
        data = {
            "error": False,
            "response": "Applicant Status changed to " + user.status,
            "prev_count": prev_count,
            "next_count": next_count,
            "prev_status": prev_status,
            "next_status": user.status,
        }
        return HttpResponse(json.dumps(data))
    return HttpResponse(
        json.dumps({"error": True, "response": "Something went wrong!"})
    )


@recruiter_login_required
def preview_job(request, job_post_id):
    if request.user.is_agency_recruiter:
        job_post = JobPost.objects.filter(
            id=job_post_id, user__company=request.user.company
        )
        if not request.user.agency_admin:
            job_post = job_post.filter(
                Q(user=request.user) | Q(agency_recruiters__in=[request.user])
            )
    else:
        job_post = JobPost.objects.filter(id=job_post_id, user=request.user)
    if job_post:
        if job_post[0].status == "Pending":
            return render(request, "recruiter/job/view.html", {"jobpost": job_post[0]})
    message_type = "404"
    message = "No Job Preview Available"
    reason = "The URL may be misspelled or the job you're looking for is no longer available."
    return render(
        request,
        "recruiter/recruiter_404.html",
        {"message_type": message_type, "message": message, "reason": reason},
        status=404,
    )


@recruiter_login_required
def getout(request):
    logout(request)
    return HttpResponseRedirect("/recruiter/login/")


def create_slug(tempslug):
    tempslug = tempslug.split("@")
    if tempslug[1] != "gmail.com":
        user = tempslug[1].split(".")[0] + "-" + tempslug[0]
        return user
    slugcount = 0
    tempslug = tempslug[0]
    while True:
        try:
            User.objects.get(username=tempslug)
            slugcount = slugcount + 1
            if isinstance(tempslug.split("-")[-1], int):
                tempslug = tempslug.split("-")[0] + str(tempslug.split("-")[-1] + 1)
            else:
                tempslug = tempslug + str(slugcount)
        except ObjectDoesNotExist:
            return tempslug


def get_autocomplete(request):
    companies = Company.objects.filter(
        name__icontains=request.GET.get("q"),
        company_type="Company",
        id__in=User.objects.filter(is_admin=False).values_list("company", flat=True),
    ).distinct()[:10]
    companies_names = []
    for each in companies:
        companies_names.append(each.name)
    if request.GET.get("register_name"):
        company = Company.objects.filter(name=request.GET.get("register_name")).first()
        if company:
            each_obj = {}
            each_obj["website"] = company.website
            each_obj["company_type"] = company.company_type
            each_obj["company_id"] = company.id
            each_obj["company_id"] = company.id
            each_obj["company_address"] = company.address
            each_obj["company_profile"] = company.profile
            data = {"company": each_obj}
            return data
    data = {"response": companies_names}
    return data


def new_user(request):  # pragma: no mccabe
    if request.method == "GET":
        if request.GET.get("q"):
            data = get_autocomplete(request)
            return HttpResponse(json.dumps(data))
        else:
            if request.user.is_authenticated:
                if request.user.is_staff:
                    return HttpResponseRedirect("/dashboard/")
                elif request.user.is_jobseeker:
                    return HttpResponseRedirect("/profile/")
                elif request.user.is_recruiter:
                    return HttpResponseRedirect(reverse("recruiter:list"))
                elif request.user.is_agency_recruiter:
                    return HttpResponseRedirect(reverse("agency:list"))
            meta_title = meta_description = h1_tag = ""
            meta = list(db.meta_data.find({"name": "recruiter_login"}))
            if meta:
                meta_title = Template(meta[0]["meta_title"]).render(Context({}))
                meta_description = Template(meta[0]["meta_description"]).render(
                    Context({})
                )
                h1_tag = Template(meta[0]["h1_tag"]).render(Context({}))
            return render(
                request,
                "recruiter/register.html",
                {
                    "meta_title": meta_title,
                    "meta_description": meta_description,
                    "h1_tag": h1_tag,
                },
            )

    if request.method == "POST":
        show_errors = False
        companies = []
        company_form = ""
        if request.POST.get("company_id"):
            companies = Company.objects.filter(id=request.POST.get("company_id"))
        if request.POST.get("client_type") == "company":
            if companies:
                company_form = Company_Form(request.POST, instance=companies[0])
            else:
                company_form = Company_Form(request.POST)
            user_obj = User_Form(request.POST)
            if company_form.is_valid() and user_obj.is_valid():
                show_errors = True
        else:
            user_obj = User_Form(request.POST)
            show_errors = True if user_obj.is_valid() else False
        if show_errors:
            payload = {
                "secret": "6LdZcgkTAAAAAGkY3zbzO4lWhqCStbWUef_6MWW-",
                "response": request.POST.get("g-recaptcha-response"),
                "remoteip": request.META.get("REMOTE_ADDR"),
            }
            response = ""
            while response == "":
                try:
                    response = requests.get(
                        "https://www.google.com/recaptcha/api/siteverify",
                        params=payload,
                    )
                except:
                    time.sleep(5)
            if json.loads(response.text)["success"]:
                if request.POST.get("client_type") == "company":
                    if company_form.is_valid():
                        if companies:
                            each_company = companies[0]
                            each_company.name = request.POST["name"]
                            each_company.website = request.POST["website"]
                            each_company.company_type = "Consultant"
                            each_company.save()
                            users = User.objects.filter(company=each_company)
                            users.update(user_type="AR")
                        else:
                            each_company = Company.objects.create(
                                name=request.POST["name"],
                                website=request.POST["website"],
                                company_type="Consultant",
                                slug=slugify(request.POST["name"]),
                                email=request.POST.get("email"),
                                created_from="register",
                            )
                    else:
                        data = {"error": True, "message": company_form.errors}
                        return HttpResponse(json.dumps(data))

                user_obj = User_Form(request.POST)
                if user_obj.is_valid():
                    username = request.POST["username"]
                    # tempslug = slugify(user_name)
                    # username = create_slug(request.POST['email'])
                    user_obj = User.objects.create(
                        first_name=username,
                        email=request.POST["email"],
                        username=username,
                        mobile=request.POST["mobile"],
                        profile_updated=datetime.now(timezone.utc),
                    )
                    user_obj.user_type = "RR"
                    user_obj.set_password(request.POST["password"])
                    user_obj.is_active = False
                    user_obj.email_notifications = True
                    user_obj.mobile_verified = True
                    user_obj.profile_updated = datetime.now(timezone.utc)
                    if (
                        "client_type" in request.POST
                        and request.POST["client_type"] == "company"
                    ):
                        user_obj.company_id = each_company.id
                        user_obj.user_type = "AA"
                        user_obj.agency_admin = True
                        user_obj.company.company_type = "Consultant"
                        user_obj.company.save()

                    user_obj.is_admin = True
                    while True:
                        random_code = get_random_string(length=10)
                        u = User.objects.filter(activation_code__iexact=random_code)
                        if not u:
                            break
                    while True:
                        unsub_code = get_random_string(length=10)
                        u = User.objects.filter(unsubscribe_code__iexact=random_code)
                        if not u:
                            break
                    user_obj.activation_code = random_code
                    user_obj.unsubscribe_code = unsub_code
                    user_obj.save()

                    temp = loader.get_template("recruiter/email/recruiter_account.html")
                    subject = "PeelJobs Recruiter Account Activation"
                    mto = [request.POST.get("email")]
                    mfrom = settings.DEFAULT_FROM_EMAIL
                    if (
                        "client_type" in request.POST
                        and request.POST["client_type"] == "company"
                    ):
                        url = (
                            request.scheme
                            + "://"
                            + request.META["HTTP_HOST"]
                            + "/agency/activation/"
                            + str(user_obj.activation_code)
                            + "/"
                        )
                    else:
                        url = (
                            request.scheme
                            + "://"
                            + request.META["HTTP_HOST"]
                            + "/recruiter/activation/"
                            + str(user_obj.activation_code)
                            + "/"
                        )
                    c = {
                        "activate_url": url,
                        "user": user_obj,
                        "user_password": request.POST["password"],
                    }
                    rendered = temp.render(c)
                    Memail(mto, mfrom, subject, rendered, False)

                    UserEmail.objects.create(
                        user=user_obj, email=request.POST["email"], is_primary=True
                    )

                    user = authenticate(
                        username=request.POST["email"],
                        password=request.POST["password"],
                    )
                    if not request.user.is_authenticated:
                        if not hasattr(user_obj, "backend"):
                            for backend in settings.AUTHENTICATION_BACKENDS:
                                if user_obj == load_backend(backend).get_user(
                                    user_obj.id
                                ):
                                    user_obj.backend = backend
                                    break
                        if hasattr(user_obj, "backend"):
                            login(request, user_obj)

                    # user = authenticate(username=request.POST["email"])
                    # print (user, request.POST["email"])
                    # login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    data = {
                        "error": False,
                        "message": "An email has been sent to your email id, Please activate your account",
                        "is_company_recruiter": request.user.is_company_recruiter(),
                    }
                    return HttpResponse(json.dumps(data))
            else:
                data = {"error": True, "captcha_response": "Choose Correct Captcha"}
                return HttpResponse(json.dumps(data))
        else:
            errors = (user_obj.errors).copy()
            if company_form:
                errors.update(company_form.errors)
            data = {"error": True, "message": errors}
            return HttpResponse(json.dumps(data))

    else:
        return HttpResponse("")


def account_activation(request, user_id):
    user = User.objects.filter(activation_code__iexact=user_id).first()
    if user:
        user.is_active = True
        user.email_veified = True
        user.last_login = datetime.now()
        user.activation_code = ""
        user.save()

        user_obj = authenticate(username=user.email)
        if not request.user.is_authenticated:
            if not hasattr(user, "backend"):
                for backend in settings.AUTHENTICATION_BACKENDS:
                    if user == load_backend(backend).get_user(user.id):
                        user.backend = backend
                        break
            if hasattr(user, "backend"):
                login(request, user)

        if user.mobile_verified:
            if user.is_agency_recruiter:
                return HttpResponseRedirect(reverse("agency:index"))
            return HttpResponseRedirect(reverse("recruiter:index"))
        return render(request, "recruiter/user/mobile_verify.html")
    message = "Looks like User Does not exists with email id"
    reason = "The URL may be misspelled or the user you're looking for is no longer available."
    return render(
        request,
        "recruiter/recruiter_404.html",
        {"message_type": "404", "message": message, "reason": reason},
        status=404,
    )


def user_password_reset(request):
    if request.method == "POST":
        if request.POST.get("email"):
            user = User.objects.filter(email=request.POST.get("email"))
            if user and user[0].is_jobseeker:
                data = {
                    "error": True,
                    "email": "User Already registered as a Applicant",
                }
                return HttpResponse(json.dumps(data))
                # if user and user[0].is_staff:
                #     data = {"error": True, "email": "User Already registered as a Admin"}
                return HttpResponse(json.dumps(data))
            if user:
                usr = User.objects.get(email=request.POST.get("email"))
                randpwd = rand_string(size=10).lower()
                if usr.is_active:
                    usr.set_password(randpwd)
                    usr.save()
                    temp = loader.get_template("email/subscription_success.html")
                else:
                    temp = loader.get_template("recruiter/email/activate.html")
                subject = "Password Reset - PeelJobs"
                mto = [request.POST.get("email")]
                mfrom = settings.DEFAULT_FROM_EMAIL
                try:
                    url = (
                        request.scheme
                        + "://"
                        + request.META["HTTP_HOST"]
                        + "/user/set_password/"
                        + str(usr.id)
                        + "/"
                        + str(randpwd)
                        + "/"
                    )
                except:
                    url = "https://peeljobs.com" + reverse("recruiter:new_user")
                if not usr.is_active:
                    if usr.company:
                        url = (
                            request.scheme
                            + "://"
                            + request.META["HTTP_HOST"]
                            + "/agency/activation/"
                            + str(usr.activation_code)
                            + "/"
                        )
                    else:
                        url = (
                            request.scheme
                            + "://"
                            + request.META["HTTP_HOST"]
                            + "/recruiter/activation/"
                            + str(usr.activation_code)
                            + "/"
                        )
                c = {
                    "randpwd": randpwd,
                    "user": usr,
                    "redirect_url": url,
                    "activate_url": url,
                }
                rendered = temp.render(c)
                user_active = True if usr.is_active else False
                Memail(mto, mfrom, subject, rendered, user_active)

                usr.last_password_reset_on = datetime.now(timezone.utc)
                usr.save()

                data = {
                    "error": False,
                    "info": "Sent a link to your email to reset your password"
                    if usr.is_active
                    else "An email has been sent to your email id, Please activate your account",
                }
                return HttpResponse(json.dumps(data))
            else:
                data = {
                    "error": True,
                    "email": "User With this Email ID not Registered",
                }
                return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "email": "Email can not be blank"}
            return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "email": "Method is not supported"}
        return HttpResponse(json.dumps(data))


@recruiter_login_required
def change_password(request):
    if request.method == "POST":
        validate_changepassword = ChangePasswordForm(request.POST, user=request.user)
        if validate_changepassword.is_valid():
            user = request.user
            user.set_password(request.POST["newpassword"])
            user.save()
            update_session_auth_hash(request, request.user)
            logout(request)
            return HttpResponse(
                json.dumps({"error": False, "message": "Password changed successfully"})
            )
        return HttpResponse(
            json.dumps({"error": True, "response": validate_changepassword.errors})
        )
    return render(request, "recruiter/user/change_password.html")


@recruiter_login_required
def verify_mobile(request):
    if request.user.mobile_verified:
        if request.user.is_agency_recruiter:
            return HttpResponseRedirect(reverse("recruiter:index"))
        return HttpResponseRedirect(reverse("agency:index"))
    if request.method == "POST":
        validate_mobile = MobileVerifyForm(request.POST)
        if validate_mobile.is_valid():
            user = request.user
            password_reset_diff = int(
                (datetime.now() - request.user.last_mobile_code_verified_on).seconds
            )
            if password_reset_diff > 600:
                return HttpResponse(
                    json.dumps(
                        {
                            "error": True,
                            "response_message": "OTP Is Expired, Please request new OTP",
                        }
                    )
                )
            if str(request.POST["mobile_verification_code"]) != str(
                request.user.mobile_verification_code
            ):
                return HttpResponse(
                    json.dumps(
                        {
                            "error": True,
                            "response": {
                                "mobile_verification_code": "Otp didn't match, Try again later"
                            },
                        }
                    )
                )
            user.mobile_verified = True
            user.save()
            return HttpResponse(
                json.dumps({"error": False, "message": "Mobile Verified successfully"})
            )
        return HttpResponse(
            json.dumps({"error": True, "response": validate_mobile.errors})
        )
    return render(request, "recruiter/user/mobile_verify.html")


@recruiter_login_required
def send_mobile_verification_code(request):
    if request.user.mobile_verified:
        if request.user.is_agency_recruiter:
            return HttpResponseRedirect(reverse("recruiter:index"))
        return HttpResponseRedirect(reverse("agency:index"))

    if request.method == "POST":
        password_reset_diff = int(
            (datetime.now() - request.user.last_mobile_code_verified_on).seconds
        )
        if password_reset_diff <= 300:
            return HttpResponse(
                json.dumps(
                    {
                        "error": True,
                        "message": "OTP Already sent to you, Please request new OTP",
                    }
                )
            )
        user = request.user
        random_code = rand_string(size=6)
        # message = 'Hello ' + request.user.username + ', An OTP ' + random_code + \
        #     ' for your Peeljobs recruiter account, Please Confirm and Proceed'
        # data = {"username": settings.BULK_SMS_USERNAME, "password": settings.BULK_SMS_PASSWORD,
        #         "from": settings.BULK_SMS_FROM, "to": user.mobile, "message": message}
        # requests.get("https://182.18.160.225/index.php/api/bulk-sms", params=data)
        # response = requests.get(
        #     'http://182.18.160.225/index.php/api/bulk-sms?username=micropyramid&password=p4rti2yka&from=PEELJB&to='+str(user.mobile)+'&message='+message)
        user.mobile_verification_code = random_code
        user.last_mobile_code_verified_on = datetime.now(timezone.utc)
        user.save()
        return HttpResponse(
            json.dumps(
                {"error": False, "message": "An OTP sent to your mobile successfully"}
            )
        )


@recruiter_login_required
def user_profile(request):
    countries = Country.objects.filter()
    if request.method == "POST":
        user = request.user
        if "profile_pic" in request.FILES:
            logo = request.FILES.get("profile_pic")
            sup_formates = ["image/jpeg", "image/png"]
            ftype = logo.content_type
            if str(ftype) in sup_formates:
                user.profile_pic = logo
                user.save()
                data = {"error": False, "data": "Profile Pic Uploaded Successfully"}
                return HttpResponse(json.dumps(data))
            data = {
                "error": True,
                "data": "Upload a valid Image format, Ex: PNG, JPEG, JPG",
            }
            return HttpResponse(json.dumps(data))
        data = {"error": True, "data": "Please Upload Profile Pic"}
        return HttpResponse(json.dumps(data))
    user = User.objects.filter(id=request.user.id).prefetch_related(
        "technical_skills", "industry", "functional_area"
    )
    return render(
        request,
        "recruiter/user/profile.html",
        {"countries": countries, "user": user[0]},
    )


def index(request):
    print(settings.AM_PASS_KEY)
    if request.user.is_authenticated:
        if request.user.is_staff:
            return HttpResponseRedirect("/dashboard/")
        elif request.user.is_recruiter:
            return HttpResponseRedirect(reverse("recruiter:list"))
        elif request.user.is_agency_recruiter:
            return HttpResponseRedirect(reverse("agency:list"))
        elif request.user.is_jobseeker:
            return HttpResponseRedirect("/")

    if request.method == "POST":
        user = authenticate(
            username=request.POST.get("email"), password=request.POST.get("password")
        )
        if user is not None:
            if user.is_jobseeker or user.is_staff:
                data = {
                    "error": True,
                    "message": "You have registered as "
                    + ("Job Seeker" if user.is_jobseeker else "Admin")
                    + " and you can't login as Employer",
                }
                return HttpResponse(json.dumps(data))

            if user.is_active:
                user_login = False
                # if not user.mobile_verified:
                #     password_reset_diff = int(
                #         (datetime.now() - user.last_mobile_code_verified_on).seconds
                #     )
                #     if password_reset_diff > 600:
                #         random_code = rand_string(size=6)
                #         message = (
                #             "Hello "
                #             + user.username
                #             + ", An OTP "
                #             + random_code
                #             + " for your Peeljobs recruiter account, Please Confirm and Proceed"
                #         )

                #         data = {
                #             "username": settings.BULK_SMS_USERNAME,
                #             "password": settings.BULK_SMS_PASSWORD,
                #             "from": settings.BULK_SMS_FROM,
                #             "to": user.mobile,
                #             "message": message,
                #         }
                #         # requests.get("http://182.18.160.225/index.php/api/bulk-sms", params=data)
                #         requests.get(
                #             "http://sms.9sm.in/rest/services/sendSMS/sendGroupSms?AUTH_KEY="
                #             + str(settings.SMS_AUTH_KEY)
                #             + "&message="
                #             + str(message)
                #             + "&senderId="
                #             + str(settings.BULK_SMS_FROM)
                #             + "&routeId=1&mobileNos="
                #             + str(user.mobile)
                #             + "&smsContentType=english"
                #         )

                #         user.mobile_verification_code = random_code
                #         user.mobile_verified = False
                #         user.save()
                #     user.is_login = True
                #     user_login = True
                #     user.profile_completeness = user.profile_completion_percentage
                #     user.save()
                login(request, user)
                data = {"error": False, "is_login": user_login}
                if user.is_company_recruiter:
                    data["redirect_url"] = "/recruiter/job/list/"
                else:
                    data["redirect_url"] = "/agency/job/list/"
                if request.POST.get("next"):
                    data["redirect_url"] = request.POST.get("next")
            else:
                login(request, user)
                temp = loader.get_template("recruiter/email/activate.html")
                if user.company:
                    url = (
                        request.scheme
                        + "://"
                        + request.META["HTTP_HOST"]
                        + "/agency/activation/"
                        + str(user.activation_code)
                        + "/"
                    )
                else:
                    url = (
                        request.scheme
                        + "://"
                        + request.META["HTTP_HOST"]
                        + "/recruiter/activation/"
                        + str(user.activation_code)
                        + "/"
                    )
                c = {"activate_url": url, "user": user}
                rendered = temp.render(c)
                Memail(
                    [request.POST.get("email")],
                    settings.DEFAULT_FROM_EMAIL,
                    "PeelJobs Recruiter Account Activation",
                    rendered,
                    False,
                )
                data = {
                    "error": True,
                    "is_login": True,
                    "is_company_recruiter": user.is_company_recruiter(),
                    "message": "Your account is inactive, We Have sent a confirmation mail to your registered Email ID.",
                }
        else:
            data = {
                "error": True,
                "message": "Your email and/or password were incorrect.",
            }
        return HttpResponse(json.dumps(data))
    meta_title = meta_description = h1_tag = ""
    meta = list(db.meta_data.find({"name": "post_job"}))
    if meta:
        meta_title = Template(meta[0]["meta_title"]).render(Context({}))
        meta_description = Template(meta[0]["meta_description"]).render(Context({}))
        h1_tag = Template(meta[0]["h1_tag"]).render(Context({}))
    return render(
        request,
        "recruiter/login.html",
        {
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
        },
    )


@recruiter_login_required
def edit_profile(request):
    if request.method == "GET":
        functional_areas = FunctionalArea.objects.all()
        user = User.objects.filter(id=request.user.id).prefetch_related(
            "technical_skills", "industry", "functional_area"
        )
        return render(
            request,
            "recruiter/user/details.html",
            {
                "skills": Skill.objects.all(),
                "industries": Industry.objects.all(),
                "functional_areas": functional_areas,
                "martial_status": MARTIAL_STATUS,
                "countries": Country.objects.all(),
                "cities": City.objects.all().select_related("state", "state__country"),
                "states": State.objects.all().select_related("country"),
                "user": user[0],
            },
        )
    validate_user = PersonalInfoForm(request.POST, request.FILES, instance=request.user)
    user_mobile = request.user.mobile
    if validate_user.is_valid():
        user = validate_user.save(commit=False)
        if request.FILES.get("profile_pic"):
            user.profile_pic = request.FILES.get("profile_pic")
        if request.POST.get("gender"):
            user.gender = request.POST.get("gender")
        if request.POST.get("dob"):
            dob = datetime.strptime(request.POST.get("dob"), "%m/%d/%Y").strftime(
                "%Y-%m-%d"
            )
            user.dob = dob
        else:
            user.dob = None
        user.show_email = request.POST.get("show_email") == "on"
        user.email_notifications = request.POST.get("email_notifications") == "on"

        user.city = City.objects.get(id=request.POST["city"])
        user.state = State.objects.get(id=request.POST["state"])

        # companies = Company.objects.filter(name=request.POST['name'], website=request.POST['website'])
        # if companies:
        #     company = companies[0]
        # else:
        #     company = Company.objects.create(name=request.POST['name'], website=request.POST['website'], company_type=request.POST['company_type'])
        # user.company = company

        user_login = False
        password_reset_diff = int(
            (datetime.now() - user.last_mobile_code_verified_on).seconds
        )
        # if not user.mobile_verified:
        #     if password_reset_diff > 600:
        #         random_code = rand_string(size=6)
        #         message = (
        #             "Hello "
        #             + request.user.username
        #             + ", An OTP "
        #             + random_code
        #             + " for your Peeljobs recruiter account, Please Confirm and Proceed"
        #         )
        #         data = {
        #             "username": settings.BULK_SMS_USERNAME,
        #             "password": settings.BULK_SMS_PASSWORD,
        #             "from": settings.BULK_SMS_FROM,
        #             "to": request.POST.get("mobile"),
        #             "message": message,
        #         }
        #         # requests.get("http://182.18.160.225/index.php/api/bulk-sms", params=data)
        #         requests.get(
        #             "http://sms.9sm.in/rest/services/sendSMS/sendGroupSms?AUTH_KEY="
        #             + str(settings.SMS_AUTH_KEY)
        #             + "&message="
        #             + str(message)
        #             + "&senderId="
        #             + str(settings.BULK_SMS_FROM)
        #             + "&routeId=1&mobileNos="
        #             + str(request.POST.get("mobile"))
        #             + "&smsContentType=english"
        #         )

        #         user.mobile_verification_code = random_code
        #         user.mobile_verified = False
        #         user_login = True
        #         user.mobile = request.POST["mobile"]
        #         user.last_mobile_code_verified_on = datetime.now(timezone.utc)
        #         message = "Your Details Updated Successfully"
        #     else:
        #         user.mobile = user_mobile
        #         message = "An otp has been sent to you in the past 1 week, Please Verify Your Mobile Number"
        # else:
        #     if user.mobile == user_mobile:
        #         user.mobile = user_mobile
        #         message = "Your Details Updated Successfully"
        #     else:
        #         message = "Mobile num can't be change within a week"
        user.marital_status = request.POST.get("marital_status", "")
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name", "")
        user.address = request.POST.get("address")
        user.permanent_address = request.POST.get("permanent_address", "")
        user.technical_skills.clear()
        user.industry.clear()
        user.functional_area.clear()
        user.technical_skills.add(*request.POST.getlist("technical_skills"))
        user.industry.add(*request.POST.getlist("industry"))
        user.functional_area.add(*request.POST.getlist("functional_area"))
        user.profile_completeness = user.profile_completion_percentage
        user.save()
        data = {"error": False, "response": message, "is_login": user_login}
        return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "response": validate_user.errors}
        return HttpResponse(json.dumps(data))


@recruiter_login_required
def twitter_login(request):
    TW_APP_KEY = "iBFgK2szpfRgj0ayv3YFqDs5g"
    TW_APP_SECURE = "H0C0q9qMWHMHakRmIUprdpGUKtvPRuZ19C3qeEWMfmJg9stCw9"

    if "oauth_verifier" in request.GET:
        oauth_verifier = request.GET["oauth_verifier"]
        twitter = Twython(
            TW_APP_KEY,
            TW_APP_SECURE,
            request.session["OAUTH_TOKEN"],
            request.session["OAUTH_TOKEN_SECRET"],
        )
        final_step = twitter.get_authorized_tokens(oauth_verifier)
        if final_step.get("oauth_token_secret"):
            twitter = Twython(
                TW_APP_KEY,
                TW_APP_SECURE,
                final_step["oauth_token"],
                final_step["oauth_token_secret"],
            )
            followers = twitter.get_followers_list(
                screen_name=final_step["screen_name"]
            )
            friends = twitter.get_friends_list(screen_name=final_step["screen_name"])
            if not request.user.is_tw_connected:
                Twitter.objects.create(
                    user=request.user,
                    twitter_id=final_step["user_id"],
                    screen_name=final_step["screen_name"],
                    oauth_token=final_step["oauth_token"],
                    oauth_secret=final_step["oauth_token_secret"],
                )

            add_twitter_friends_followers.delay(request.user.id, friends, followers)
            return HttpResponseRedirect(reverse("recruiter:index"))
        message_type = "Sorry,"
        message = "We didnt find your Twitter Account"
        reason = "Please verify your details and try again"
        email = settings.DEFAULT_FROM_EMAIL
        number = settings.CONTACT_NUMBER
        return render(
            request,
            "recruiter/recruiter_404.html",
            {
                "message_type": message_type,
                "message": message,
                "reason": reason,
                "email": email,
                "number": number,
            },
            status=404,
        )
    else:
        twitter = Twython(TW_APP_KEY, TW_APP_SECURE)
        url = (
            request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("recruiter:twitter_login")
        )
        auth = twitter.get_authentication_tokens(callback_url=url)
        request.session["OAUTH_TOKEN"] = auth["oauth_token"]
        request.session["OAUTH_TOKEN_SECRET"] = auth["oauth_token_secret"]
        return HttpResponseRedirect(auth["auth_url"])


def google_login(request):
    if "code" in request.GET:
        params = {
            "grant_type": "authorization_code",
            "code": request.GET.get("code"),
            "redirect_uri": request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("recruiter:google_login"),
            "client_id": settings.GP_CLIENT_ID,
            "client_secret": settings.GP_CLIENT_SECRET,
        }
        info = requests.post("https://accounts.google.com/o/oauth2/token", data=params)
        info = info.json()
        if not info.get("access_token"):
            return render(
                request,
                "404.html",
                {
                    "message_type": "Sorry,",
                    "message": "Your session has been expired",
                    "reason": "Please kindly try again to update your profile",
                    "email": settings.DEFAULT_FROM_EMAIL,
                    "number": settings.CONTACT_NUMBER,
                },
            )
        url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {"access_token": info["access_token"]}
        kw = dict(params=params, headers={}, timeout=60)
        response = requests.request("GET", url, **kw)
        user_document = response.json()
        email_matches = UserEmail.objects.filter(email__iexact=user_document["email"])
        link = "https://plus.google.com/" + user_document["id"]
        picture = user_document.get("picture", "")
        dob = user_document.get("birthday", "")
        gender = user_document.get("gender", "")
        link = user_document.get("link", link)
        if email_matches:
            user = email_matches[0].user
            if user.is_recruiter or user.is_agency_recruiter:
                google, created = Google.objects.get_or_create(
                    user=user,
                    google_url=link,
                    verified_email=user_document.get("verified_email", ""),
                    google_id=user_document.get("id", ""),
                    family_name=user_document.get("family_name", ""),
                    name=user_document.get("name", ""),
                    given_name=user_document.get("given_name", ""),
                    dob=dob,
                    email=user_document.get("email", ""),
                    gender=gender,
                    picture=picture,
                )
                if not created:
                    google.google_url = link
                    google.verified_email = user_document.get("verified_email", "")
                    google.google_url = link
                    google.google_id = user_document.get("id", "")
                    google.family_name = user_document.get("family_name", "")
                    google.name = user_document.get("name", "")
                    google.given_name = user_document.get("given_name", "")
                    google.dob = dob
                    google.email = user_document.get("email", "")
                    google.gender = gender
                    google.picture = picture
                    google.save()
                user = authenticate(username=user.username)
                user.is_active = True
                user.save()
                login(request, user)
                return HttpResponseRedirect(reverse("recruiter:index"))
            else:
                return HttpResponseRedirect(
                    reverse("recruiter:new_user")
                    + "?invalid=Only Recruiters and Agencies are allowed to log in."
                )
        else:
            return HttpResponseRedirect(
                reverse("recruiter:new_user")
                + "?invalid=Sorry, User not found with this mail."
            )
    else:
        rty = (
            "https://accounts.google.com/o/oauth2/auth?client_id="
            + settings.GP_CLIENT_ID
            + "&response_type=code&scope="
        )
        rty += (
            "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email "
            + "https://www.googleapis.com/auth/contacts.readonly"
        )
        rty += (
            "&redirect_uri="
            + request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("recruiter:google_login")
            + "&state=1235dfghjkf123"
        )
        return HttpResponseRedirect(rty)


@recruiter_login_required
def google_connect(request):
    if "code" in request.GET:
        code = request.GET.get("code")
        params = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("recruiter:google_connect"),
            "client_id": settings.GP_CLIENT_ID,
            "client_secret": settings.GP_CLIENT_SECRET,
        }
        info = requests.post("https://accounts.google.com/o/oauth2/token", data=params)
        info = info.json()
        if info.get("access_token"):
            url = "https://www.googleapis.com/oauth2/v1/userinfo"
            params = {"access_token": info["access_token"]}
            headers = {}
            args = dict(params=params, headers=headers, timeout=60)
            response = requests.request("GET", url, **args)
            user_document = response.json()
            link = "https://plus.google.com/" + user_document.get("id", "")
            picture = user_document.get("picture", "")
            dob = user_document.get("birthday", "")
            gender = user_document.get("gender", "")
            link = user_document.get("link", link)

            request.session["google"] = user_document("id", "")

            if not request.user.is_gp_connected:
                Google.objects.create(
                    user=request.user,
                    google_url=link,
                    verified_email=user_document["verified_email"],
                    google_id=user_document["id"],
                    family_name=user_document["family_name"],
                    name=user_document["name"],
                    given_name=user_document["given_name"],
                    dob=dob,
                    email=user_document["email"],
                    gender=gender,
                    picture=picture,
                )

            add_google_friends.delay(request.user.id, info["access_token"])
            return HttpResponseRedirect(reverse("recruiter:index"))
        message_type = "Sorry,"
        message = "We didnt find your Account"
        reason = "Please verify your details and try again"
        email = settings.DEFAULT_FROM_EMAIL
        number = settings.CONTACT_NUMBER
        return render(
            request,
            "recruiter/recruiter_404.html",
            {
                "message_type": message_type,
                "message": message,
                "reason": reason,
                "email": email,
                "number": number,
            },
            status=404,
        )
    else:
        rty = (
            "https://accounts.google.com/o/oauth2/auth?client_id="
            + settings.GP_CLIENT_ID
            + "&response_type=code&scope="
        )
        rty += (
            "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email "
            + "https://www.googleapis.com/auth/contacts.readonly"
        )
        rty += (
            "&redirect_uri="
            + request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("recruiter:google_connect")
            + "&state=1235dfghjkf123"
        )
        return HttpResponseRedirect(rty)


@recruiter_login_required
def facebook_login(request):
    if "code" in request.GET:
        accesstoken = get_access_token_from_code(
            request.GET["code"],
            request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("recruiter:facebook_login"),
            settings.FB_APP_ID,
            settings.FB_SECRET,
        )
        if accesstoken.get("access_token"):
            graph = GraphAPI(accesstoken["access_token"])
            accesstoken = graph.extend_access_token(
                settings.FB_APP_ID, settings.FB_SECRET
            )["accesstoken"]
            profile = graph.get_object(
                "me",
                fields="id, name, email, birthday, hometown, location, link, locale, gender, timezone",
            )
            # print profile
            if profile.get("email"):
                email = profile.get("email")
                hometown = (
                    profile["hometown"]["name"] if "hometown" in profile.keys() else ""
                )
                location = (
                    profile["location"]["name"] if "location" in profile.keys() else ""
                )
                bday = (
                    datetime.strptime(profile["birthday"], "%m/%d/%Y").strftime(
                        "%Y-%m-%d"
                    )
                    if profile.get("birthday")
                    else "1970-09-09"
                )
                if not request.user.is_fb_connected:
                    Facebook.objects.create(
                        user=request.user,
                        facebook_url=profile.get("link", ""),
                        facebook_id=profile.get("id"),
                        first_name=profile.get("first_name", ""),
                        last_name=profile.get("last_name", ""),
                        verified=profile.get("verified", ""),
                        name=profile.get("name", ""),
                        language=profile.get("locale", ""),
                        hometown=hometown,
                        email=profile.get("email", ""),
                        gender=profile.get("gender", ""),
                        dob=bday,
                        location=location,
                        timezone=profile.get("timezone", ""),
                        accesstoken=accesstoken,
                    )
                add_facebook_friends_pages_groups(
                    accesstoken, profile["id"], request.user
                )
                return HttpResponseRedirect(reverse("recruiter:index"))
        message_type = "Sorry,"
        message = "We didnt find your email id through facebook"
        reason = "Please verify your email id in facebook and try again"
        email = settings.DEFAULT_FROM_EMAIL
        number = settings.CONTACT_NUMBER
        return render(
            request,
            "recruiter/recruiter_404.html",
            {
                "message_type": message_type,
                "message": message,
                "reason": reason,
                "email": email,
                "number": number,
            },
            status=404,
        )
    else:
        # publish_stream, friends_groups
        # the above are depricated as part of graphapi 2.3 we need to update
        # our code to fix it
        rty = (
            "https://graph.facebook.com/oauth/authorize?client_id="
            + settings.FB_APP_ID
            + "&redirect_uri="
            + request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("recruiter:facebook_login")
            + "&scope=manage_pages,read_stream, user_about_me, user_birthday, user_location, user_work_history, user_hometown"
            + ", user_website, email, user_likes, user_groups, publish_actions, publish_pages"
        )
        return HttpResponseRedirect(rty)


@recruiter_login_required
def linkedin_login(request):
    if "code" in request.GET:
        params = {}
        params["grant_type"] = "authorization_code"
        params["code"] = request.GET.get("code")
        params["redirect_uri"] = (
            request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("recruiter:linkedin_login")
        )
        params["client_id"] = settings.LN_API_KEY
        params["client_secret"] = settings.LN_SECRET_KEY
        import urllib.request as ur

        args = {
            "grant_type": "authorization_code",
            "code": request.GET.get("code"),
            "redirect_uri": request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("recruiter:linkedin_login"),
            "client_id": settings.LN_API_KEY,
            "client_secret": settings.LN_SECRET_KEY,
        }
        response = requests.get(
            "https://www.linkedin.com/uas/oauth2/accessToken?"
            + urllib.parse.urlencode(args)
        ).json()
        if response.get("access_token"):
            accesstoken = response["access_token"]
            required_info = "id,first-name,last-name,email-address,location,positions,educations,industry,summary,public-profile-url,picture-urls::(original)"
            rty = (
                "https://api.linkedin.com/v1/people/~:("
                + required_info
                + ")"
                + "?format=json&oauth2_access_token="
            )
            rty += accesstoken
            details = ur.urlopen(rty).read().decode("utf8")
            details = json.loads(details)
            if "positions" in details.keys():
                if details["positions"]["_total"] == 0:
                    positions = 0
                else:
                    positions = details["positions"]["values"]
            else:
                positions = 0
            # purl = ""
            # if 'pictureUrls' in details:
            #     pictureurl = details['pictureUrls']
            #     if pictureurl['_total'] != 0:
            #             for i in pictureurl['values']:
            #                 purl = i
            Linkedin.objects.create(
                user=request.user,
                accesstoken=accesstoken,
                linkedin_id=details["id"],
                linkedin_url=details["publicProfileUrl"],
                first_name=details["firstName"],
                last_name=details["lastName"],
                email=details["emailAddress"],
                location=details["location"]["name"],
                workhistory=positions,
            )

            # TODO need to store User groups and frnds in the database

            # lninfo(id_value,details,location,edu,positions,industry,accesstoken,pictureurl,"login")
            # lngroups(id_value,details['id'],accesstoken)
            # lnfrnds(id_value,details['id'],accesstoken)

            return HttpResponseRedirect(reverse("recruiter:index"))
        message_type = "Sorry,"
        message = "We didnt find your email id through facebook"
        reason = "Please verify your email id in facebook and try again"
        email = settings.DEFAULT_FROM_EMAIL
        number = settings.CONTACT_NUMBER
        return render(
            request,
            "recruiter/recruiter_404.html",
            {
                "message_type": message_type,
                "message": message,
                "reason": reason,
                "email": email,
                "number": number,
            },
            status=404,
        )
    else:
        rty = (
            "https://www.linkedin.com/uas/oauth2/authorization?response_type=code&client_id="
            + settings.LN_API_KEY
        )
        rty += "&scope=r_basicprofile r_emailaddress rw_company_admin w_share&state=8897239179ramya"
        rty += (
            "&redirect_uri="
            + request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("recruiter:linkedin_login")
        )
        return HttpResponseRedirect(rty)


# def add_linkedin_group_friends(uemail, id, accesstoken):
# TODO:
# check wether we are getting all groups or just few as per paging
# user = User.objects.get(id=id)
# url = 'https://api.linkedin.com/v1/people/~/group-memberships:(group:(id,name),membership-state)'
# params = {'count': 100}
# headers = {'x-li-format': 'json', 'Content-Type': 'application/json'}
# kw = dict(params=params, headers=headers, timeout=60)
# params.update({'oauth2_access_token': accesstoken})
# response = requests.request('GET', url, **kw).json()
# if response['_total'] != 0:
#     for i in response['values']:
#         LinkedinGroup.objects.create(
#             user=user,
#             membership=i['membershipState']['code'],
#             group_id=i['group']['id'],
#             group_name=i['group']['name']
#         )

# required_info = "id,first-name,last-name,email-address,location,positions,educations,industry"
# url = "https://api.linkedin.com/v1/people/~:(" + required_info + ")?format=json&oauth2_access_token=" + \
#       "?format=json&oauth2_access_token="
# url += accesstoken
# fdetails = json.loads(urllib.urlopen(url).read())
# friends = fdetails['values']

# for friend in friends:
#     industry = friend['industry'] if 'industry' in friend.keys() else None
#     if 'positions' in friend.keys():
#         positions = 0 if (friend['positions']['_total'] == 0) else friend['positions']['values']
#     else:
#         positions = 0
#     location = friend['location'] if 'location' in friend.keys() else ""
#     LinkedinFriend.objects.create(
#         user=user,
#         linkedin_id=friend['id'],
#         first_name=friend['firstName'],
#         last_name=friend['lastName'],
#         location=location,
#         workhistory=positions,
#         industry=industry
#     )


@recruiter_login_required
def new_template(request, jobpost_id):
    if request.method == "POST":
        validate_mailtemplate = MailTemplateForm(request.POST)
        if validate_mailtemplate.is_valid():
            MailTemplate.objects.create(
                title=request.POST.get("title"),
                subject=request.POST.get("subject"),
                message=request.POST.get("message"),
                created_on=datetime.utcnow(),
                modified_on=datetime.utcnow(),
                created_by=request.user,
                job_post_id=jobpost_id,
            )
            data = {
                "error": False,
                "message": "Successfully saved new template, now you can see it, edit it, send to your contacts.!",
            }
            return HttpResponse(json.dumps(data))
        data = {"error": True, "message": validate_mailtemplate.errors}
        return HttpResponse(json.dumps(data))
    return render(
        request, "recruiter/mail/new_mailtemplate.html", {"jobpost_id": jobpost_id}
    )


@recruiter_login_required
def edit_template(request, jobpost_id, template_id):
    mailtemplates = MailTemplate.objects.filter(id=template_id, created_by=request.user)
    if mailtemplates:
        mailtemplate = mailtemplates[0]
        if request.method == "POST":
            validate_mailtemplate = MailTemplateForm(
                request.POST, instance=mailtemplate
            )
            if validate_mailtemplate.is_valid():
                mailtemplate = validate_mailtemplate.save(commit=False)
                mailtemplate.modified_on = datetime.utcnow()
                mailtemplate.job_post_id = jobpost_id
                mailtemplate.save()
                data = {
                    "error": False,
                    "message": "Successfully saved template, now you can see it, edit it, send to recruiters!",
                }
                return HttpResponse(json.dumps(data))
            data = {"error": True, "message": validate_mailtemplate.errors}
            return HttpResponse(json.dumps(data))
        return render(
            request,
            "recruiter/mail/edit_mailtemplate.html",
            {"email_template": mailtemplate, "jobpost_id": jobpost_id},
        )
    message = "Sorry, the page you requested can not be found"
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/404.html",
        {"message_type": "404", "message": message, "reason": reason},
        status=404,
    )


def emailtemplates(request, jobpost_id):
    mailtemplates = MailTemplate.objects.filter(created_by=request.user)
    jobpost = JobPost.objects.get(id=jobpost_id)
    return render(
        request,
        "recruiter/mail/list.html",
        {"mailtemplates": mailtemplates, "jobpost_id": jobpost_id, "jobpost": jobpost},
    )


@recruiter_login_required
def view_template(request, template_id):
    mailtemplate = MailTemplate.objects.filter(
        id=template_id, created_by=request.user
    ).first()
    if mailtemplate:
        return render(
            request, "recruiter/mail/view.html", {"mailtemplate": mailtemplate}
        )
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/404.html",
        {
            "message_type": "404",
            "message": "Sorry, the page you requested can not be found",
            "reason": reason,
        },
        status=404,
    )


@recruiter_login_required
def delete_template(request, template_id):
    mailtemplate = MailTemplate.objects.filter(id=template_id, created_by=request.user)
    if mailtemplate.exists():
        mailtemplate.delete()
        data = {"error": False, "response": "Job Post deleted Successfully"}
        return HttpResponse(json.dumps(data))
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/404.html",
        {
            "message_type": "404",
            "message": "Sorry, the page you requested can not be found",
            "reason": reason,
        },
        status=404,
    )


@recruiter_login_required
def send_mail(request, template_id, jobpost_id):
    mailtemplates = MailTemplate.objects.filter(id=template_id)
    if mailtemplates:
        emailtemplate = mailtemplates[0]
        if request.method == "POST":
            validate_mailtemplate = MailTemplateForm(
                request.POST, instance=emailtemplate
            )
            if validate_mailtemplate.is_valid():
                validate_mailtemplate.save()
                t = loader.get_template("email/email_template.html")
                c = {"text": emailtemplate.message}
                rendered = t.render(c)
                mto = []
                for recruiter in request.POST.getlist("recruiters"):
                    recruiter = User.objects.get(id=recruiter)
                    mto.append(recruiter.email)
                sent_mail = SentMail.objects.create(
                    template=emailtemplate, job_post_id=jobpost_id
                )

                for recruiter in request.POST.getlist("recruiters"):
                    recruiter = User.objects.get(id=recruiter)
                    sent_mail.recruiter.add(recruiter)
                Memail(
                    mto,
                    settings.DEFAULT_FROM_EMAIL,
                    emailtemplate.subject,
                    rendered,
                    False,
                )
                sending_mail.delay(emailtemplate, request.POST.getlist("recruiters"))
                data = {"error": False, "response": "Email Sent Successfully"}
                return HttpResponse(json.dumps(data))
            data = {"error": True, "response": validate_mailtemplate.errors}
            return HttpResponse(json.dumps(data))
        applicants = AppliedJobs.objects.filter(job_post_id=jobpost_id)
        return render(
            request,
            "recruiter/mail/send_mail.html",
            {
                "applicants": applicants,
                "mailtemplate": emailtemplate,
                "jobpost_id": jobpost_id,
            },
        )
    else:
        reason = "The URL may be misspelled or the page you're looking for is no longer available."
        return render(
            request,
            "recruiter/404.html",
            {
                "message_type": "404",
                "message": "Sorry, the page you requested can not be found",
                "reason": reason,
            },
            status=404,
        )


@recruiter_login_required
def sent_mails(request, jobpost_id):
    sent_mails = SentMail.objects.filter(job_post=jobpost_id)
    return render(
        request,
        "recruiter/mail/sent_mail_list.html",
        {"sent_mails": sent_mails, "jobpost_id": jobpost_id},
    )


@recruiter_login_required
def enable_email_notifications(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    if job_post.send_email_notifications:
        job_post.send_email_notifications = False
    else:
        job_post.send_email_notifications = True
    job_post.save()
    return HttpResponseRedirect(
        reverse("recruiter:view", kwargs={"job_post_id": job_post_id})
    )


def view_sent_mail(request, sent_mail_id):
    sent_mail = SentMail.objects.filter(id=sent_mail_id).first()
    if sent_mail:
        return render(
            request, "recruiter/mail/view_sent_mail.html", {"sent_mail": sent_mail}
        )
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/404.html",
        {
            "message_type": "404",
            "message": "Sorry, the page you requested can not be found",
            "reason": reason,
        },
        status=404,
    )


@recruiter_login_required
def delete_sent_mail(request, sent_mail_id):
    sent_mails = SentMail.objects.filter(id=sent_mail_id)
    if sent_mails:
        sent_mail = sent_mails[0]
        sent_mail.delete()
        data = {"error": False, "response": "Sent Mail Deleted Successfully"}
        return HttpResponse(json.dumps(data))
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/404.html",
        {
            "message_type": "404",
            "message": "Sorry, the page you requested can not be found",
            "reason": reason,
        },
        status=404,
    )


def interview_location(request, location_count):
    location_count = int(location_count) + 1
    cities = City.objects.all()
    selected_locations = request.POST.get("selected_locations")
    return render(
        request,
        "recruiter/job/add_interview_location.html",
        {
            "selected_locations": selected_locations,
            "interview_location_count": location_count,
            "cities": cities,
        },
    )


@recruiter_login_required
def registration_success(request):
    # user = request.user
    # random_code = rand_string(size=6)
    # message = 'Hello ' + user.username + ', An OTP ' + random_code + ' for your Peeljobs recruiter account, Please Confirm and Proceed'
    # data = {"username": settings.SMS_AUTH_KEY, "password": settings.BULK_SMS_PASSWORD, "from": settings.BULK_SMS_FROM, "to": user.mobile, "message": message}
    # # requests.get("http://182.18.160.225/index.php/api/bulk-sms", params=data)
    # url = 'http://sms.9sm.in/rest/services/sendSMS/sendGroupSms?AUTH_KEY='+str(settings.SMS_AUTH_KEY) + '&message=' + str(message)
    # requests.get(url+'&senderId='+str(settings.BULK_SMS_FROM)+'&routeId=1&mobileNos=' + str(user.mobile) + '&smsContentType=english')

    # user.mobile_verification_code = random_code
    # user.mobile_verified = False
    # user.save()

    return render(request, "recruiter/registration_success.html", {})


def how_it_works(request):
    return render(request, "recruiter/how_it_works.html", {})


@recruiter_login_required
def view_company(request):
    menu = Menu.objects.filter(company=request.user.company).order_by("lvl")
    return render(
        request,
        "recruiter/company/view_microsite_page.html",
        {"company": request.user.company, "company_menu": menu},
    )


@recruiter_login_required
def edit_company(request):
    print(request.POST)
    company = request.user.company
    if request.method == "POST":
        if company:
            company_form = EditCompanyForm(
                request.POST, request.FILES, instance=company
            )
        else:
            company_form = EditCompanyForm(request.POST, request.FILES)
        if company_form.is_valid():
            company_obj = company_form.save(commit=False)
            if request.FILES.get("profile_pic"):
                if company_obj.profile_pic:
                    url = str(company.profile_pic).split("cdn.peeljobs.com")[-1:]
                    AWS().cloudfront_invalidate(paths=url)
                file_path = get_aws_file_path(
                    request.FILES.get("profile_pic"),
                    "company/logo/",
                    slugify(request.POST["name"]),
                )
                company_obj.profile_pic = file_path
            if request.user.is_agency_recruiter:
                company_obj.company_type = "Consultant"
            else:
                company_obj.company_type = "Company"
            company_obj.slug = slugify(request.POST.get("name"))
            company_obj.save()
            if not company:
                request.user.company = company_obj
            request.user.save()
            data = {"error": False, "response": "Company Edited Successfully"}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "response": company_form.errors}
            return HttpResponse(json.dumps(data))
    if request.method == "GET":
        if request.GET.get("q"):
            companies = Company.objects.filter(
                id__in=User.objects.filter(is_admin=False).values_list(
                    "company", flat=True
                ),
                name__icontains=request.GET.get("q"),
            ).distinct()
            companies_names = []
            for each in companies:
                companies_names.append(each.name)
            if request.GET.get("register_name"):
                companies = Company.objects.filter(
                    name=request.GET.get("register_name")
                )
                if companies:
                    company = companies[0]
                    each_obj = {}
                    each_obj["website"] = company.website
                    each_obj["company_type"] = company.company_type
                    each_obj["company_id"] = company.id
                    data = {"company": each_obj}
                    return HttpResponse(json.dumps(data))
            data = {"response": companies_names}
            return HttpResponse(json.dumps(data))
        else:
            if request.user.agency_admin or request.user.is_recruiter:
                template_name = "recruiter/company/edit_microsite_page.html"
                data = {"company_types": COMPANY_TYPES, "company": company}
                status = 200
            else:
                template_name = "recruiter/company/edit_microsite_page.html"
                data = {
                    "message": "Sorry, You don't have permissions to access this page"
                }
                status = 404
            return render(request, template_name, data, status=status)


@recruiter_login_required
def upload_profilepic(request):
    if request.user.company:
        if "profile_pic" in request.FILES:
            logo = request.FILES.get("profile_pic")
            sup_formates = ["image/jpeg", "image/png"]
            ftype = logo.content_type
            if str(ftype) in sup_formates:
                if request.user.company.profile_pic:
                    url = str(request.user.company.profile_pic).split(
                        "cdn.peeljobs.com"
                    )[-1:]
                    AWS().cloudfront_invalidate(paths=url)
                file_path = get_aws_file_path(
                    logo, "company/logo/", request.user.company.slug
                )
                request.user.company.profile_pic = file_path
                request.user.company.save()
                data = {
                    "error": False,
                    "data": "Company Profile Pic Uploaded Successfully",
                }
                return HttpResponse(json.dumps(data))
            else:
                data = {
                    "error": True,
                    "data": "Upload Valid Image Format Files Ex: Png, Jpg, JPEG",
                }
                return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "data": "upload file first"}
            return HttpResponse(json.dumps(data))

    else:
        data = {"error": True, "data": "Please Update your company details"}
        return HttpResponse(json.dumps(data))


@recruiter_login_required
def company_recruiter_list(request):
    recruiters = User.objects.filter(company=request.user.company).exclude(
        id=request.user.id
    )
    if "search" in request.GET.keys():
        if str(request.GET["search"].lower()) == "active":
            recruiters = recruiters.filter(is_active=True)
        else:
            recruiters = recruiters.filter(is_active=False)
        if not (
            request.GET["search"].lower() == "active"
            or str(request.GET["search"].lower()).replace(" ", "") == "inactive"
        ):
            recruiters = recruiters.filter(
                Q(first_name__icontains=request.GET["search"])
                | Q(email__icontains=request.GET["search"])
            )
    if "page" in request.GET and int(request.GET.get("page")) > 0:
        page = int(request.GET.get("page"))
    else:
        page = 1
    items_per_page = 10
    no_pages = int(math.ceil(float(recruiters.count()) / items_per_page))
    recruiters = recruiters[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    search_value = request.GET["search"] if "search" in request.GET.keys() else ""
    return render(
        request,
        "recruiter/company/recruiter_list.html",
        {
            "recruiters": recruiters,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "search_value": search_value,
        },
    )


@agency_admin_login_required
def company_recruiter_create(request):
    contenttype = ContentType.objects.get(model="user")
    permissions = Permission.objects.filter(
        content_type_id=contenttype, codename__icontains="jobposts"
    ).order_by("id")

    if request.method == "POST":
        validate_recruiter = RecruiterForm(request.POST, request.FILES)
        if validate_recruiter.is_valid():
            user = User.objects.create(
                first_name=request.POST["first_name"],
                email=request.POST["email"],
                username=request.POST["email"],
                job_role=request.POST["job_role"],
                mobile=request.POST["mobile"],
            )
            if request.FILES.get("profile_pic"):
                user.profile_pic = request.FILES.get("profile_pic")
            user.set_password(request.POST["password"])
            user.company = request.user.company
            user.user_type = "AR"
            user.mobile_verified = True
            while True:
                random_code = get_random_string(length=10)
                u = User.objects.filter(activation_code__iexact=random_code)
                if not u:
                    break
            while True:
                unsub_code = get_random_string(length=10)
                u = User.objects.filter(unsubscribe_code__iexact=random_code)
                if not u:
                    break
            user.activation_code = random_code
            user.unsubscribe_code = unsub_code
            user.save()
            if (
                "is_admin" in request.POST.keys()
                and request.POST.get("is_admin") == "True"
            ):
                user.user_type = "AA"
                user.agency_admin = True
                user.save()
                for permission in permissions:
                    user.user_permissions.add(permission)
            else:
                for perm in request.POST.getlist("permissions"):
                    permission = Permission.objects.get(id=perm)
                    user.user_permissions.add(permission)

            temp = loader.get_template("recruiter/email/recruiter_account.html")
            try:
                url = (
                    "https://"
                    + request.META["HTTP_HOST"]
                    + "/recruiter/activation/"
                    + str(user.activation_code)
                    + "/"
                )
            except:
                url = (
                    "https://peeljobs.com"
                    + "/recruiter/activation/"
                    + str(user.activation_code)
                    + "/"
                )
            c = {
                "user": user,
                "activate_url": url,
                "user_password": request.POST["password"],
            }
            rendered = temp.render(c)
            # user_active = True if request.user.is_active else False
            Memail(
                [user.email],
                settings.DEFAULT_FROM_EMAIL,
                "PeelJobs Recruiter Account Activation",
                rendered,
                False,
            )
            data = {"error": False, "response": "Recruiter Created Successfully"}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "response": validate_recruiter.errors}
            return HttpResponse(json.dumps(data))
    return render(
        request, "recruiter/company/create_recruiter.html", {"permissions": permissions}
    )


@agency_admin_login_required
def edit_company_recruiter(request, recruiter_id):
    recruiters = User.objects.filter(
        company=request.user.company, id=recruiter_id
    ).exclude(id=request.user.id)
    if recruiters:
        recruiter = recruiters[0]
        contenttype = ContentType.objects.get(model="user")
        permissions = Permission.objects.filter(
            content_type_id=contenttype, codename__icontains="jobposts"
        ).order_by("id")

        if request.method == "POST":
            validate_recruiter = RecruiterForm(
                request.POST, request.FILES, instance=recruiter
            )
            if validate_recruiter.is_valid():
                recruiter = validate_recruiter.save(commit=False)
                if recruiter.password != request.POST[
                    "password"
                ] and not check_password(request.POST["password"], recruiter.password):
                    recruiter.set_password(request.POST["password"])
                if request.FILES.get("profile_pic"):
                    recruiter.profile_pic = request.FILES.get("profile_pic")
                recruiter.save()
                recruiter.user_permissions.clear()
                if (
                    "is_admin" in request.POST.keys()
                    and request.POST.get("is_admin") == "True"
                ):
                    recruiter.user_type = "AA"
                    recruiter.agency_admin = True
                    recruiter.save()
                    for permission in permissions:
                        recruiter.user_permissions.add(permission)
                else:
                    recruiter.user_type = "AR"
                    recruiter.agency_admin = False
                    recruiter.save()

                    for perm in request.POST.getlist("permissions"):
                        permission = Permission.objects.get(id=perm)
                        recruiter.user_permissions.add(permission)

                data = {"error": False, "response": "Recruiter Updated Successfully"}
                return HttpResponse(json.dumps(data))
            else:
                data = {"error": True, "response": validate_recruiter.errors}
                return HttpResponse(json.dumps(data))
        return render(
            request,
            "recruiter/company/create_recruiter.html",
            {"recruiter": recruiter, "permissions": permissions},
        )
    message = "Sorry, No Recruiter Available with this id"
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/recruiter_404.html",
        {"message_type": "404", "message": message, "reason": reason},
        status=404,
    )


@agency_admin_login_required
def activate_company_recruiter(request, recruiter_id):
    recruiters = User.objects.filter(company=request.user.company, id=recruiter_id)
    if recruiters:
        recruiter = recruiters[0]
        if recruiter.is_active:
            recruiter.is_active = False
        else:
            recruiter.is_active = True
        recruiter.save()
        return HttpResponseRedirect(reverse("recruiter:company_recruiter_list"))
    message = "Sorry, No Recruiter Available with this id"
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/recruiter_404.html",
        {"message_type": "404", "message": message, "reason": reason},
        status=404,
    )


@agency_admin_login_required
def delete_company_recruiter(request, recruiter_id):
    recruiters = User.objects.filter(company=request.user.company, id=recruiter_id)
    if recruiters:
        recruiter = recruiters[0]
        recruiter.delete()
        data = {"error": False, "response": "Recruiter Deleted Successfully"}
    else:
        data = {"error": True, "response": "Some Problem Occurs"}
    return HttpResponse(json.dumps(data))


@recruiter_login_required
def company_recruiter_profile(request, recruiter_id):
    recruiters = User.objects.filter(company=request.user.company, id=recruiter_id)
    if recruiters:
        recruiter = recruiters[0]
        if recruiter.is_admin:
            job_posts = JobPost.objects.filter(company=request.user.company)
        else:
            job_posts = JobPost.objects.filter(
                Q(user=recruiter) | Q(agency_recruiters__in=[recruiter])
            )
        if "job_status" in request.GET.keys():
            job_posts = job_posts.filter(status=request.GET["job_status"])

        tickets = Ticket.objects.filter(user=recruiter)
        if "search_value" in request.GET.keys():
            if request.GET["search_value"] == "all":
                pass
            else:
                job_posts = job_posts.filter(job_type=request.GET["search_value"])
        if "page" in request.GET and int(request.GET.get("page")) > 0:
            page = int(request.GET.get("page"))
        else:
            page = 1
        items_per_page = 10
        no_pages = int(math.ceil(float(job_posts.count()) / items_per_page))
        job_posts = job_posts[(page - 1) * items_per_page : page * items_per_page]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        search_value = (
            request.GET.get("search_value") if request.GET.get("search_value") else ""
        )
        job_status = (
            request.GET.get("job_status") if request.GET.get("job_status") else "active"
        )

        return render(
            request,
            "recruiter/company/recruiter_profile.html",
            {
                "recruiter": recruiter,
                "job_posts": job_posts,
                "tickets": tickets,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
                "search_value": search_value,
                "job_status": job_status,
            },
        )

    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/recruiter_404.html",
        {
            "message_type": "404",
            "message": "Sorry, No Recruiter Available with this id",
            "reason": reason,
        },
        status=404,
    )


@agency_admin_login_required
def add_menu(request):
    if request.method == "POST":
        validate_menu = MenuForm(request.POST)
        if validate_menu.is_valid():
            new_menu = validate_menu.save(commit=False)
            if request.POST.get("status") == "True":
                new_menu.status = True
            menu_count = Menu.objects.count()
            new_menu.lvl = menu_count + 1
            new_menu.company = request.user.company
            new_menu.save()
            data = {"error": False, "response": "Menu created successfully"}
        else:
            data = {"error": True, "response": validate_menu.errors}
        return HttpResponse(json.dumps(data))


@agency_admin_login_required
def menu_status(request, menu_id):
    menu = Menu.objects.filter(id=menu_id, company=request.user.company)
    if menu:
        menu = menu[0]
        if menu.status:
            menu.status = False
        else:
            menu.status = True
        menu.save()
    return HttpResponseRedirect(reverse("recruiter:view_company"))


@agency_admin_login_required
def delete_menu(request, menu_id):
    menu = Menu.objects.filter(id=menu_id, company=request.user.company)
    if menu:
        menu = menu[0]
        menu.delete()
        data = {"error": False, "response": "Menu Deleted Successfully"}
    else:
        data = {"error": True, "response": "Some Problem Occurs"}
    return HttpResponse(json.dumps(data))


@agency_admin_login_required
def edit_menu(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id, company=request.user.company)
    if request.method == "POST":
        validate_menu = MenuForm(request.POST, instance=menu)
        if validate_menu.is_valid():
            new_menu = validate_menu.save(commit=False)
            if request.POST.get("status") == "True":
                new_menu.status = True
            new_menu.save()
            data = {"error": False, "response": "Menu created successfully"}
        else:
            data = {"error": True, "response": validate_menu.errors}
        return HttpResponse(json.dumps(data))


@agency_admin_login_required
def menu_order(request):
    menu = get_object_or_404(
        Menu, id=request.GET.get("menu_id"), company=request.user.company
    )
    prev = request.GET.get("prev")
    current = request.GET.get("current")
    if int(prev) < int(current):
        selected_menus = Menu.objects.filter(
            lvl__gt=prev, lvl__lte=current, company=request.user.company
        )
        for each in selected_menus:
            each.lvl = each.lvl - 1
            each.save()
    else:
        selected_menus = Menu.objects.filter(
            lvl__lt=prev, lvl__gte=current, company=request.user.company
        )
        for each in selected_menus:
            each.lvl = each.lvl + 1
            each.save()
    menu.lvl = current
    menu.save()
    return HttpResponseRedirect(reverse("recruiter:view_company"))


@recruiter_login_required
def dashboard(request):
    # active_jobs = JobPost.objects.filter(user=request.user, status='Live')
    # return render(request, 'recruiter/dashboard.html', {'active_jobs':
    # active_jobs})
    return HttpResponseRedirect(reverse("recruiter:list"))


@recruiter_login_required
def messages(request):
    if request.GET.get("search"):
        user_ids = AppliedJobs.objects.filter(
            job_post__user__id=request.user.id
        ).values_list("user", flat=True)
        users = User.objects.filter(
            Q(id__in=user_ids)
            & Q(
                Q(email__icontains=request.GET.get("search"))
                | Q(first_name__icontains=request.GET.get("search"))
                | Q(last_name__icontains=request.GET.get("search"))
            )
        )
        return HttpResponse(
            json.dumps(
                {"error": False, "users": list(users.values_list("id", flat=True))}
            )
        )
    if request.POST.get("mode") == "get_messages":
        db.messages.update(
            {
                "$and": [
                    {"message_to": request.user.id},
                    {"message_from": int(request.POST.get("r_id"))},
                    {"job_id": None},
                ]
            },
            {"$set": {"is_read": True}},
            multi=True,
        )
        messages = db.messages.find(
            {
                "$or": [
                    {
                        "$and": [
                            {"message_from": request.user.id},
                            {"message_to": int(request.POST.get("r_id"))},
                            {"job_id": None},
                        ]
                    },
                    {
                        "$and": [
                            {"message_to": request.user.id},
                            {"message_from": int(request.POST.get("r_id"))},
                            {"job_id": None},
                        ]
                    },
                ]
            }
        )
        user = User.objects.filter(id=request.POST.get("r_id")).first()
        if user:
            try:
                user_pic = user.profile_pic.url
            except:
                user_pic = user.photo
            try:
                profile_pic = request.user.profile_pic.url
            except:
                profile_pic = request.user.photo
            if not user_pic:
                user_pic = "https://cdn.peeljobs.com/dummy.jpg"
            if not profile_pic:
                profile_pic = "https://cdn.peeljobs.com/dummy.jpg"
            messages = render_to_string(
                "candidate/messages.html",
                {
                    "messages": list(messages),
                    "user": user,
                    "user_pic": user_pic,
                    "profile_pic": profile_pic,
                },
                request,
            )
            return HttpResponse(json.dumps({"error": False, "messages": messages}))
        else:
            return HttpResponse(
                json.dumps({"error": True, "response": "User Not Found!"})
            )
    if request.POST.get("post_message"):
        data = {
            "message": request.POST.get("message"),
            "message_from": request.user.id,
            "message_to": int(request.POST.get("message_to")),
            "created_on": datetime.now(),
            "is_read": False,
        }
        if request.POST.get("job_id"):
            data["job_id"] = int(request.POST.get("job_id"))
        msg_id = db.messages.insert(data)
        time = datetime.now().strftime("%b. %d, %Y, %l:%M %p")
        return HttpResponse(
            json.dumps(
                {
                    "error": False,
                    "message": request.POST.get("message"),
                    "msg_id": str(msg_id),
                    "time": time,
                }
            )
        )
    if request.POST.get("mode") == "delete_message":
        msg = db.messages.find_one({"_id": ObjectId(request.POST.get("id"))})
        if (
            msg.get("message_from") == request.user.id
            or msg.get("message_to") == request.user.id
        ):
            db.messages.remove({"_id": ObjectId(request.POST.get("id"))})
            data = {"error": False, "message": request.POST.get("message")}
        else:
            data = {"error": True, "message": "You Cannot delete!"}
        return HttpResponse(json.dumps(data))
    if request.POST.get("mode") == "delete_chat":
        if request.POST.get("job"):
            messages = db.messages.remove(
                {
                    "$or": [
                        {
                            "$and": [
                                {"message_from": request.user.id},
                                {"message_to": int(request.POST.get("user"))},
                                {"job_id": int(request.POST.get("job"))},
                            ]
                        },
                        {
                            "$and": [
                                {"message_to": request.user.id},
                                {"message_from": int(request.POST.get("user"))},
                                {"job_id": int(request.POST.get("job"))},
                            ]
                        },
                    ]
                }
            )
        else:
            messages = db.messages.remove(
                {
                    "$or": [
                        {
                            "$and": [
                                {"message_from": request.user.id},
                                {"message_to": int(request.POST.get("user"))},
                                {"job_id": None},
                            ]
                        },
                        {
                            "$and": [
                                {"message_to": request.user.id},
                                {"message_from": int(request.POST.get("user"))},
                                {"job_id": None},
                            ]
                        },
                    ]
                }
            )
        return HttpResponse(
            json.dumps({"error": False, "message": request.POST.get("message")})
        )
    if request.user.is_authenticated:
        messages = list(
            db.messages.find(
                {
                    "$or": [
                        {"message_from": request.user.id},
                        {"message_to": request.user.id},
                    ]
                },
                {"message_from": 1, "message_to": 1, "_id": 0},
            ).sort([("created_on", -1)])
        )
        user_ids = AppliedJobs.objects.filter(
            job_post__user__id=request.user.id
        ).values_list("user", flat=True)
        users = User.objects.filter(id__in=user_ids)
        if messages:
            recruiter_ids = map(
                lambda d: d.get("message_from")
                if d.get("message_to") == request.user.id
                else d.get("message_to"),
                messages,
            )
            preserved = Case(
                *[When(pk=pk, then=pos) for pos, pk in enumerate(recruiter_ids)]
            )
            users = users.order_by(preserved)
        return render(request, "recruiter/user/messages.html", {"users": users})
    else:
        return HttpResponseRedirect("/")


@recruiter_login_required
def resume_upload(request):
    if request.user.is_agency_admin:
        agency_jobposts = JobPost.objects.filter(user__company=request.user.company)
    else:
        agency_jobposts = JobPost.objects.filter(
            Q(agency_recruiters__in=[request.user]) | Q(user=request.user)
        ).distinct()
    if request.method == "POST":
        resume_user = AgencyResume.objects.filter(
            email=request.POST.get("email"), uploaded_by=request.user
        ).first()
        if not resume_user:
            validate_resume_upload = ResumeUploadForm(
                request.POST, request.FILES, request=request
            )
            if validate_resume_upload.is_valid():
                fo = request.FILES["resume"]
                sup_formates = [
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "application/pdf",
                    "application/rtf",
                    "application/x-rtf",
                    "text/richtext",
                    "application/msword",
                ]
                ftype = fo.content_type
                size = fo.size / 1024
                if str(ftype) in sup_formates:
                    if size < 300 and size > 0:
                        conn = tinys3.Connection(
                            settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY
                        )
                        random_string = "".join(
                            random.choice("0123456789ABCDEF") for i in range(3)
                        )
                        user_id = str(request.user.id) + str(random_string)
                        path = (
                            "resume/"
                            + user_id
                            + "/"
                            + request.FILES["resume"]
                            .name.replace(" ", "-")
                            .encode("ascii", "ignore")
                            .decode("ascii")
                        )
                        conn.upload(
                            path,
                            request.FILES["resume"],
                            settings.AWS_STORAGE_BUCKET_NAME,
                            public=True,
                        )
                        email = request.POST.get("email")
                        user = User.objects.filter(email__iexact=email).first()
                        if not user:
                            user = User.objects.create(
                                email=email,
                                user_type="JS",
                                username=email,
                                mobile=request.POST.get("mobile", ""),
                                resume=path,
                                registered_from="ResumePool",
                            )
                            passwd = get_random_string(length=10).lower()
                            user.set_password(passwd)
                            user.save()
                            save_codes_and_send_mail(user, request, passwd)
                        resume_upload = AgencyResume.objects.create(
                            candidate_name=request.POST.get("candidate_name"),
                            email=email,
                            user=user,
                            resume=path,
                            uploaded_by=request.user,
                            mobile=request.POST.get("mobile"),
                        )
                        if request.POST.get("experience"):
                            resume_upload.experience = request.POST.get("experience")
                        resume_upload.save()
                        resume_upload.skill.add(*request.POST.getlist("skill"))
                        for job in request.POST.getlist("job_post"):
                            AppliedJobs.objects.create(
                                status="Pending",
                                resume_applicant=resume_upload,
                                job_post_id=job,
                                ip_address=request.META["REMOTE_ADDR"],
                                user_agent=request.META["HTTP_USER_AGENT"],
                            )
                        data = {"error": False, "data": "Resume Uploaded Successfully"}
                        return HttpResponse(json.dumps(data))
                    else:
                        data = {
                            "error": True,
                            "data": "File Size must be less than 300 kb",
                        }
                        return HttpResponse(json.dumps(data))
                else:
                    data = {
                        "error": True,
                        "data": "Upload Valid Files Ex: docx, pdf, doc, rtf",
                    }
                    return HttpResponse(json.dumps(data))
            else:
                data = {"error": True, "response": validate_resume_upload.errors}
                return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "data": "Reusme Already Existed"}
            return HttpResponse(json.dumps(data))
    skills = Skill.objects.filter(status="Active")
    return render(
        request,
        "recruiter/company/resume_upload.html",
        {"skills": skills, "agency_jobposts": agency_jobposts, "status": POST},
    )


@recruiter_login_required
def multiple_resume_upload(request):
    if request.method == "POST":
        resume = request.FILES.get("file")
        sup_formates = [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/pdf",
            "application/rtf",
            "application/x-rtf",
            "text/richtext",
            "application/msword",
        ]
        size = resume.size / 1024
        if str(resume.content_type) in sup_formates:
            if size < 300 and size > 0:
                handle_uploaded_file(resume, resume.name)
                email, mobile, text = get_resume_data(resume)
                if not email:
                    data = {"error": True, "data": "Resume Must contain Email address"}
                    return HttpResponse(json.dumps(data))
                resume_user = AgencyResume.objects.filter(
                    email=email, uploaded_by=request.user
                ).first()
                if resume_user:
                    replace = request.POST.get(resume.name)
                    if replace and replace == "true":
                        conn = tinys3.Connection(
                            settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY
                        )
                        random_string = "".join(
                            random.choice("0123456789ABCDEF") for i in range(3)
                        )
                        user_id = str(request.user.id) + str(random_string)
                        path = (
                            "resume/"
                            + user_id
                            + "/"
                            + resume.name.replace(" ", "-")
                            .encode("ascii", "ignore")
                            .decode("ascii")
                        )
                        conn.upload(
                            path, resume, settings.AWS_STORAGE_BUCKET_NAME, public=True
                        )
                        resume_user.resume = path
                        resume_user.save()
                        data = {
                            "duplicated": True,
                            "data": "Resume Updated Successfully",
                        }
                    elif replace:
                        data = {"duplicated": True, "data": "Resume Already Existed"}
                    else:
                        data = {
                            "error": True,
                            "duplicate": True,
                            "email": email,
                            "fname": resume.name,
                        }
                    return HttpResponse(json.dumps(data))

                user = User.objects.filter(email__iexact=email).first()
                if not user:
                    user = User.objects.create(
                        email=email,
                        user_type="JS",
                        username=email,
                        registered_from="ResumePool",
                    )
                    passwd = get_random_string(length=10).lower()
                    user.set_password(passwd)
                    user.save()
                    save_codes_and_send_mail(user, request, passwd)
                conn = tinys3.Connection(
                    settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY
                )
                random_string = "".join(
                    random.choice("0123456789ABCDEF") for i in range(3)
                )
                user_id = str(request.user.id) + str(random_string)
                path = (
                    "resume/"
                    + user_id
                    + "/"
                    + resume.name.replace(" ", "-")
                    .encode("ascii", "ignore")
                    .decode("ascii")
                )
                conn.upload(path, resume, settings.AWS_STORAGE_BUCKET_NAME, public=True)
                resume_upload = AgencyResume.objects.create(
                    candidate_name=email,
                    email=email,
                    resume=path,
                    uploaded_by=request.user,
                    mobile=mobile,
                )
                for job in request.POST.getlist("job_post"):
                    AppliedJobs.objects.create(
                        status="Pending",
                        resume_applicant=resume_upload,
                        job_post_id=job,
                        ip_address=request.META["REMOTE_ADDR"],
                        user_agent=request.META["HTTP_USER_AGENT"],
                    )
                data = {"error": False, "data": "Resume Uploaded Successfully"}
            else:
                data = {"error": True, "data": "File Size must be less than 300 kb"}
        else:
            data = {"error": True, "data": "Upload Valid Files Ex: docx, pdf, doc, rtf"}
        return HttpResponse(json.dumps(data))
    message = (
        "Sorry, Page not available, Url may be mispelled or Page not available anymore"
    )
    return render(request, "recruiter/recruiter_404.html", {"message": message})


@recruiter_login_required
def resume_pool(request):
    if request.POST.getlist("applicants"):
        validate_resume_applicant = ApplicantResumeForm(request.POST)
        if validate_resume_applicant.is_valid():
            for resume in request.POST.getlist("applicants"):
                applied_job = AppliedJobs.objects.filter(
                    resume_applicant__id=resume,
                    job_post__id=request.POST.get("job_post"),
                ).first()
                if not applied_job:
                    AppliedJobs.objects.create(
                        status=request.POST.get("status"),
                        resume_applicant_id=resume,
                        job_post_id=request.POST.get("job_post"),
                        ip_address=request.META["REMOTE_ADDR"],
                        user_agent=request.META["HTTP_USER_AGENT"],
                    )
                else:
                    applied_job.status = request.POST.get("status")
                    applied_job.save()
            data = {"error": False, "response": "JobPosts Added Successfully"}
        else:
            data = {"error": True, "response": validate_resume_applicant.errors}
        return HttpResponse(json.dumps(data))

    if request.user.agency_admin or request.user.has_perm("jobposts_resume_profiles"):
        agency_resumes = AgencyResume.objects.filter(
            uploaded_by__company=request.user.company
        )
    else:
        agency_resumes = AgencyResume.objects.filter(uploaded_by=request.user)
    if request.POST.get("recruiters"):
        agency_resumes = agency_resumes.filter(
            uploaded_by_id=request.POST.get("recruiters")
        )
    if request.POST.get("experience"):
        agency_resumes = agency_resumes.filter(
            experience=request.POST.get("experience")
        )
    if request.POST.getlist("skills"):
        agency_resumes = agency_resumes.filter(
            skill__id__in=request.POST.getlist("skills")
        )

    no_of_jobs = len(agency_resumes)
    items_per_page = 15
    no_pages = int(math.ceil(float(len(agency_resumes)) / items_per_page))

    try:
        if int(request.GET.get("page")) > (no_pages + 2):
            return HttpResponseRedirect(reverse("jobs:index"))
        else:
            page = int(request.GET.get("page"))
    except:
        page = 1
    agency_resumes = agency_resumes[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    skills = Skill.objects.filter(status="Active")
    recruiters = User.objects.filter(company=request.user.company)
    if request.user.agency_admin or request.user.has_perm("jobposts_edit"):
        agency_jobposts = JobPost.objects.filter(user__company=request.user.company)
    else:
        agency_jobposts = JobPost.objects.filter(
            Q(agency_recruiters__in=[request.user]) | Q(user=request.user)
        ).distinct()
    return render(
        request,
        "recruiter/company/resume_pool.html",
        {
            "agency_resumes": agency_resumes,
            "recruiters": recruiters,
            "years": YEARS,
            "skills": skills,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "no_of_jobs": no_of_jobs,
            "selected_skills": request.POST.getlist("skills"),
            "agency_jobposts": agency_jobposts,
            "status": POST,
        },
    )


@recruiter_login_required
def resume_view(request, resume_id):
    if request.user.agency_admin or request.user.has_perm("jobposts_resume_profiles"):
        agency_resume = get_object_or_404(
            AgencyResume, uploaded_by__company=request.user.company, id=resume_id
        )
    else:
        agency_resume = get_object_or_404(
            AgencyResume, uploaded_by=request.user, id=resume_id
        )
    if not agency_resume:
        message = "Sorry, You have no permissions to access this page"
        return render(request, "recruiter/recruiter_404.html", {"message": message})

    applicants = AppliedJobs.objects.filter(resume_applicant=agency_resume)
    if request.user.is_agency_admin:
        agency_jobposts = JobPost.objects.filter(user__company=request.user.company)
    else:
        agency_jobposts = JobPost.objects.filter(
            Q(agency_recruiters__in=[request.user]) | Q(user=request.user)
        ).distinct()
    agency_jobposts = agency_jobposts.filter(
        skills__in=agency_resume.skill.all().values_list("id", flat=True)
    ).exclude(id__in=applicants.values_list("job_post", flat=True))
    if request.POST.get("mode") == "add_job":
        validate_resume_applicant = ApplicantResumeForm(request.POST)
        if validate_resume_applicant.is_valid():
            if not AppliedJobs.objects.filter(
                resume_applicant=agency_resume, job_post_id=request.POST.get("job_post")
            ):
                AppliedJobs.objects.create(
                    status=request.POST.get("status"),
                    resume_applicant=agency_resume,
                    job_post_id=request.POST.get("job_post"),
                    ip_address=request.META["REMOTE_ADDR"],
                    user_agent=request.META["HTTP_USER_AGENT"],
                )
            data = {"error": False, "response": "JobPost Added Successfully"}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "response": validate_resume_applicant.errors}
            return HttpResponse(json.dumps(data))
    profile = render_to_string(
        "recruiter/company/resume_view.html",
        {
            "agency_resume": agency_resume,
            "agency_jobposts": agency_jobposts,
            "status": POST,
            "applicants": applicants,
        },
        request,
    )
    return HttpResponse(json.dumps({"profile": profile}))


@recruiter_login_required
def resume_edit(request, resume_id):
    if request.user.is_agency_admin:
        agency_jobposts = JobPost.objects.filter(user__company=request.user.company)
    else:
        agency_jobposts = JobPost.objects.filter(
            Q(agency_recruiters__in=[request.user]) | Q(user=request.user)
        ).distinct()
    agency_resume = AgencyResume.objects.filter(id=resume_id).first()
    if request.method == "POST" and agency_resume:
        validate_resume_upload = ResumeUploadForm(
            request.POST, request.FILES, instance=agency_resume, request=request
        )
        if validate_resume_upload.is_valid():
            if "resume" in request.FILES:
                fo = request.FILES["resume"]
                sup_formates = [
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "application/pdf",
                    "application/rtf",
                    "application/x-rtf",
                    "text/richtext",
                    "application/msword",
                ]
                ftype = fo.content_type
                size = fo.size / 1024
                if str(ftype) in sup_formates:
                    if size < 300 and size > 0:
                        conn = tinys3.Connection(
                            settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY
                        )
                        random_string = "".join(
                            random.choice("0123456789ABCDEF") for i in range(3)
                        )
                        user_id = str(request.user.id) + str(random_string)
                        path = (
                            "resume/"
                            + user_id
                            + "/"
                            + request.FILES["resume"]
                            .name.replace(" ", "-")
                            .encode("ascii", "ignore")
                            .decode("ascii")
                        )
                        conn.upload(
                            path,
                            request.FILES["resume"],
                            settings.AWS_STORAGE_BUCKET_NAME,
                            public=True,
                        )
                        agency_resume.resume = path
                    else:
                        data = {
                            "error": True,
                            "data": "File Size must be less than 300 kb",
                        }
                        return HttpResponse(json.dumps(data))
                else:
                    data = {"error": True, "data": "enter docx or pdf file only"}
                    return HttpResponse(json.dumps(data))
            agency_resume.candidate_name = request.POST.get("candidate_name")
            if request.POST.get("email"):
                agency_resume.email = request.POST.get("email")
            if request.POST.get("experience"):
                agency_resume.experience = request.POST.get("experience")
            if request.POST.get("mobile"):
                agency_resume.mobile = request.POST.get("mobile")
            agency_resume.save()
            agency_resume.skill.clear()
            agency_resume.skill.add(*request.POST.getlist("skill"))
            if request.POST.getlist("job_post"):
                AppliedJobs.objects.filter(resume_applicant=agency_resume).delete()
                for job in request.POST.getlist("job_post"):
                    AppliedJobs.objects.create(
                        status=request.POST.get("status", "pending"),
                        resume_applicant=agency_resume,
                        job_post_id=job,
                        ip_address=request.META["REMOTE_ADDR"],
                        user_agent=request.META["HTTP_USER_AGENT"],
                    )
            data = {"error": False, "data": "Resume Updated Successfully"}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "response": validate_resume_upload.errors}
            return HttpResponse(json.dumps(data))
    skills = Skill.objects.filter(status="Active")
    if request.user.agency_admin or request.user.has_perm("jobposts_resume_profiles"):
        agency_resume = AgencyResume.objects.filter(id=resume_id).first()
    else:
        agency_resume = AgencyResume.objects.filter(
            id=resume_id, uploaded_by=request.user
        ).first()
    if agency_resume:
        template_name = "recruiter/company/resume_upload.html"
        data = {
            "skills": skills,
            "resume": agency_resume,
            "agency_jobposts": agency_jobposts,
            "status": POST,
        }
    else:
        template_name = "recruiter/recruiter_404.html"
        data = {"message": "Sorry, You don't have no permissions to access this page"}
    return render(request, template_name, data, status=200 if agency_resume else 404)


def download_applicants(request, jobpost_id, status):
    search_locations = ""
    search_skills = ""
    if request.GET.get("search_skills"):
        search_skills = request.GET.get("search_skills").split(",")
    if request.GET.get("search_locations"):
        search_locations = request.GET.get("search_locations").split(",")
    all_applicants = (
        AppliedJobs.objects.filter(job_post=jobpost_id)
        .prefetch_related("user", "resume_applicant")
        .distinct()
    )
    pending_applicants = all_applicants.filter(status=status.capitalize())
    if search_skills or search_locations:
        pending_applicants = pending_applicants.filter(
            Q(user__current_city__id__in=search_locations)
            | Q(user__skills__skill__id__in=search_skills)
        )
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        "attachment; filename=" + status + "_applicants.csv"
    )
    headers = OrderedDict()
    headers["first_name"] = "Firstname"
    headers["last_name"] = "Lastname"
    headers["email"] = "Email"
    headers["mobile"] = "Phone Number"
    headers["location"] = "Current Location"
    headers["permanent_address"] = "Permanent Address"
    headers["resume"] = "Resume"
    headers["status"] = "Status"
    writer = csv.DictWriter(response, fieldnames=headers)
    writer.writerow(headers)
    s3 = S3Connection(
        settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, is_secure=False
    )
    for user in pending_applicants:
        if user.user.resume:
            stored_url = s3.generate_url(
                600,
                "GET",
                bucket=settings.AWS_STORAGE_BUCKET_NAME,
                key=user.user.resume,
                force_http=True,
            )
        else:
            stored_url = ""
        writer.writerow(
            {
                "email": user.user.email,
                "first_name": user.user.first_name,
                "last_name": user.user.last_name,
                "location": user.user.current_city,
                "mobile": user.user.mobile,
                "resume": stored_url,
                "status": status,
                "permanent_address": user.user.permanent_address,
            }
        )
    return response
