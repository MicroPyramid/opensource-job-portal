"""
Resume Management Views
Handles resume pool operations and resume management
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



# Resume Management Views will be moved here
# TODO: Move the following functions from the main views.py:
# - resume_upload()
# - multiple_resume_upload()
# - resume_pool()
# - resume_view()
# - resume_edit()
# - download_applicants()



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
                        conn = S3Connection(
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
                            public=False,
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
                        conn = S3Connection(
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
                    conn = S3Connection(
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
                        conn = S3Connection(
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
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    for user in pending_applicants:
        if user.user.resume:
            stored_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': user.user.resume},
                ExpiresIn=600
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
