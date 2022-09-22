import datetime
import json
import tinys3
import random
import math
import re

from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from django.template import loader, Template, Context
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Case, When
from django.core.cache import cache

from mpcomp.views import (
    jobseeker_login_required,
    get_prev_after_pages_count,
    get_social_referer,
    get_resume_data,
    handle_uploaded_file,
    get_meta,
)
from candidate.forms import (
    PersonalInfoForm,
    ProfileDescriptionForm,
    WorkExperienceForm,
    EducationForm,
    DegreeForm,
    EducationInstitueForm,
    TechnicalSkillForm,
    ProjectForm,
    ProfessinalInfoForm,
    YEARS,
    MONTHS,
    DEGREE_TYPES,
    JobAlertForm,
)
from peeldb.models import (
    MetaData,
    User,
    City,
    Country,
    UserEmail,
    Industry,
    Language,
    UserLanguage,
    Subscriber,
    EmploymentHistory,
    Project,
    MARTIAL_STATUS,
    EducationDetails,
    Degree,
    EducationInstitue,
    Skill,
    TechnicalSkill,
    Qualification,
    JobPost,
    TechnicalSkill_STATUS,
    JobAlert,
    FunctionalArea,
    Question,
    AssessmentData,
    Solution,
    State,
    UserMessage,
)
from dashboard.tasks import send_email
from psite.forms import UserPassChangeForm
from django.contrib.auth import authenticate, login
from peeldb.models import JOB_TYPE
from pjob.views import add_other_location_to_user


def index(request):

    latest_jobs_list = cache.get("latest_1hr_jobs_list")
    if not latest_jobs_list:
        latest_jobs_list = (
            JobPost.objects.filter(status="Live")
            .exclude(job_type="walk-in")
            .select_related("company", "user")
            .prefetch_related("location", "skills")[:9]
        )
        cache.set("latest_1hr_jobs_list", latest_jobs_list, 60 * 60)

    latest_jobs_list = (
        JobPost.objects.filter(status="Live")
        .exclude(job_type="walk-in")
        .select_related("company", "user")
        .prefetch_related("location", "skills")[:9]
    )

    field = get_social_referer(request)
    show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
    meta_title, meta_description, h1_tag = get_meta("home_page", {"page": 1})
    states = State.objects.filter(status="Enabled")
    data = {
        "jobs_list": latest_jobs_list,
        "show_pop_up": show_pop,
        "meta_title": meta_title,
        "meta_description": meta_description,
        "job_types": JOB_TYPE,
        "h1_tag": h1_tag,
        "states": states,
    }

    template = "index.html"
    return render(request, template, data)


def applicant_unsubscribing(request, message_id):
    users = User.objects.filter(unsubscribe_code=message_id)
    if users:
        user = users[0]
        user.is_unsubscribe = True
        user.save()
    return HttpResponseRedirect("/")


def applicant_email_unsubscribing(request, email_type, message_id):
    if email_type == "alert":
        user = JobAlert.objects.filter(unsubscribe_code__iexact=message_id).first()
    elif email_type == "subscriber":
        user = Subscriber.objects.filter(unsubscribe_code__iexact=message_id).first()
    else:
        user = User.objects.filter(unsubscribe_code__iexact=message_id).first()
    if request.POST:
        if request.POST.get("reason") and user:
            user.is_unsubscribe = True
            user.unsubscribe_code = ""
            user.unsubscribe_reason = request.POST.get("reason")
            user.save()
            if email_type == "user":
                user = authenticate(username=user.username)
                login(request, user)
            return HttpResponse(json.dumps({"error": False}))
        elif not user:
            return HttpResponse(
                json.dumps(
                    {"error": True, "err_message": "You are alredy Unsubscribed"}
                )
            )
        else:
            return HttpResponse(
                json.dumps({"error": True, "message": "* Please provide a reason!"})
            )
    if not user:
        return render(request, "unsubscribe_alerts.html", {"unsubscribed": True})
    return render(request, "unsubscribe_alerts.html")


@csrf_exempt
def bounces(request):
    body = request.body
    json_body = body.decode("utf8")
    js = json.loads(json_body.replace("\n", ""))
    if js["Type"] == "Notification":
        arg_info = js["Message"]
        arg_info = json.loads(arg_info.replace("\n", ""))
        if (
            "notificationType" in arg_info.keys()
            and arg_info["notificationType"] == "Bounce"
        ):
            bounce_email_address = arg_info["bounce"]["bouncedRecipients"]
            for each in bounce_email_address:
                user = User.objects.filter(email=each["emailAddress"])
                user.update(is_bounce=True)
                job_alerts = JobAlert.objects.filter(email=each["emailAddress"])
                job_alerts.delete()
                subscribers = Subscriber.objects.filter(email=each["emailAddress"])
                subscribers.delete()

    return HttpResponse("Bounced Email has been updated Sucessfully.")


@login_required
def upload_resume(request):
    """validate file size <250kb and type doc,docx,pdf,rtf,odt"""
    if "resume" in request.FILES and request.user.user_type == "JS":
        fo = request.FILES["resume"]
        sup_formates = [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/pdf",
            "application/rtf",
            "application/x-rtf",
            "text/richtext",
            "application/msword",
            "application/vnd.oasis.opendocument.text",
            "application/x-vnd.oasis.opendocument.text",
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
                    expires="max",
                )
                request.user.resume = path
                request.user.profile_updated = datetime.datetime.now(timezone.utc)
                handle_uploaded_file(
                    request.FILES["resume"], request.FILES["resume"].name
                )
                email, mobile, text = get_resume_data(request.FILES["resume"])
                request.user.resume_text = text
                if not request.user.mobile:
                    request.user.mobile = mobile
                request.user.save()
                data = {
                    "error": False,
                    "data": "Resume Uploaded Successfully",
                    "profile_percantage": request.user.profile_completion_percentage,
                    "upload_resume": True,
                    "email": email,
                    "resume_name": request.FILES["resume"].name,
                    "resume_path": "https://"
                    + settings.AWS_STORAGE_BUCKET_NAME
                    + ".s3.amazonaws.com/"
                    + path,
                }
            else:
                data = {"error": True, "data": "File Size must be less than 300 kb"}
        else:
            data = {
                "error": True,
                "data": "Please upload valid files For Ex: Doc, Docx, PDF, odt format",
            }
        return HttpResponse(json.dumps(data))
    elif request.user.user_type == "RR":
        data = {"error": True, "data": "Recruiter is not allowed to Subscribe"}
    elif request.user.is_staff:
        data = {"error": True, "data": "Admin is not allowed to Subscribe"}
    else:
        data = {
            "error": True,
            "data": "Upload your resume either in Doc or Docx or PDF or ODT format",
        }
    return HttpResponse(json.dumps(data))


@login_required
def upload_profilepic(request):
    """validate file size <250kb and type doc,docx,pdf,rtf,odt"""
    if "profile_pic" in request.FILES:
        pic = request.FILES["profile_pic"]
        sup_formates = ["image/jpeg", "image/png"]
        ftype = pic.content_type
        if str(ftype) in sup_formates:
            request.user.profile_pic = request.FILES["profile_pic"]
            request.user.profile_updated = datetime.datetime.now(timezone.utc)
            request.user.save()
            data = {"error": False, "data": "Profile Pic Uploaded Successfully"}
        else:
            data = {
                "error": True,
                "data": "Please upload valid formats For Ex: JPEG, JPG, PNG format",
            }
    else:
        data = {
            "error": True,
            "data": "Upload your profile picture either in JPEG, JPG, PNG format",
        }
    return HttpResponse(json.dumps(data))


@jobseeker_login_required
def profile(request):
    """need to check user login or not"""
    if request.user.is_authenticated:
        messages = UserMessage.objects.filter(message_to=request.user.id, is_read=False)
        user = request.user
        user.profile_completeness = user.profile_completion_percentage
        user.save()

        nationality = ""
        functional_areas = FunctionalArea.objects.filter(status="Active").order_by(
            "name"
        )
        cities = (
            City.objects.filter(status="Enabled")
            .exclude(slug__icontains="india")
            .order_by("name")
        )
        skills = Skill.objects.filter(status="Active").order_by("name")
        industries = (
            Industry.objects.filter(status="Active").order_by("name").exclude(id=36)
        )
        if request.user.nationality:
            nationality = Country.objects.get(id=request.user.nationality)
        return render(
            request,
            "candidate/view_userinfo.html",
            {
                "nationality": nationality,
                "cities": cities,
                "skills": skills,
                "years": YEARS,
                "months": MONTHS,
                "industries": industries,
                "languages": Language.objects.all(),
                "martial_status": MARTIAL_STATUS,
                "functional_areas": functional_areas,
                "unread_messages": messages.count(),
            },
        )
    return HttpResponseRedirect("/")


@jobseeker_login_required
def edit_personalinfo(request):
    if request.method == "POST":
        validate_personalform = PersonalInfoForm(request.POST, instance=request.user)
        if validate_personalform.is_valid():
            user = validate_personalform.save(commit=False)
            if request.POST.get("dob"):
                dob = datetime.datetime.strptime(
                    request.POST.get("dob"), "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
                user.dob = dob
            user.marital_status = (
                request.POST.get("marital_status")
                if request.POST.get("marital_status")
                else None
            )
            user.first_name = request.POST.get("first_name")
            user.last_name = (
                request.POST.get("last_name") if request.POST.get("last_name") else None
            )
            user.alternate_mobile = (
                request.POST.get("alternate_mobile")
                if request.POST.get("alternate_mobile")
                else None
            )
            user.pincode = (
                request.POST.get("pincode") if request.POST.get("pincode") else None
            )
            user.gender = (
                request.POST.get("gender") if request.POST.get("gender") else None
            )
            user.address = request.POST.get("address")
            user.permanent_address = request.POST.get("permanent_address")
            user.resume_title = (
                request.POST.get("resume_title")
                if request.POST.get("resume_title")
                else None
            )
            user.nationality = 1
            if request.POST.get("current_city"):
                user.current_city = City.objects.get(
                    id=int(request.POST.get("current_city"))
                )
            # random_code = rand_string(size=6)
            # message = 'Hello ' + request.user.username + ', An OTP ' + random_code + \
            #     ' for your Peeljobs recruiter account, Please Confirm and Proceed'
            # data = {"username": settings.BULK_SMS_USERNAME, "password": settings.BULK_SMS_PASSWORD,
            #         "from": settings.BULK_SMS_FROM, "to": request.POST.get('mobile'), "message": message}
            # requests.get(
            #     "http://182.18.160.225/index.php/api/bulk-sms", params=data)
            # user.mobile_verification_code = random_codea
            user.mobile_verified = True
            user.last_mobile_code_verified_on = datetime.datetime.now(timezone.utc)
            user.profile_updated = datetime.datetime.now(timezone.utc)
            user.save()
            if request.POST.get("other_loc"):
                add_other_location_to_user(user, request)
            user.preferred_city.clear()
            user.preferred_city.add(*request.POST.getlist("preferred_city"))
            user.industry.clear()
            user.industry.add(*request.POST.getlist("industry"))
            user.functional_area.clear()
            user.functional_area.add(*request.POST.getlist("functional_area"))
            data = {
                "error": False,
                "response": "Presonal Info edited successfully",
                "profile_percantage": request.user.profile_completion_percentage,
                "personal_info": True,
                "first_name": user.first_name,
                "mobile": user.mobile,
                "resume_title": user.resume_title,
                "dob": datetime.datetime.strptime(str(user.dob), "%Y-%m-%d").strftime(
                    "%b %d, %Y"
                ),
                "current_city": user.current_city.name,
            }
        else:
            data = {"error": True, "response": validate_personalform.errors}
        return HttpResponse(json.dumps(data))
    else:
        cities = City.objects.filter(state__country_id=1, status="Enabled").order_by(
            "name"
        )
        countries = Country.objects.all()
        martial_status = MARTIAL_STATUS
        industires = (
            Industry.objects.filter(status="Active").order_by("name").exclude(id=36)
        )
        functional_areas = FunctionalArea.objects.filter(status="Active").order_by(
            "name"
        )
        data = {
            "martial_status": martial_status,
            "cities": cities,
            "countries": countries,
            "industries": industires,
            "functional_areas": functional_areas,
        }
        template = "candidate/edit_personalinfo.html"
        return render(request, template, data)


# @jobseeker_login_required
# def verify_mobile(request):
#     if request.method == 'POST':
#         validate_mobile = MobileVerifyForm(request.POST)
#         if validate_mobile.is_valid():
#             user = request.user
#             password_reset_diff = int(
#                 (datetime.datetime.now() - request.user.last_mobile_code_verified_on).seconds)
#             if password_reset_diff > 60:
#                 return HttpResponse(json.dumps({'error': True, 'response_message': 'OTP Is Expired, Please request new OTP'}))
#             if str(request.POST['mobile_verification_code']) != str(request.user.mobile_verification_code):
#                 return HttpResponse(json.dumps({'error': True, 'response': {'mobile_verification_code': "Otp didn't match, Try again later"}}))
#             user.mobile_verified = True
#             user.profile_updated = datetime.datetime.now(timezone.utc)
#             user.save()
#             return HttpResponse(json.dumps({'error': False, 'message': 'Mobile Verified successfully'}))
#         else:
#             return HttpResponse(json.dumps({'error': True, 'response': validate_mobile.errors}))
#     if not request.is_mobile:
#         return render(request, 'candidate/mobile_verify.html')
#     else:
#         return render(request, 'mobile/profile/mobile_verify.html')


# @jobseeker_login_required
# def send_mobile_verification_code(request):
#     if request.method == 'POST':
#         password_reset_diff = int(
#             (datetime.datetime.now() - request.user.last_mobile_code_verified_on).seconds)
#         if not password_reset_diff > 60:
#             return HttpResponse(json.dumps({'error': True, 'message': 'OTP Already sent to you, Please request new OTP'}))
#         user = request.user
#         random_code = rand_string(size=6)
#         message = 'Hello ' + request.user.username + ', An OTP ' + random_code + \
#             ' for your Peeljobs recruiter account, Please Confirm and Proceed'
#         data = {"username": settings.BULK_SMS_USERNAME, "password": settings.BULK_SMS_PASSWORD,
#                 "from": settings.BULK_SMS_FROM, "to": user.mobile, "message": message}
#         requests.get(
#             "http://182.18.160.225/index.php/api/bulk-sms", params=data)
#         user.mobile_verification_code = random_code
#         user.last_mobile_code_verified_on = datetime.datetime.now(timezone.utc)
#         user.save()
# return HttpResponse(json.dumps({'error': False, 'message': 'An OTP sent
# to your mobile successfully'}))


@login_required
def edit_profile_description(request):
    if request.method == "POST":
        validate_personalform = ProfileDescriptionForm(
            request.POST, instance=request.user
        )
        if validate_personalform.is_valid():
            user = validate_personalform.save()
            user.profile_updated = datetime.datetime.now(timezone.utc)
            user.save()
            data = {"error": False, "response": "Presonal Info edited successfully"}
        else:
            data = {"error": True, "response": validate_personalform.errors}
        return HttpResponse(json.dumps(data))
    template = "candidate/edit_profile_description.html"
    return render(request, template)


@login_required
def edit_professionalinfo(request):
    if request.method == "POST":
        validate_professionalinfo = ProfessinalInfoForm(
            request.POST, instance=request.user
        )
        if validate_professionalinfo.is_valid():
            user = validate_professionalinfo.save(commit=False)
            industry = Industry.objects.get(id=request.POST.get("prefered_industry"))
            user.prefered_industry = industry
            user.current_salary = request.POST.get("current_salary", "")
            user.expected_salary = request.POST.get("expected_salary")
            user.notice_period = request.POST.get("notice_period")
            user.relocation = str(request.POST.get("relocation")) == "on"
            user.profile_updated = datetime.datetime.now(timezone.utc)
            user.save()
            data = {
                "error": False,
                "info": "professional info edited successfully",
                "profile_percantage": request.user.profile_completion_percentage,
                "professional_info": True,
                "current_salary": user.current_salary,
                "expected_salary": user.expected_salary,
                "job_role": user.job_role,
                "year": user.year,
                "month": user.month,
                "notice_period": user.notice_period,
                "prefered_industry": industry.name,
            }
        else:
            data = {"error": True, "response": validate_professionalinfo.errors}
        return HttpResponse(json.dumps(data))
    else:
        data = {
            "industires": Industry.objects.filter(status="Active").exclude(id=36),
            "years": YEARS,
            "months": MONTHS,
        }
        template = "candidate/edit_professionalInfo.html"
        return render(request, template, data)


@login_required
def add_language(request):
    if request.method == "GET":
        languages = Language.objects.all()
        template = "candidate/add_language.html"
        return render(request, template, {"languages": languages})
    if request.POST.get("language"):
        if request.user.language.filter(language_id=request.POST.get("language")):
            data = {
                "error": True,
                "response_message": "You have already created this langugae in your profile",
            }
            return HttpResponse(json.dumps(data))
        read = request.POST.get("read") == "on"
        write = request.POST.get("write") == "on"
        speak = request.POST.get("speak") == "on"
        if read or write or speak:
            language = Language.objects.get(id=request.POST.get("language"))
            language = UserLanguage.objects.create(
                language=language, read=read, write=write, speak=speak
            )
            user = request.user
            request.user.language.add(language)
            user.profile_updated = datetime.datetime.now(timezone.utc)
            request.user.save()
            data = {"error": False, "response": "language added"}
        else:
            data = {
                "error": True,
                "language": "Please Select atleast any read/write/speak  option",
            }
        return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "response": "Please select the language"}
        return HttpResponse(json.dumps(data))


@login_required
def edit_language(request, language_id):
    user_language = UserLanguage.objects.filter(user=request.user, id=language_id)
    if request.method == "GET":
        languages = Language.objects.all()
        if user_language:
            template = "candidate/editlanguage.html"
            data = {"language": user_language[0], "languages": languages}
        else:
            template = "404.html"
            data = {
                "message": "Sorry, User with this language not exists",
                "reason": "The URL may be misspelled or the language you're looking for is no longer available.",
            }
        return render(request, template, data, status=200 if user_language else 404)
    if request.POST.get("get_lang"):
        lan = UserLanguage.objects.filter(user=request.user, id=language_id).first()
        data = {
            "error": False,
            "id": lan.language.id,
            "read": lan.read,
            "write": lan.write,
            "speak": lan.speak,
        }
        return HttpResponse(json.dumps(data))
    if request.POST.get("edit_lang") and request.POST.get("language"):
        # if request.user.language.filter(
        #     language_id=request.POST.get("language")
        # ).exclude(id=language_id):
        #     data = {
        #         "error": True,
        #         "response": "You have already created this langugae in your profile",
        #     }
        #     return HttpResponse(json.dumps(data))
        read = request.POST.get("read") == "on"
        write = request.POST.get("write") == "on"
        speak = request.POST.get("speak") == "on"
        if read or write or speak:
            language = user_language[0]
            lang = Language.objects.get(id=request.POST.get("language"))
            language.language = lang
            language.read = read
            language.write = write
            language.speak = speak
            language.save()
            user = request.user
            user.profile_updated = datetime.datetime.now(timezone.utc)
            user.save()
            data = {"error": False, "response": "language updated"}
        else:
            data = {
                "error": True,
                "response": "Please Select atleast any read/write/speak option",
            }
        return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "response": "Please select the language"}
        return HttpResponse(json.dumps(data))


@login_required
def delete_language(request, language_id):
    user_language = UserLanguage.objects.filter(user=request.user, id=language_id)
    if user_language:
        language = user_language[0]
        language.delete()
        user = request.user
        user.profile_updated = datetime.datetime.now(timezone.utc)
        user.save()

        data = {"error": False, "message": "language deleted successfully"}
    else:
        data = {"error": True, "errinfo": "language not exist"}
    return HttpResponse(json.dumps(data))


@login_required
def add_experience(request):
    if request.method == "GET":
        template = "candidate/add_experience.html"
        return render(request, template)
    work_experience = WorkExperienceForm(request.POST)
    if work_experience.is_valid():
        if request.user.employment_history.filter(
            company=request.POST.get("company"),
            designation=request.POST.get("designation"),
        ):
            data = {
                "error": True,
                "response_message": "Experince with this company and designation already exists",
            }
            return HttpResponse(json.dumps(data))
        experience = work_experience.save(commit=False)
        if request.POST.get("current_job") == "on":
            current_job = True
        else:
            current_job = False
            to = datetime.datetime.strptime(
                request.POST.get("to_date"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
            experience.to_date = to
        experience.from_date = datetime.datetime.strptime(
            request.POST.get("from_date"), "%m/%d/%Y"
        ).strftime("%Y-%m-%d")
        experience.current_job = current_job
        experience.salary = request.POST.get("salary")
        experience.job_profile = request.POST.get("job_profile")

        experience.save()
        user = request.user
        user.employment_history.add(experience)
        user.profile_updated = datetime.datetime.now(timezone.utc)
        user.save()

        request.user.save()

        data = {"error": False, "response": "experience added"}
        return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "response": work_experience.errors}
        return HttpResponse(json.dumps(data))


@login_required
def edit_experience(request, experience_id):
    experiences = EmploymentHistory.objects.filter(id=experience_id)
    if request.method == "GET":
        if experiences:
            experience = experiences[0]
            template = "candidate/edit_experience.html"
            data = {"experience": experience}
        else:
            template = "404.html"
            data = {
                "message": "Sorry, User with this Experience not exists",
                "reason": "The URL may be misspelled or the experience you're looking for is no longer available.",
            }
        return render(request, template, data, status=200 if experiences else 404)
    work_experience = WorkExperienceForm(request.POST, instance=experiences[0])
    if request.user.employment_history.filter(
        company=request.POST.get("company"), designation=request.POST.get("designation")
    ).exclude(id=experience_id):
        data = {
            "error": True,
            "response_message": "Experince with this company and designation already exists",
        }
        return HttpResponse(json.dumps(data))
    else:
        if work_experience.is_valid():
            experience = work_experience.save(commit=False)
            if request.POST.get("current_job") == "on":
                current_job = True
                experience.to_date = request.POST.get("to_date")
            else:
                current_job = False
                to = datetime.datetime.strptime(
                    request.POST.get("to_date"), "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
                experience.to_date = to
            if request.POST.get("from_date"):
                experience.from_date = datetime.datetime.strptime(
                    request.POST.get("from_date"), "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
            experience.current_job = current_job
            experience.salary = request.POST.get("salary")
            if request.POST.get("job_profile"):
                experience.job_profile = request.POST.get("job_profile")

            experience.save()
            user = request.user
            user.profile_updated = datetime.datetime.now(timezone.utc)
            user.save()

            data = {"error": False, "response": "work history updated successfully"}
        else:
            data = {"error": True, "response": work_experience.errors}
        return HttpResponse(json.dumps(data))


@login_required
def delete_experience(request, experience_id):
    experiences = EmploymentHistory.objects.filter(id=experience_id)
    if experiences:
        experiences[0].delete()
        user = request.user
        user.profile_updated = datetime.datetime.now(timezone.utc)
        user.save()
        data = {"error": False, "response": "work history deleted successfully"}
    else:
        data = {"error": True, "response": "work history not exist"}
    return HttpResponse(json.dumps(data))


@login_required
def add_education(request):
    if request.method == "GET":
        template = "candidate/add_education.html"
        return render(
            request,
            template,
            {
                "degree_types": DEGREE_TYPES,
                "qualifications": Qualification.objects.filter(
                    status="Active"
                ).order_by("name"),
                "cities": City.objects.filter(status="Enabled").order_by("name"),
            },
        )
    education_valid = EducationForm(request.POST)
    degree_valid = DegreeForm(request.POST)
    education_institute_valid = EducationInstitueForm(request.POST)
    if (
        education_valid.is_valid()
        and degree_valid.is_valid()
        and education_institute_valid.is_valid()
    ):
        if request.user.education.filter(
            degree__degree_name=request.POST.get("degree_name")
        ):
            return HttpResponse(
                json.dumps(
                    {"error": True, "response_message": "education already exists"}
                )
            )
        city = City.objects.get(id=request.POST.get("city"))
        institute = EducationInstitue.objects.create(
            name=request.POST.get("name"), city=city
        )
        if request.POST.get("address"):
            institute.address = request.POST.get("address")
            institute.save()
        degree_name = Qualification.objects.get(id=request.POST.get("degree_name"))
        degree = Degree.objects.create(
            degree_name=degree_name,
            degree_type=request.POST.get("degree_type"),
            specialization=request.POST.get("specialization"),
        )
        to = (
            None
            if (request.POST.get("current_education") == "on")
            else datetime.datetime.strptime(
                request.POST.get("to_date"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
        )
        from_date = datetime.datetime.strptime(
            request.POST.get("from_date"), "%m/%d/%Y"
        ).strftime("%Y-%m-%d")
        education = EducationDetails.objects.create(
            institute=institute,
            degree=degree,
            score=request.POST.get("score"),
            from_date=from_date,
            to_date=to,
            current_education=request.POST.get("current_education") == "on",
        )
        request.user.profile_updated = datetime.datetime.now(timezone.utc)
        request.user.save()
        request.user.education.add(education)
        return HttpResponse(
            json.dumps({"error": False, "response": "education details added"})
        )
    else:
        errors = {}
        for k in education_valid.errors:
            errors[k] = education_valid.errors[k][0]
        for k in degree_valid.errors:
            errors[k] = degree_valid.errors[k][0]
        for k in education_institute_valid.errors:
            errors[k] = education_institute_valid.errors[k][0]
        return HttpResponse(json.dumps({"error": True, "response": errors}))


@login_required
def edit_education(request, education_id):
    education = EducationDetails.objects.filter(id=education_id).first()
    if education:
        if request.method == "GET":
            template = "candidate/edit_education.html"
            return render(
                request,
                template,
                {
                    "degree_types": DEGREE_TYPES,
                    "qualifications": Qualification.objects.filter(
                        status="Active"
                    ).order_by("name"),
                    "education": education,
                    "cities": City.objects.filter(status="Enabled").order_by("name"),
                },
            )
        student_degree = Degree.objects.get(id=education.degree.id)
        degree_valid = DegreeForm(request.POST, student_degree)
        institute = EducationInstitue.objects.get(id=education.institute.id)
        education_institute_valid = EducationInstitueForm(request.POST, institute)
        education_valid = EducationForm(request.POST, education, student_degree)
        if (
            education_valid.is_valid()
            and degree_valid.is_valid()
            and education_institute_valid.is_valid()
        ):
            degree_name = Qualification.objects.get(id=request.POST.get("degree_name"))

            if request.user.education.filter(
                degree__degree_name=request.POST.get("degree_name")
            ).exclude(id=education_id):
                return HttpResponse(
                    json.dumps(
                        {"error": True, "response_message": "Education already exists"}
                    )
                )

            student_degree.degree_name = degree_name
            student_degree.degree_type = request.POST.get("degree_type")
            student_degree.specialization = request.POST.get("specialization")
            student_degree.save()

            institute.name = request.POST.get("name")
            if request.POST.get("address"):
                institute.address = request.POST.get("address")
            city = City.objects.get(id=request.POST.get("city"))
            institute.city = city
            institute.save()

            education.degree = student_degree
            education.institute = institute
            education.from_date = datetime.datetime.strptime(
                request.POST.get("from_date"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
            education.to_date = (
                None
                if (request.POST.get("current_education") == "on")
                else datetime.datetime.strptime(
                    request.POST.get("to_date"), "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
            )
            education.score = request.POST.get("score")
            education.current_education = request.POST.get("current_education") == "on"
            education.save()
            user = request.user
            user.profile_updated = datetime.datetime.now(timezone.utc)
            user.save()

            return HttpResponse(
                json.dumps(
                    {"error": False, "response": "education updated successfully"}
                )
            )
        else:
            errors = {}
            for k in education_valid.errors:
                errors[k] = education_valid.errors[k][0]
            for k in degree_valid.errors:
                errors[k] = degree_valid.errors[k][0]
            for k in education_institute_valid.errors:
                errors[k] = education_institute_valid.errors[k][0]
            return HttpResponse(json.dumps({"error": True, "response": errors}))
    else:
        template = "404.html"
        reason = "The URL may be misspelled or the education you're looking for is no longer available."
        return render(
            request,
            template,
            {"message": "Sorry, User with this Education not exists", "reason": reason},
            status=404,
        )


@login_required
def delete_education(request, education_id):
    educations = EducationDetails.objects.filter(id=education_id)
    if educations:
        educations[0].delete()
        user = request.user
        user.profile_updated = datetime.datetime.now(timezone.utc)
        user.save()
        data = {"error": False, "response": "education deleted successfully"}
    else:
        data = {"error": True, "repsonse": "education not exist"}
    return HttpResponse(json.dumps(data))


@login_required
def add_technicalskill(request):
    if request.method == "GET":
        user_skills = request.user.skills.values_list("skill", flat=True)
        skills = (
            Skill.objects.filter(status="Active")
            .exclude(id__in=user_skills)
            .order_by("name")
        )
        template = "candidate/add_technicalskill.html"
        return render(
            request,
            template,
            {
                "years": YEARS,
                "months": MONTHS,
                "skills": skills,
                "status": TechnicalSkill_STATUS,
            },
        )
    technical_skill = TechnicalSkillForm(request.POST, requested_user=request.user)
    if technical_skill.is_valid():
        if request.user.skills.filter(skill__id=request.POST.get("skill")):
            data = {
                "error": True,
                "response_message": "You have already created this skill in your profile",
            }
            return HttpResponse(json.dumps(data))
        skill = technical_skill.save()
        if request.POST.get("last_used"):
            last_used = datetime.datetime.strptime(
                request.POST.get("last_used"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
            skill.last_used = last_used
        skill.version = request.POST.get("version")
        skill.proficiency = request.POST.get("proficiency")
        user = request.user
        user.profile_updated = datetime.datetime.now(timezone.utc)
        skill.is_major = True if request.POST.get("is_major") else False
        skill.save()
        user.save()
        user.skills.add(skill)
        data = {
            "error": False,
            "response": "techskills added",
            "profile_percantage": request.user.profile_completion_percentage,
            "technical_skill": True,
        }
    else:
        data = {"error": True, "response": technical_skill.errors}
    return HttpResponse(json.dumps(data))


@login_required
def edit_technicalskill(request, technical_skill_id):
    skill = TechnicalSkill.objects.filter(id=technical_skill_id)
    if skill:
        if request.method == "GET":
            skills = Skill.objects.filter(status="Active").order_by("name")
            template = "candidate/edit_technicalskill.html"
            return render(
                request,
                template,
                {
                    "years": YEARS,
                    "months": MONTHS,
                    "skills": skills,
                    "technical_skill": skill[0],
                    "status": TechnicalSkill_STATUS,
                },
            )
        technical_skill = TechnicalSkillForm(
            request.POST, requested_user=request.user, instance=skill[0]
        )
        if technical_skill.is_valid():
            if request.user.skills.filter(skill_id=request.POST.get("skill")).exclude(
                id=technical_skill_id
            ):
                data = {
                    "error": True,
                    "response_message": "You have already created this skill in your profile",
                }
                return HttpResponse(json.dumps(data))
            technical_skill = technical_skill.save(commit=False)
            if request.POST.get("last_used"):
                last_used = datetime.datetime.strptime(
                    request.POST.get("last_used"), "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
                technical_skill.last_used = last_used
            technical_skill.version = request.POST.get("version")
            technical_skill.proficiency = request.POST.get("proficiency")
            user = request.user
            user.profile_updated = datetime.datetime.now(timezone.utc)
            user.save()
            technical_skill.is_major = True if request.POST.get("is_major") else False
            technical_skill.save()
            data = {"error": False, "response": "skillinfo updated successfully"}
        else:
            data = {"error": True, "response": technical_skill.errors}
        return HttpResponse(json.dumps(data))
    else:
        message = "Sorry, User with this Technical Skill not exists"
        template = "404.html"
        return render(request, template, {"message": message}, status=404)


@login_required
def delete_technicalskill(request, technical_skill_id):
    skill = TechnicalSkill.objects.filter(id=technical_skill_id)
    if skill:
        skill.delete()
        user = request.user
        user.profile_updated = datetime.datetime.now(timezone.utc)
        user.save()
        data = {"error": False, "response": "tech skill deleted successfully"}
    else:
        data = {"error": True, "response": "tech skill not exist"}
    return HttpResponse(json.dumps(data))


@login_required
def add_project(request):
    if request.method == "GET":
        template = "candidate/add_project.html"
        return render(
            request,
            template,
            {
                "skills": Skill.objects.filter(status="Active"),
                "cities": City.objects.filter(status="Enabled"),
            },
        )
    project_form = ProjectForm(request.POST)
    if project_form.is_valid():
        if User.objects.filter(
            id=request.user.id, project__name=request.POST.get("name")
        ):
            data = {"error": True, "response_message": "Project already exists"}
            return HttpResponse(json.dumps(data))
        project = project_form.save()
        if request.POST.get("role"):
            project.role = request.POST.get("role")
        if request.POST.get("size"):
            project.size = request.POST.get("size")
        if request.POST.get("location"):
            project.location_id = request.POST.get("location")
        project.save()
        user = request.user
        user.profile_updated = datetime.datetime.now(timezone.utc)
        user.save()
        user.project.add(project)
        data = {"error": False, "response": "project added"}
    else:
        data = {"error": True, "response": project_form.errors}
    return HttpResponse(json.dumps(data))


@login_required
def edit_project(request, project_id):
    projects = Project.objects.filter(id=project_id)
    if projects:
        if request.method == "GET":
            template = "candidate/edit_project.html"
            return render(
                request,
                template,
                {
                    "project": projects[0],
                    "skills": Skill.objects.filter(status="Active"),
                    "cities": City.objects.filter(status="Enabled"),
                },
            )
        project_form = ProjectForm(request.POST, instance=projects[0])
        if project_form.is_valid():
            if request.user.project.filter(name=request.POST.get("name")).exclude(
                id=project_id
            ):
                data = {"error": True, "response_message": "Project already exists"}
                return HttpResponse(json.dumps(data))
            project = project_form.save()
            if request.POST.get("role"):
                project.role = request.POST.get("role")
            if request.POST.get("size"):
                project.size = request.POST.get("size")
            if request.POST.get("location"):
                project.location_id = request.POST.get("location")
            project.save()
            user = request.user
            user.profile_updated = datetime.datetime.now(timezone.utc)
            user.save()

            data = {"error": False, "response": "project added"}
        else:
            data = {"error": True, "response": project_form.errors}
        return HttpResponse(json.dumps(data))
    else:
        message = "Sorry, User with this Project not exists"
        template = "404.html"
        return render(request, template, {"message": message}, status=404)


@login_required
def delete_project(request, project_id):
    projects = Project.objects.filter(id=project_id)
    if projects:
        projects.delete()
        user = request.user
        user.profile_updated = datetime.datetime.now(timezone.utc)
        user.save()
        data = {"error": False, "response": "Project deleted successfully"}
    else:
        data = {"error": True, "response": "Project not exist"}
    return HttpResponse(json.dumps(data))


@login_required
def edit_email(request):
    if request.method == "POST":
        user = UserEmail.objects.filter(user=request.user, is_primary=True)
        if user:
            user = user[0]
            user.is_primary = False
            requested_email = UserEmail.objects.get(id=request.POST.get("email"))
            requested_email.is_primary = True
            requested_email.save()
            user.save()
            user = request.user
            user.profile_updated = datetime.datetime.now(timezone.utc)
            user.save()
            data = {"error": False, "message": "changed successfully"}
        else:
            data = {"error": True, "errinfo": "no email to change"}
        return HttpResponse(json.dumps(data))

    else:
        template = "candidate/edit_email.html"
        return render(request, template)


def job_alert(request):
    if request.method == "GET":
        meta_title = meta_description = h1_tag = ""
        meta = MetaData.objects.filter(name="alerts_list")
        if meta:
            meta_title = Template(meta[0].meta_title).render(Context({}))
            meta_description = Template(meta[0].meta_description).render(Context({}))
            h1_tag = Template(meta[0].h1_tag).render(Context({}))
        template = "alert/job_alert.html"
        return render(
            request,
            template,
            {
                "skills": Skill.objects.filter(status="Active"),
                "industires": Industry.objects.filter(status="Active"),
                "cities": City.objects.filter(status="Enabled"),
                "years": YEARS,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "h1_tag": h1_tag,
            },
        )
    validate_jobalert = JobAlertForm(request.POST)
    if validate_jobalert.is_valid():
        job_alert = JobAlert.objects.create(name=request.POST.get("name"))
        if request.POST.get("min_year"):
            job_alert.min_year = request.POST.get("min_year")
            job_alert.max_year = request.POST.get("max_year", "")
        if request.POST.get("min_salary"):
            job_alert.min_salary = request.POST.get("min_salary", "")
            job_alert.max_salary = request.POST.get("max_salary", "")
        job_alert.role = request.POST.get("role", "")
        if request.POST.getlist("location"):
            job_alert.location.add(*request.POST.getlist("location"))
        if request.POST.getlist("industry"):
            job_alert.industry.add(*request.POST.getlist("industry"))
        job_alert.email = (
            request.user.email
            if request.user.is_authenticated
            else request.POST.get("email", "")
        )
        while True:
            unsubscribe_code = get_random_string(length=15)
            if not JobAlert.objects.filter(unsubscribe_code__iexact=unsubscribe_code):
                break
        job_alert.unsubscribe_code = unsubscribe_code
        while True:
            subscribe_code = get_random_string(length=15)
            if not JobAlert.objects.filter(subscribe_code__iexact=subscribe_code):
                break
        job_alert.subscribe_code = subscribe_code
        job_alert.save()
        job_alert.skill.add(*request.POST.getlist("skill"))
        temp = loader.get_template("email/job_alert.html")
        subject = "Job Alert Confirmation"
        url = (
            request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + "/alert/verification/"
            + str(job_alert.subscribe_code)
            + "/"
        )
        c = {
            "alert": job_alert,
            "user": request.user,
            "new_alert": True,
            "verify_alert": True,
            "redirect_url": url,
        }
        rendered = temp.render(c)
        user_active = (
            True if request.user.is_authenticated and request.user.is_active else False
        )
        mto = request.POST.get("email")
        send_email.delay(mto, subject, rendered)
        return HttpResponse(
            json.dumps(
                {
                    "error": False,
                    "message": "job alert created successfully",
                    "alert_id": job_alert.id,
                }
            )
        )
    else:
        return HttpResponse(
            json.dumps({"error": True, "message": validate_jobalert.errors})
        )


def alert_subscribe_verification(request, obj_type, obj_id):
    if obj_type == "alert":
        value = JobAlert.objects.filter(subscribe_code__iexact=obj_id).first()
    else:
        value = Subscriber.objects.filter(subscribe_code__iexact=obj_id).first()
        if value:
            subscribers = Subscriber.objects.filter(email=value.email)
            for sub in subscribers:
                sub.is_verified = True
                sub.save()
    if value:
        verified = value.is_verified
        value.is_verified = True
        value.save()
        user = User.objects.filter(email=value.email).first()
        if user:
            user.is_active = True
            user.save()
        if verified:
            return HttpResponseRedirect("/jobs/?verification=verified")
        return HttpResponseRedirect("/jobs/?verification=success")
    return HttpResponseRedirect(
        "/jobs/?verification=error&type="
        + ("Alerts" if obj_type == "alert" else "Subscribers")
    )


def job_alert_results(request, job_alert_id):
    if request.user.is_authenticated and request.user.user_type == "JS":
        job_alerts = JobAlert.objects.filter(id=job_alert_id, email=request.user.email)
    else:
        job_alerts = JobAlert.objects.filter(id=job_alert_id)

    if request.user.is_authenticated:
        if request.user.is_staff or request.user.user_type == "RR":
            message = "Sorry, No Job Alerts Availableble"
            template = "404.html"
            return render(request, template, {"message": message}, status=404)

    if job_alerts:
        job_alert = job_alerts[0]
        jobs_list = JobPost.objects.filter(
            (Q(skills__in=job_alert.skill.all(), status="Live"))
            & (
                Q(industry__in=job_alert.industry.all())
                | Q(min_year=job_alert.min_year)
                | Q(max_year=job_alert.max_year)
                | Q(max_salary=job_alert.max_salary)
                | Q(min_salary=job_alert.min_salary)
                | Q(job_role=job_alert.role)
                | Q(location__in=job_alert.location.all())
            )
        ).distinct()
        if not jobs_list:
            jobs_list = JobPost.objects.filter(
                status="Live", skills__in=job_alert.skill.all()
            )
        items_per_page = 10
        no_pages = int(math.ceil(float(jobs_list.count()) / items_per_page))

        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                page = 1
                return HttpResponseRedirect("/")
            else:
                page = int(request.GET.get("page"))
        else:
            page = 1

        jobs_list = jobs_list[(page - 1) * items_per_page : page * items_per_page]

        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        data = {
            "jobs_list": jobs_list,
            "job_alert": job_alert,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
        }
        template = "alert/job_alert_results.html"
        return render(request, template, data)
    else:
        template = "alert/list.html"
        return render(request, "alert/list.html", {"job_alerts": []})


def modify_job_alert(request, job_alert_id):
    job_alerts = JobAlert.objects.filter(id=job_alert_id)
    if job_alerts:
        job_alert = job_alerts[0]
        if request.method == "GET":
            data = {
                "skills": Skill.objects.filter(status="Active"),
                "industires": Industry.objects.filter(status="Active"),
                "cities": City.objects.filter(status="Enabled"),
                "years": YEARS,
                "job_alert": job_alert,
            }
            template = "alert/modify_job_alert.html"
            return render(request, template, data)
        validate_jobalert = JobAlertForm(request.POST, instance=job_alert)
        if validate_jobalert.is_valid():
            job_alert.name = request.POST.get("name")
            if request.POST.get("min_year"):
                job_alert.min_year = request.POST.get("min_year", "")
                job_alert.max_year = request.POST.get("max_year", "")
            if request.POST.get("min_salary"):
                job_alert.min_salary = request.POST.get("min_salary", "")
                job_alert.max_salary = request.POST.get("max_salary", "")
            job_alert.role = request.POST.get("role")
            job_alert.save()

            job_alert.skill.clear()
            job_alert.location.clear()
            job_alert.industry.clear()

            job_alert.skill.add(*request.POST.getlist("skill"))
            if request.POST.getlist("location"):
                job_alert.location.add(*request.POST.getlist("location"))
            if request.POST.getlist("industry"):
                job_alert.industry.add(*request.POST.getlist("industry"))

            data = {
                "error": False,
                "message": "job alert updated successfully",
                "alert_id": job_alert.id,
            }
        else:
            data = {"error": True, "message": validate_jobalert.errors}
        return HttpResponse(json.dumps(data))
    else:
        message = "Sorry, No Alerts Fount"
        template = "404.html"
        return render(request, template, {"message": message}, status=404)


def alerts_list(request, **kwargs):
    meta_title = meta_description = h1_tag = ""
    meta = MetaData.objects.filter(name="alerts_list")
    if meta:
        meta_title = Template(meta[0].meta_title).render(Context({}))
        meta_description = Template(meta[0].meta_description).render(Context({}))
        h1_tag = Template(meta[0].h1_tag).render(Context({}))
    if request.user.is_authenticated:
        job_alerts = JobAlert.objects.filter(email=request.user.email)

        items_per_page = 5
        no_pages = int(math.ceil(float(job_alerts.count()) / items_per_page))

        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                page = 1
                return HttpResponseRedirect("/")
            else:
                page = int(request.GET.get("page"))
        else:
            page = 1
        if kwargs:
            page = int(kwargs["page_num"])

        job_alerts = job_alerts[(page - 1) * items_per_page : page * items_per_page]

        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        template = "alert/list.html"
        return render(
            request,
            template,
            {
                "job_alerts": job_alerts,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
                "current_url": reverse("my:alerts_list"),
                "meta_title": meta_title,
                "meta_description": meta_description,
                "h1_tag": h1_tag,
            },
        )
    else:
        template = "alert/job_alert.html"
        return render(
            request,
            template,
            {
                "skills": Skill.objects.filter(status="Active"),
                "industires": Industry.objects.filter(status="Active"),
                "cities": City.objects.filter(status="Enabled"),
                "years": YEARS,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "h1_tag": h1_tag,
            },
        )


def delete_job_alert(request, job_alert_id):
    job_alerts = JobAlert.objects.filter(id=job_alert_id)
    if job_alerts:
        job_alerts[0].delete()
        data = {"error": False, "response": "job alerts deleted successfully"}
    else:
        data = {"error": True, "response": "job alert not exist"}
    return HttpResponse(json.dumps(data))


@login_required
def edit_emailnotifications(request):
    if request.method == "POST":
        user = request.user
        user.email_notifications = False if user.email_notifications else True
        user.save()
        data = {
            "status": user.email_notifications,
            "response": "Updated Successfully",
            "error": False,
        }
    else:
        data = {"error": True}
    return HttpResponse(json.dumps(data))


@login_required
def delete_resume(request):
    if request.method == "POST":
        request.user.resume = ""
        request.user.save()
        data = {"error": False, "response": "Your resume deleted Successfully"}
    else:
        data = {"error": False, "response": "Updated Successfully"}
    return HttpResponse(json.dumps(data))


@login_required
def user_password_change(request):
    if request.method == "POST":
        validate_changepassword = UserPassChangeForm(request.POST)
        if validate_changepassword.is_valid():
            user = request.user
            if request.POST["new_password"] != request.POST["retype_password"]:
                return HttpResponse(
                    json.dumps(
                        {
                            "error": True,
                            "response_message": "Password and ConfirmPasswords did not match",
                        }
                    )
                )
            user.set_password(request.POST["new_password"])
            user.save()
            return HttpResponse(
                json.dumps({"error": False, "message": "Password changed successfully"})
            )
        else:
            return HttpResponse(
                json.dumps({"error": True, "response": validate_changepassword.errors})
            )
    template = "candidate/change_user_password.html"
    return render(request, template)


def question_view(request, que_id):
    question = Question.objects.filter(status="Live", id=que_id).first()
    latest_questions = Question.objects.filter(status="Live").order_by("-modified_on")
    meta_title = meta_description = h1_tag = ""
    if question:
        meta = MetaData.objects.filter(name="question_view")
        if meta:
            meta_title = Template(meta[0].meta_title).render(Context({}))
            meta_description = Template(meta[0].meta_description).render(Context({}))
            h1_tag = Template(meta[0].h1_tag).render(Context({}))
        return render(
            request,
            "assessments/question_view.html",
            {
                "question": question,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "h1_tag": h1_tag,
                "latest_questions": latest_questions[:7],
            },
        )
    template = "404.html"
    data = {
        "message": "Sorry, Question does not exists",
        "reason": "The URL may be misspelled or the language you're looking for is no longer available.",
    }
    return render(request, template, data, status=404)


def assessments_questions(request, **kwargs):
    current_url = reverse("assessments_questions")
    questions = Question.objects.filter(status="Live")
    latest_jobs = (
        JobPost.objects.filter(status="Live")
        .exclude(job_type="walk-in")
        .select_related("company")
        .prefetch_related("location", "skills")[:7]
    )
    search = request.GET.get("search", "")
    if search:
        questions = questions.filter(title__icontains=search)
    items_per_page = 20
    no_of_que = questions.count()
    no_pages = int(math.ceil(float(no_of_que) / items_per_page))
    page = kwargs.get("page_num", 1)
    if page and int(page) > 0:
        if int(page) > (no_pages + 2):
            return HttpResponseRedirect(reverse("assessments_questions"))
        else:
            page = int(page)
    else:
        page = 1
    questions = questions[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    meta_title = meta_description = h1_tag = ""
    meta = MetaData.objects.filter(name="question_view")
    if meta:
        meta_title = Template(meta[0].meta_title).render(Context({}))
        meta_description = Template(meta[0].meta_description).render(Context({}))
        h1_tag = Template(meta[0].h1_tag).render(Context({}))
    return render(
        request,
        "assessments/questions_list.html",
        {
            "questions": questions,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "current_url": current_url,
            "no_of_que": no_of_que,
            "latest_jobs": latest_jobs,
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
            "search": search,
        },
    )


def assessment_changes(request):
    user = request.user
    if request.POST.get("mode") == "add_like":
        model = request.POST.get("model")
        obj_id = request.POST.get("id")
        if model == "question":
            like = AssessmentData.objects.filter(
                question=Question.objects.get(id=int(obj_id)), user=user, comment=""
            ).first()
            if like:
                like.like = True
                like.dislike = False
                like.save()
            else:
                AssessmentData.objects.create(
                    question=Question.objects.get(id=int(obj_id)), user=user, like=True
                )
        else:
            like = AssessmentData.objects.filter(
                solution=Solution.objects.get(id=int(obj_id)), user=user, comment=""
            ).first()
            if like:
                like.like = True
                like.dislike = False
                like.save()
            else:
                AssessmentData.objects.create(
                    solution=Solution.objects.get(id=int(obj_id)), like=True, user=user
                )
        return HttpResponse(json.dumps({"error": False}))
    if request.POST.get("mode") == "dis_like":
        model = request.POST.get("model")
        obj_id = request.POST.get("id")
        if model == "question":
            dislike = AssessmentData.objects.filter(
                question=Question.objects.get(id=int(obj_id)), user=user, comment=""
            ).first()
            if dislike:
                dislike.like = False
                dislike.dislike = True
                dislike.save()
            else:
                AssessmentData.objects.create(
                    question=Question.objects.get(id=int(obj_id)),
                    user=user,
                    dislike=True,
                )
        else:
            dislike = AssessmentData.objects.filter(
                solution=Solution.objects.get(id=int(obj_id)), user=user, comment=""
            ).first()
            if dislike:
                dislike.like = False
                dislike.dislike = True
                dislike.save()
            else:
                AssessmentData.objects.create(
                    solution=Solution.objects.get(id=int(obj_id)),
                    dislike=True,
                    user=user,
                )
        return HttpResponse(json.dumps({"error": False}))
    if request.POST.get("mode") == "add_comment":
        if request.POST.get("comment"):
            model = request.POST.get("model")
            obj_id = request.POST.get("id")
            if model == "question":
                AssessmentData.objects.create(
                    question=Question.objects.get(id=int(obj_id)),
                    user=user,
                    comment=request.POST.get("comment"),
                )
            else:
                AssessmentData.objects.create(
                    solution=Solution.objects.get(id=int(obj_id)),
                    user=user,
                    comment=request.POST.get("comment"),
                )
            return HttpResponse(
                json.dumps({"error": False, "comment": request.POST.get("comment")})
            )
        else:
            return HttpResponse(
                json.dumps({"error": True, "message": "Please enter your comment"})
            )
    return HttpResponse(json.dumps({"error": True}))


def get_messages(request):
    if request.POST.get("job_id"):
        UserMessage.objects.filter(
            message_to=request.user.id, job=int(request.POST.get("job_id"))
        ).update(is_read=True)

        messages = UserMessage.objects.filter(
            job__id=int(request.POST.get("job_id"))
            & (Q(message_from=request.user.id) | Q(message_to=request.user.id))
        )

    else:
        UserMessage.objects.filter(
            message_to=request.user.id, message_from=int(request.POST.get("r_id"))
        ).update(is_read=True)

        messages = UserMessage.objects.filter(
            Q(
                message_from=request.user.id,
                message_to=int(request.POST.get("r_id")),
                job__id=None,
            )
            | Q(
                message_from=int(request.POST.get("r_id")),
                message_to=request.user.id,
                job__id=None,
            )
        )

    user = User.objects.filter(id=request.POST.get("r_id")).first()
    job = JobPost.objects.filter(id=request.POST.get("job_id")).first()
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
    if user:
        messages = render_to_string(
            "candidate/messages.html",
            {
                "messages": messages,
                "user": user,
                "job": job,
                "user_pic": user_pic,
                "profile_pic": profile_pic,
            },
            request,
        )
        data = {"error": False, "messages": messages}
    else:
        data = {"error": True, "response": "User Not Found!"}
    return data


@jobseeker_login_required
def messages(request):
    """need to check user login or not"""
    if request.POST.get("mode") == "get_messages":
        data = get_messages(request)
        return HttpResponse(json.dumps(data))
    if request.POST.get("post_message"):

        msg = UserMessage.objects.create(
            message=request.POST.get("message"),
            message_from=request.user,
            message_to=User.objects.get(id=int(request.POST.get("message_to"))),
        )

        if request.POST.get("job_id"):
            msg.job = int(request.POST.get("job_id"))

        time = datetime.datetime.now().strftime("%b. %d, %Y, %l:%M %p")
        return HttpResponse(
            json.dumps(
                {
                    "error": False,
                    "message": request.POST.get("message"),
                    "job_post": request.POST.get("job_id"),
                    "msg_id": str(msg.id),
                    "time": time,
                }
            )
        )
    if request.POST.get("mode") == "delete_message":
        msg = UserMessage.objects.get(id=request.POST.get("id"))
        if msg.message_from == request.user or msg.message_to == request.user:
            msg.delete()
            data = {"error": False, "message": request.POST.get("message")}
        else:
            data = {"error": True, "message": "You cannot delete!"}
        return HttpResponse(json.dumps(data))
    if request.POST.get("mode") == "delete_chat":
        if request.POST.get("job"):
            UserMessage.objects.filter(
                message_from=request.user.id,
                message_to=int(request.POST.get("user")),
                job=int(request.POST.get("job")),
            ).delete()
            UserMessage.objects.filter(
                message_from=int(request.POST.get("user"), message_to=request.user.id),
                job=int(request.POST.get("job")),
            ).delete()

        else:
            UserMessage.objects.filter(
                message_from=request.user.id,
                message_to=int(request.POST.get("user")),
                job=None,
            ).delete()
            UserMessage.objects.filter(
                message_from=int(request.POST.get("user")),
                message_to=request.user.id,
                job=None,
            ).delete()

        return HttpResponse(
            json.dumps({"error": False, "message": request.POST.get("message")})
        )
    if request.user.is_authenticated:
        messages = UserMessage.objects.filter(message_to=request.user.id)

        job_ids = messages.values_list("job__id", flat=True).distinct()
        recruiter_ids = messages.values_list("message_from__id", flat=True).distinct()
        jobs = JobPost.objects.filter(id__in=job_ids)
        users = User.objects.filter(id__in=recruiter_ids)
        if jobs.exists():
            job_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(job_ids)])
            jobs = jobs.order_by(job_order)
        if users.exists():
            recruiter_order = Case(
                *[When(pk=pk, then=pos) for pos, pk in enumerate(recruiter_ids)]
            )
            users = users.order_by(recruiter_order)
        template = "candidate/user_messages.html"
        return render(request, template, {"recruiters": users, "jobs": jobs})
    else:
        return HttpResponseRedirect("/")
