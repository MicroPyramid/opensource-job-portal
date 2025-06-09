"""
Authentication Views
Handles user authentication, registration, and account management
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
from recruiter.views.dashboard import get_autocomplete

# Authentication Views will be moved here
# TODO: Move the following functions from the main views.py:
# - index()
# - new_user()
# - account_activation()
# - user_password_reset()
# - change_password()
# - verify_mobile()
# - send_mobile_verification_code()
# - google_login()
# - google_connect()
# - facebook_login()


def index(request):
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
                mto = [request.POST.get("email")]
                subject = "PeelJobs Recruiter Account Activation"
                send_email.delay(mto, subject, rendered)
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
    meta = MetaData.objects.filter(name="post_job")
    if meta:
        meta_title = Template(meta[0].meta_title).render(Context({}))
        meta_description = Template(meta[0].meta_description).render(Context({}))
        h1_tag = Template(meta[0].h1_tag).render(Context({}))
    return render(
        request,
        "recruiter/login.html",
        {
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
        },
    )




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
            meta = MetaData.objects.filter(name="recruiter_login")
            if meta:
                meta_title = Template(meta[0].meta_title).render(Context({}))
                meta_description = Template(meta[0].meta_description).render(
                    Context({})
                )
                h1_tag = Template(meta[0].h1_tag).render(Context({}))
            return render(
                request,
                "recruiter/register.html",
                {
                    "meta_title": meta_title,
                    "meta_description": meta_description,
                    "h1_tag": h1_tag,
                    "RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY,
                },
            )

    if request.method == "POST":

        # check recaptcha v3 score
        recaptcha_secret_key = settings.RECAPTCHA_SECRET_KEY
        recaptcha_response = request.POST.get("g-recaptcha-response")
        recaptcha_url = "https://www.google.com/recaptcha/api/siteverify"
        recaptcha_data = {
            "secret": recaptcha_secret_key,
            "response": recaptcha_response,
            "remoteip": request.META.get("REMOTE_ADDR"),
        }
        recaptcha_response = requests.post(
            recaptcha_url, data=recaptcha_data
        )
        recaptcha_result = recaptcha_response.json()
        if recaptcha_result.get('score', 0) < 0.6:
            data = {"error": True, "captcha_response": "Choose Correct Captcha"}
            return HttpResponse(json.dumps(data))

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
            
                
            if 1:
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
                    mto = request.POST.get("email")
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
                    send_email.delay(mto, subject, rendered)

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
                send_email.delay(mto, subject, rendered)

                usr.last_password_reset_on = datetime.now(timezone.utc)
                usr.save()

                data = {
                    "error": False,
                    "info": (
                        "Sent a link to your email to reset your password"
                        if usr.is_active
                        else "An email has been sent to your email id, Please activate your account"
                    ),
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
        user.mobile_verification_code = random_code
        user.last_mobile_code_verified_on = datetime.now(timezone.utc)
        user.save()
        return HttpResponse(
            json.dumps(
                {"error": False, "message": "An OTP sent to your mobile successfully"}
            )
        )




def google_login(request):
    if "code" in request.GET:
        params = {
            "grant_type": "authorization_code",
            "code": request.GET.get("code"),
            "redirect_uri": settings.GOOGLE_LOGIN_HOST + reverse("social:google_login"),
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
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
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
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
            + settings.GOOGLE_CLIENT_ID
            + "&response_type=code&scope="
        )
        rty += (
            "https://www.googleapis.com/auth/userinfo.profile"
            + " https://www.googleapis.com/auth/userinfo.email"
        )
        rty += (
            "&redirect_uri="
            + settings.GOOGLE_LOGIN_HOST
            + reverse("social:google_login")
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
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
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

            return HttpResponseRedirect(reverse("recruiter:index"))
        message_type = "Sorry,"
        message = "We didnt find your Account"
        reason = "Please verify your details and try again"
        email = settings.DEFAULT_FROM_EMAIL
        return render(
            request,
            "recruiter/recruiter_404.html",
            {
                "message_type": message_type,
                "message": message,
                "reason": reason,
                "email": email,
            },
            status=404,
        )
    else:
        rty = (
            "https://accounts.google.com/o/oauth2/auth?client_id="
            + settings.GOOGLE_CLIENT_ID
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
                
                return HttpResponseRedirect(reverse("recruiter:index"))
        message_type = "Sorry,"
        message = "We didnt find your email id through facebook"
        reason = "Please verify your email id in facebook and try again"
        email = settings.DEFAULT_FROM_EMAIL
        return render(
            request,
            "recruiter/recruiter_404.html",
            {
                "message_type": message_type,
                "message": message,
                "reason": reason,
                "email": email,
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
