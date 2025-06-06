"""
Dashboard and Utility Views
Handles dashboard, utility functions, and miscellaneous views
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

# Dashboard and Utility Views will be moved here
# TODO: Move the following functions from the main views.py:
# - dashboard()
# - registration_success()
# - how_it_works()
# - interview_location()
# - create_slug()
# - get_autocomplete()


@recruiter_login_required
def dashboard(request):
    # active_jobs = JobPost.objects.filter(user=request.user, status='Live')
    # return render(request, 'recruiter/dashboard.html', {'active_jobs':
    # active_jobs})
    return HttpResponseRedirect(reverse("recruiter:list"))




@recruiter_login_required
def registration_success(request):
   
    return render(request, "recruiter/registration_success.html", {})




def how_it_works(request):
    return render(request, "recruiter/how_it_works.html", {})




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

