from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import boto3
import requests
import os

from django.template import loader
from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.utils import timezone
from zoneinfo import ZoneInfo
from django.urls import reverse
from django.conf import settings
from peeldb.models import (
    User,
    Google,
    Facebook,
    UserEmail,
    GitHub,
    JobPost,
    AppliedJobs,
)
from mpcomp.facebook import GraphAPI, get_access_token_from_code

from urllib.parse import parse_qsl


def login_and_apply(request):
    """
    1. Check for jobpost id present in user session exists or not
    2. Checking for if user already applies to a job
    3. if user uploads a resume or profile completion percantage > 55 then user can applies to job
    4. Sending a notification to recruiter if user applies to job, also sending a resume if user uploads resume
    """
    job_post = JobPost.objects.filter(
        id=request.session["job_id"], status="Live"
    ).first()
    if job_post:
        if not AppliedJobs.objects.filter(user=request.user, job_post=job_post):
            if request.user.resume or request.user.profile_completion_percentage >= 50:
                AppliedJobs.objects.create(
                    user=request.user,
                    job_post=job_post,
                    status="Pending",
                    ip_address=request.META["REMOTE_ADDR"],
                    user_agent=request.META["HTTP_USER_AGENT"],
                )
                template_loader = loader.get_template("email/applicant_apply_job.html")
                context = {
                    "user": request.user,
                    "recruiter": job_post.user,
                    "job_post": job_post,
                }
                rendered = template_loader.render(context)
                msg = MIMEMultipart()
                msg["Subject"] = "Peeljobs - The best Job Portal"
                msg["From"] = settings.DEFAULT_FROM_EMAIL
                msg["To"] = job_post.user.email
                part = MIMEText(rendered, "html")
                msg.attach(part)
                if request.user.resume and os.path.exists(
                    str(request.user.email) + ".docx"
                ):
                    resume_part = MIMEApplication(
                        open(str(request.user.email) + ".docx", "rb").read()
                    )
                    resume_part.add_header(
                        "Content-Disposition",
                        "attachment",
                        filename=str(request.user.email) + ".docx",
                    )
                    msg.attach(resume_part)
                    os.remove(str(request.user.email) + ".docx")
                
                # Use boto3 SES client
                ses_client = boto3.client(
                    'ses',
                    region_name='eu-west-1',
                    aws_access_key_id=settings.AM_ACCESS_KEY,
                    aws_secret_access_key=settings.AM_PASS_KEY,
                )
                ses_client.send_raw_email(
                    Source=msg["From"],
                    Destinations=[msg["To"]],
                    RawMessage={'Data': msg.as_string()}
                )
                return job_post, "applied"
        return job_post, "apply"
    return False


def facebook_login(request):
    if "code" in request.GET:
        accesstoken = get_access_token_from_code(
            request.GET["code"],
            request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:facebook_login"),
            settings.FB_APP_ID,
            settings.FB_SECRET,
        )
        if "error" in accesstoken.keys() or not accesstoken.get("access_token"):
            return render(
                request,
                "404.html",
                {
                    "message": "Sorry, Your session has been expired",
                    "reason": "Please kindly try again login to update your profile",
                    "email": settings.DEFAULT_FROM_EMAIL,
                },
                status=404,
            )
        graph = GraphAPI(accesstoken["access_token"])
        accesstoken = graph.extend_access_token(settings.FB_APP_ID, settings.FB_SECRET)[
            "accesstoken"
        ]
        profile = graph.get_object(
            "me",
            fields="id, name, email",
        )
        email = profile.get("email", "")

        if "email" in profile.keys():
            email_matches = UserEmail.objects.filter(email__iexact=email).first()
            if email_matches:
                user = email_matches.user
                if user.is_recruiter or user.is_agency_recruiter:
                    user = authenticate(username=user.username)
                    login(request, user)
                    return HttpResponseRedirect(reverse("recruiter:index"))

                # Checking Email associated with the user but user is not connected to facebook
                if not user.is_fb_connected:
                    Facebook.objects.create(
                        user=user,
                        name=profile.get("name", ""),
                        email=profile.get("email", ""),
                    )
                    user.save()
                user = authenticate(username=user.email)
            else:
                user = User.objects.filter(
                    email__iexact=profile.get("email", "")
                ).first()
                if user:
                    user.first_name = profile.get("name", "")
                    user.profile_updated = timezone.now()
                    user.is_active = True
                    user.save()
                else:
                    user = User.objects.create(
                        username=profile.get("email", ""),
                        email=profile.get("email", ""),
                        first_name=profile.get("name", ""),
                        last_name=profile.get("name", ""),
                        user_type="JS",
                        profile_updated=timezone.now(),
                        is_active=True,
                        registered_from="Social",
                    )

                Facebook.objects.create(
                    user=user,
                    facebook_id=profile.get("id"),
                    name=profile.get("name", ""),
                    email=profile.get("email", ""),
                )
                UserEmail.objects.create(
                    user=user, email=profile.get("email"), is_primary=True
                )
                user = authenticate(username=user.username)
                user.last_login = datetime.now()
                user.is_bounce = False
                user.referer = request.session.get("referer", "")
                user.save()
                login(request, user)
                return HttpResponseRedirect("/social/user/update/")
        else:
            return render(
                request,
                "404.html",
                {
                    "message": "Sorry, We didnt find your email id through facebook",
                    "reason": "Please verify your email id in facebook and try again",
                    "email": settings.DEFAULT_FROM_EMAIL,
                },
                status=404,
            )

        login(request, user)
        if "design" in request.session.keys():
            if request.session.get("job_id"):
                post = JobPost.objects.filter(
                    id=request.session["job_id"], status="Live"
                )
                return HttpResponseRedirect(post[0].slug)
            return HttpResponseRedirect("/jobs/")
        # Apply job after login starts
        if request.session.get("job_id"):
            log_apply = login_and_apply(request)
            if log_apply:
                return HttpResponseRedirect(
                    log_apply[0].slug + "?job_apply=" + log_apply[1]
                )
        # Apply job after login ends
        if user.profile_completion_percentage < 50:
            return HttpResponseRedirect(reverse("my:profile"))
        return HttpResponseRedirect("/")
    elif "error" in request.GET:
        # TODO : llog the error and transfer to error page
        return HttpResponseRedirect("/jobs/")
    else:
        print(settings.FB_APP_ID)

        rty = (
            "https://graph.facebook.com/oauth/authorize?client_id="
            + settings.FB_APP_ID
            + "&redirect_uri="
            + request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:facebook_login")
            + "&scope=email"
        )
        return HttpResponseRedirect(rty)


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
                    "message": "Sorry, Your session has been expired",
                    "reason": "Please kindly try again to update your profile",
                    "email": settings.DEFAULT_FROM_EMAIL,
                },
                status=404,
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
                # Handle recruiter login properly instead of redirecting to registration
                google, created = Google.objects.get_or_create(
                    user=user,
                    defaults={
                        'google_url': link,
                        'verified_email': user_document.get("verified_email", ""),
                        'google_id': user_document.get("id", ""),
                        'family_name': user_document.get("family_name", ""),
                        'name': user_document.get("name", ""),
                        'given_name': user_document.get("given_name", ""),
                        'dob': dob,
                        'email': user_document.get("email", ""),
                        'gender': gender,
                        'picture': picture,
                    }
                )
                if not created:
                    # Update existing Google record
                    google.google_url = link
                    google.verified_email = user_document.get("verified_email", "")
                    google.google_id = user_document.get("id", "")
                    google.family_name = user_document.get("family_name", "")
                    google.name = user_document.get("name", "")
                    google.given_name = user_document.get("given_name", "")
                    google.dob = dob
                    google.email = user_document.get("email", "")
                    google.gender = gender
                    google.picture = picture
                    google.save()
                
                # Authenticate and login the recruiter
                user = authenticate(username=user.username)
                user.is_active = True
                user.save()
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                
                # Redirect to recruiter dashboard
                return HttpResponseRedirect(reverse("recruiter:index"))

            # Email associated with the user but Google is not connected
            if not user.is_gp_connected:
                Google.objects.create(
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
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        else:
            user = User.objects.filter(
                email__iexact=user_document.get("email", "")
            ).first()
            if user:
                user.first_name = user_document.get("given_name", "")
                user.last_name = user_document.get("family_name", "")
                user.photo = picture
                user.profile_pic = picture
                user.profile_updated = timezone.now()
                user.is_active = True
                user.save()
            else:
                user = User.objects.create(
                    username=user_document.get("email", ""),
                    email=user_document.get("email", ""),
                    first_name=user_document.get("given_name", ""),
                    last_name=user_document.get("family_name", ""),
                    photo=picture,
                    user_type="JS",
                    profile_updated=timezone.now(),
                    is_active=True,
                    registered_from="Social",
                )
            if user_document.get("gender"):
                user.gender = "M" if user_document.get("gender") == "male" else "F"
                user.save()

            Google.objects.create(
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

            UserEmail.objects.create(
                user=user, email=user_document.get("email", ""), is_primary=True
            )

            # login(request, user)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            user.is_bounce = False
            user.referer = request.session.get("referer", "")
            user.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            # gpinfo.delay(id_value,user_document,picture,gender,dob,link,"login")
            return HttpResponseRedirect("/social/user/update/")

        # user.last_login = datetime.now()
        user.save()
        # login(request, user)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        # gpinfo.delay(id_value,user_document,picture,gender,dob,link,"login")
        if request.session.get("job_event"):
            return HttpResponseRedirect(reverse("pjob:job_add_event"))
        # if request.is_mobile == "mobile":
        #     return HttpResponseRedirect("/jobs/")

        if request.session.get("job_id"):
            log_apply = login_and_apply(request)
            if log_apply:
                return HttpResponseRedirect(
                    log_apply[0].slug + "?job_apply=" + log_apply[1]
                )
        if user.profile_completion_percentage < 50:
            return HttpResponseRedirect(reverse("my:profile"))
        return HttpResponseRedirect("/")
    else:
        rty = (
            "https://accounts.google.com/o/oauth2/auth?client_id="
            + settings.GOOGLE_CLIENT_ID
            + "&response_type=code"
        )
        rty += (
            "&scope=https://www.googleapis.com/auth/userinfo.profile \
               https://www.googleapis.com/auth/userinfo.email&redirect_uri="
            + settings.GOOGLE_LOGIN_HOST
            + reverse("social:google_login")
            + "&state=1235dfghjkf123"
        )

        return HttpResponseRedirect(rty)


# TODO: need to think about this a lot because github will return lot of email ids including no-reply.github.com.
# we need to see if the other emails are not assiciated with any acocunts
# or else it will be a problem
def github_login(request):
    if "code" in request.GET:
        params = {
            "client_id": settings.GIT_APP_ID,
            "redirect_uri": request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:github_login"),
            "client_secret": settings.GIT_APP_SECRET,
            "code": request.GET.get("code"),
        }
        info = requests.post("https://github.com/login/oauth/access_token", data=params)
        ac = dict(parse_qsl(info.text))
        if not ac.get("access_token"):
            return render(
                request,
                "404.html",
                {
                    "message": "Sorry, Your session has been expired",
                    "reason": "Please kindly try again to update your profile",
                    "email": settings.DEFAULT_FROM_EMAIL,
                },
                status=404,
            )
        params = {"access_token": ac["access_token"]}
        headers = {
            "X-GitHub-Media-Type": "application/vnd.github.v3",
            "Authorization": "token %s" % ac["access_token"],
        }
        kw = dict(params=params, headers=headers, timeout=60)
        info = requests.request("GET", "https://api.github.com/user", **kw)
        details = info.json()
        params = {"access_token": ac["access_token"]}
        headers = {
            "X-GitHub-Media-Type": "application/vnd.github.v3",
            "Authorization": "token %s" % ac["access_token"],
        }
        kw = dict(params=params, headers=headers, timeout=60)
        response = requests.request("GET", "https://api.github.com/user/emails", **kw)
        picture = details["avatar_url"] if "avatar_url" in details.keys() else ""

        emails = []
        for x in response.json():
            emails.append(str(x["email"]))

        # loop through the emails we got from github
        for email in emails:
            email_matches = UserEmail.objects.filter(email__iexact=email)

            hireable = False
            if "hireable" in details.keys() and details["hireable"]:
                hireable = details["hireable"]
            company = ""
            if "company" in details.keys() and details["company"]:
                company = details["company"]
            name = ""
            if "login" in details.keys() and details["login"]:
                name = details["login"]
            # if there is an user associated with the email
            if email_matches:
                user = email_matches[0].user
                # if the user is not having github record
                if not user.is_gh_connected:
                    GitHub.objects.create(
                        user=user,
                        git_url=details.get("html_url", ""),
                        git_id=details.get("id", ""),
                        disk_usage=details.get("disk_usage", ""),
                        private_gists=details.get("private_gists", ""),
                        public_gists=details.get("public_gists", ""),
                        public_repos=details.get("public_repos", ""),
                        hireable=hireable,
                        total_private_repos=details.get("total_private_repos", ""),
                        owned_private_repos=details.get("owned_private_repos", ""),
                        following=details.get("following", ""),
                        followers=details.get("followers", ""),
                        company=company,
                        name=name,
                        user_from=details.get("created_at", ""),
                    )
                    for email in emails:
                        if not UserEmail.objects.filter(
                            user=user, email=email
                        ).exists():
                            UserEmail.objects.create(user=user, email=email)
                user = authenticate(username=user.username)
                break
            else:
                user = User.objects.filter(email__iexact=emails[0]).first()
                if user:
                    user.photo = picture
                    user.profile_pic = picture
                    user.profile_updated = timezone.now()
                    user.is_active = True
                    user.save()
                else:
                    user = User.objects.create(
                        username=emails[0],
                        email=emails[0],
                        user_type="JS",
                        photo=picture,
                        profile_updated=timezone.now(),
                        is_active=True,
                        registered_from="Social",
                    )

                GitHub.objects.create(
                    user=user,
                    git_url=details.get("html_url", ""),
                    git_id=details.get("id", ""),
                    disk_usage=details.get("disk_usage", ""),
                    private_gists=details.get("private_gists", ""),
                    public_gists=details.get("public_gists", ""),
                    public_repos=details.get("public_repos", ""),
                    hireable=hireable,
                    total_private_repos=details.get("total_private_repos", ""),
                    owned_private_repos=details.get("owned_private_repos", ""),
                    following=details.get("following", ""),
                    followers=details.get("followers", ""),
                    company=company,
                    name=name,
                    user_from=details.get("created_at", ""),
                )

                for email in emails:
                    if not UserEmail.objects.filter(user=user, email=email).exists():
                        UserEmail.objects.create(user=user, email=email)

                user = authenticate(username=user.username)
                user.last_login = datetime.now()
                user.save()
                login(request, user)
                return HttpResponseRedirect("/social/user/update/")

        user.last_login = datetime.now()
        user.referer = request.session.get("referer", "")
        user.save()

        login(request, user)

        # if request.is_mobile == "mobile":
        #     return HttpResponseRedirect("/jobs/")

        if request.session.get("job_id"):
            log_apply = login_and_apply(request)
            if log_apply:
                return HttpResponseRedirect(
                    log_apply[0].slug + "?job_apply=" + log_apply[1]
                )
        if user.profile_completion_percentage < 50:
            return HttpResponseRedirect(reverse("my:profile"))
        return HttpResponseRedirect("/")
    else:
        rty = (
            "https://github.com/login/oauth/authorize?client_id=" + settings.GIT_APP_ID
        )
        rty += (
            "&redirect_uri="
            + request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:github_login")
            + "&scope=read:user user:email&state=dia123456789ramya"
        )
        return HttpResponseRedirect(rty)

