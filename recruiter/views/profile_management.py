"""
Profile Management Views
Handles user and company profile operations
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


# Profile Management Views will be moved here
# TODO: Move the following functions from the main views.py:
# - user_profile()
# - edit_profile()
# - upload_profilepic()
# - view_company()
# - edit_company()



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
        data = {
            "error": False,
            "response": "Profile updated successfully",
            "is_login": user_login,
        }
        return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "response": validate_user.errors}
        return HttpResponse(json.dumps(data))



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

