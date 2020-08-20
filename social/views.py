"""
    social logins module which includes facebook, google, twitter, linkedin, github, stackoverflow connections
    Also applying jobs when user clicks on apply button in jobs list page
"""

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import json
import urllib
import boto
import requests
import os

from django.template import loader
from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.template.defaultfilters import slugify
from peeldb.models import (
    User,
    Google,
    Facebook,
    UserEmail,
    GitHub,
    Linkedin,
    Twitter,
    JobPost,
    StackOverFlow,
    AppliedJobs,
    City,
    State,
    Industry,
    EmploymentHistory,
)
from mpcomp.facebook import GraphAPI, get_access_token_from_code

from twython.api import Twython
from urllib.parse import parse_qsl
from .tasks import (
    facebook_groups,
    facebook_friends,
    facebook_pages,
    add_google_friends,
    add_twitter_friends_followers,
)


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
                conn = boto.ses.connect_to_region(
                    "eu-west-1",
                    aws_access_key_id=settings.AM_ACCESS_KEY,
                    aws_secret_access_key=settings.AM_PASS_KEY,
                )
                conn.send_raw_email(
                    msg.as_string(), source=msg["From"], destinations=[msg["To"]]
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
                    "number": settings.CONTACT_NUMBER,
                },
                status=404,
            )
        graph = GraphAPI(accesstoken["access_token"])
        accesstoken = graph.extend_access_token(settings.FB_APP_ID, settings.FB_SECRET)[
            "accesstoken"
        ]
        profile = graph.get_object(
            "me",
            fields="id, name, email, birthday, hometown, location, link, locale, gender, timezone",
        )
        email = profile.get("email", "")
        hometown = profile["hometown"]["name"] if "hometown" in profile.keys() else ""
        location = profile["location"]["name"] if "location" in profile.keys() else ""
        bday = (
            datetime.strptime(profile["birthday"], "%m/%d/%Y").strftime("%Y-%m-%d")
            if profile.get("birthday")
            else "1970-09-09"
        )
        profile_pic = (
            "https://graph.facebook.com/" + profile["id"] + "/picture?type=large"
        )
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
                        facebook_url=profile.get("link", ""),
                        facebook_id=profile.get("id"),
                        first_name=profile.get("first_name", ""),
                        last_name=profile.get("last_name", ""),
                        verified=profile.get("verified", ""),
                        name=profile.get("name", ""),
                        language=profile["locale"] if profile.get("locale") else "",
                        hometown=hometown,
                        email=profile.get("email", ""),
                        gender=profile.get("gender", ""),
                        dob=bday,
                        location=location,
                        timezone=profile.get("timezone", ""),
                        accesstoken=accesstoken,
                    )
                    user.photo = profile_pic
                    user.save()
                user = authenticate(username=user.email)
            else:
                user = User.objects.filter(
                    email__iexact=profile.get("email", "")
                ).first()
                if user:
                    user.first_name = profile.get("name", "")
                    user.last_name = profile.get("last_name", "")
                    user.photo = profile_pic
                    user.profile_pic = profile_pic
                    user.profile_updated = datetime.now(timezone.utc)
                    user.is_active = True
                    user.save()
                else:
                    user = User.objects.create(
                        username=profile.get("email", ""),
                        email=profile.get("email", ""),
                        profile_pic=profile_pic,
                        photo=profile_pic,
                        first_name=profile.get("first_name", ""),
                        last_name=profile.get("last_name", ""),
                        user_type="JS",
                        profile_updated=datetime.now(timezone.utc),
                        is_active=True,
                        registered_from="Social",
                    )
                if profile.get("gender"):
                    user.gender = profile.get("gender")
                if profile.get("location"):
                    city = City.objects.filter(name__iexact=location.strip())
                    if city:
                        user.current_city = city[0]
                    else:
                        city = City.objects.create(
                            name=location,
                            status="Disabled",
                            slug=slugify(location),
                            state=State.objects.get(id=16),
                        )
                        user.current_city = city

                Facebook.objects.create(
                    user=user,
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
                UserEmail.objects.create(
                    user=user, email=profile.get("email"), is_primary=True
                )
                user = authenticate(username=user.username)
                user.last_login = datetime.now()
                user.is_bounce = False
                user.referer = request.session.get("referer", "")
                user.save()
                login(request, user)
                facebook_pages.delay(accesstoken, user.id)
                facebook_friends.delay(accesstoken, user.id)
                facebook_groups.delay(accesstoken, user.id)
                return HttpResponseRedirect("/social/user/update/")
        else:
            return render(
                request,
                "404.html",
                {
                    "message": "Sorry, We didnt find your email id through facebook",
                    "reason": "Please verify your email id in facebook and try again",
                    "email": settings.DEFAULT_FROM_EMAIL,
                    "number": settings.CONTACT_NUMBER,
                },
                status=404,
            )

        login(request, user)
        facebook_pages.delay(accesstoken, user.id)
        facebook_friends.delay(accesstoken, user.id)
        facebook_groups.delay(accesstoken, user.id)
        if "design" in request.session.keys() and request.is_mobile == "mobile":
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
            + reverse("social:facebook_login")
            + "&scope=manage_pages, user_birthday, user_location, user_hometown"
            + ", email, user_likes"
        )
        return HttpResponseRedirect(rty)


def google_login(request):
    if "code" in request.GET:
        params = {
            "grant_type": "authorization_code",
            "code": request.GET.get("code"),
            "redirect_uri": request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:google_login"),
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
                    "message": "Sorry, Your session has been expired",
                    "reason": "Please kindly try again to update your profile",
                    "email": settings.DEFAULT_FROM_EMAIL,
                    "number": settings.CONTACT_NUMBER,
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
                user = authenticate(username=user.username)
                login(request, user)
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
                user.profile_updated = datetime.now(timezone.utc)
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
                    profile_updated=datetime.now(timezone.utc),
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
            login(request, user)
            # gpinfo.delay(id_value,user_document,picture,gender,dob,link,"login")
            add_google_friends.delay(request.user.id, info["access_token"])
            return HttpResponseRedirect("/social/user/update/")

        # user.last_login = datetime.now()
        user.save()
        # login(request, user)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        # gpinfo.delay(id_value,user_document,picture,gender,dob,link,"login")
        add_google_friends.delay(request.user.id, info["access_token"])
        if request.session.get("job_event"):
            return HttpResponseRedirect(reverse("pjob:job_add_event"))
        if request.is_mobile == "mobile":
            return HttpResponseRedirect("/jobs/")

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
            + settings.GP_CLIENT_ID
            + "&response_type=code"
        )
        rty += (
            "&scope=https://www.googleapis.com/auth/userinfo.profile"
            + " https://www.googleapis.com/auth/userinfo.email"
            + " https://www.googleapis.com/auth/contacts.readonly&redirect_uri="
            + request.scheme
            + "://"
            + request.META["HTTP_HOST"]
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
            "grant_type": "authorization_code",
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
                    "number": settings.CONTACT_NUMBER,
                },
                status=404,
            )
        params = {"access_token": ac["access_token"]}
        kw = dict(params=params)
        info = requests.request("GET", "https://api.github.com/user", **kw)
        details = info.json()
        params = {"access_token": ac["access_token"]}
        headers = {"X-GitHub-Media-Type": "application/vnd.github.v3"}
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
                    user.profile_updated = datetime.now(timezone.utc)
                    user.is_active = True
                    user.save()
                else:
                    user = User.objects.create(
                        username=emails[0],
                        email=emails[0],
                        user_type="JS",
                        photo=picture,
                        profile_updated=datetime.now(timezone.utc),
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

        if request.is_mobile == "mobile":
            return HttpResponseRedirect("/jobs/")

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
            + "&scope=user,user:email&state=dia123456789ramya"
        )
        return HttpResponseRedirect(rty)


# def linkedin(request):
#     rty = "https://www.linkedin.com/uas/oauth2/authorization?response_type=code&client_id="+LN_API_KEY
#     rty += "&scope=r_fullprofile r_emailaddress r_network r_contactinfo w_messages rw_nus rw_groups&state=fdgyt5hj4fg54jhlt8a"
#     rty += "&redirect_uri="+LN_REDIRECT_URI
#     return HttpResponseRedirect(rty)


def linkedin_login(request):
    if "code" in request.GET:
        params = {}
        params["grant_type"] = "authorization_code"
        params["code"] = request.GET.get("code")
        params["redirect_uri"] = (
            request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:linkedin_login")
        )
        params["client_id"] = settings.LN_API_KEY
        params["client_secret"] = settings.LN_SECRET_KEY
        from urllib.request import urlopen

        args = {
            "grant_type": "authorization_code",
            "code": request.GET.get("code"),
            "redirect_uri": request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:linkedin_login"),
            "client_id": settings.LN_API_KEY,
            "client_secret": settings.LN_SECRET_KEY,
        }
        response = requests.get(
            "https://www.linkedin.com/uas/oauth2/accessToken?"
            + urllib.parse.urlencode(args)
        ).json()
        if not response.get("access_token"):
            return render(
                request,
                "404.html",
                {
                    "message": "Sorry, Your session has been expired",
                    "reason": "Please kindly try again to update your profile",
                },
                status=404,
            )
        accesstoken = response["access_token"]
        required_info = "id,first-name,last-name,email-address,location,positions,educations,industry,summary,public-profile-url,picture-urls::(original)"
        rty = (
            "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))&oauth2_access_token="
            + accesstoken
        )

        details = urlopen(rty).read().decode("utf-8")
        details = json.loads(details)
        email_address = details["elements"][0]["handle~"]["emailAddress"]

        profile_rty = (
            "https://api.linkedin.com/v2/me?oauth2_access_token=" + accesstoken
        )
        profile_rty = urlopen(profile_rty).read().decode("utf-8")
        profile_rty = json.loads(profile_rty)

        if not email_address:
            return render(
                request,
                "404.html",
                {
                    "message": "Sorry, Your session has been expired",
                    "reason": "Please kindly try again to update your profile",
                },
                status=404,
            )
        email_matches = UserEmail.objects.filter(email__iexact=email_address)
        employment = details.get("positions")
        if "positions" in details.keys():
            if details["positions"]["_total"] == 0:
                positions = 0
            else:
                positions = details["positions"]["values"]
        else:
            positions = 0
        profile_pic = ""
        if "pictureUrls" in details:
            pictureurl = details["pictureUrls"]
            if pictureurl["_total"] != 0:
                for i in pictureurl["values"]:
                    profile_pic = i
        if email_matches:
            user = email_matches[0].user
            if user.is_recruiter or user.is_agency_recruiter:
                login(request, user)
                return HttpResponseRedirect(reverse("recruiter:index"))
            # Email associated with the user but Linkedin is not connected
            if not user.is_ln_connected:
                # TODO need to add education, industry details of user
                Linkedin.objects.create(
                    user=user,
                    linkedin_id=profile_rty.get("id", ""),
                    linkedin_url=details.get("publicProfileUrl", ""),
                    first_name=profile_rty["firstName"]["localized"]["en_US"],
                    last_name=profile_rty["lastName"]["localized"]["en_US"],
                    location=details["location"]["name"],
                    workhistory=positions,
                    email=email_address,
                    accesstoken=accesstoken,
                )
            user = authenticate(username=user.username)
        else:
            user = User.objects.filter(email__iexact=email_address).first()
            if user:
                user.first_name = details.get("firstName", "")
                user.last_name = details.get("lastName", "")
                user.photo = profile_pic
                user.profile_updated = datetime.now(timezone.utc)
                user.is_active = True
                user.save()
            else:
                user = User.objects.create(
                    username=email_address,
                    email=email_address,
                    first_name=details.get("firstName", ""),
                    last_name=details.get("lastName", ""),
                    photo=profile_pic,
                    user_type="JS",
                    profile_updated=datetime.now(timezone.utc),
                    is_active=True,
                    registered_from="Social",
                )
            if details.get("summery"):
                user.profile_description = details.get("summery")
            if employment and details["positions"]["_total"] != 0:
                for i in employment["values"]:
                    if i.get("company"):
                        exp = EmploymentHistory.objects.create(
                            company=i["company"].get("name", ""),
                            designation=i["title"],
                            current_job=i["isCurrent"],
                        )
                        if i.get("startDate"):
                            fromd = (
                                str(i["startDate"]["year"])
                                + "-"
                                + str(i["startDate"]["month"])
                                + "-01"
                            )
                            exp.from_date = fromd
                            exp.save()
                        user.employment_history.add(exp)
            if details.get("industry"):
                industry = Industry.objects.filter(name__iexact=details.get("industry"))
                if industry:
                    user.industry.add(industry[0])
                else:
                    industry = Industry.objects.create(
                        name=details.get("industry"),
                        status="InActive",
                        slug=slugify(details.get("industry")),
                    )
                    user.industry.add(industry)
            user.save()
            Linkedin.objects.create(
                user=user,
                linkedin_id=details.get("id", ""),
                linkedin_url=details.get("publicProfileUrl", ""),
                first_name=details.get("firstName", ""),
                last_name=details.get("lastName", ""),
                # location=details['location']['name'],
                workhistory=positions,
                email=details.get("emailAddress", ""),
                accesstoken=accesstoken,
            )

            UserEmail.objects.create(
                user=user, email=details.get("emailAddress", ""), is_primary=True
            )

            login(request, user)
            user.is_bounce = False
            user.last_login = datetime.now()
            user.referer = request.session.get("referer", "")
            user.save()
            login(request, user)
            return HttpResponseRedirect("/social/user/update/")

        user.is_bounce = False

        user.last_login = datetime.now()
        user.save()

        login(request, user)

        # TODO need to store User groups and frnds in the database

        # lninfo(id_value,details,location,edu,positions,industry,accesstoken,pictureurl,"login")
        # lngroups(id_value,details['id'],accesstoken)
        # lnfrnds(id_value,details['id'],accesstoken)

        if request.is_mobile == "mobile":
            return HttpResponseRedirect("/jobs/")

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
            "https://www.linkedin.com/uas/oauth2/authorization?response_type=code&client_id="
            + settings.LN_API_KEY
        )
        rty += (
            "&scope=r_liteprofile r_emailaddress w_member_social&state=8897239179ramya"
        )
        rty += (
            "&redirect_uri="
            + request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:linkedin_login")
        )
        return HttpResponseRedirect(rty)


@login_required
def twitter_login(request):

    if "oauth_verifier" in request.GET:
        oauth_verifier = request.GET["oauth_verifier"]
        twitter = Twython(
            settings.PJ_TW_APP_KEY,
            settings.PJ_TW_APP_SECRET,
            request.session["OAUTH_TOKEN"],
            request.session["OAUTH_TOKEN_SECRET"],
        )
        final_step = twitter.get_authorized_tokens(oauth_verifier)
        if not final_step.get("oauth_token_secret"):
            return render(
                request,
                "404.html",
                {
                    "message": "Sorry, Your session has been expired",
                    "reason": "Please kindly try again to update your profile",
                    "email": settings.DEFAULT_FROM_EMAIL,
                    "number": settings.CONTACT_NUMBER,
                },
                status=404,
            )
        twitter = Twython(
            settings.PJ_TW_APP_KEY,
            settings.PJ_TW_APP_SECRET,
            final_step["oauth_token"],
            final_step["oauth_token_secret"],
        )
        followers = twitter.get_followers_list(screen_name=final_step["screen_name"])
        friends = twitter.get_friends_list(screen_name=final_step["screen_name"])

        if not request.user.is_tw_connected and request.user.is_authenticated:
            Twitter.objects.create(
                user=request.user,
                twitter_id=final_step.get("user_id", ""),
                screen_name=final_step.get("screen_name", ""),
                oauth_token=final_step.get("oauth_token", ""),
                oauth_secret=final_step.get("oauth_token_secret", ""),
            )

        add_twitter_friends_followers.delay(request.user.id, friends, followers)

        if request.is_mobile == "mobile":
            return HttpResponseRedirect("/jobs/")
        if request.session.get("job_id"):
            log_apply = login_and_apply(request)
            if log_apply:
                return HttpResponseRedirect(
                    log_apply[0].slug + "?job_apply=" + log_apply[1]
                )
        return HttpResponseRedirect(reverse("my:profile"))
    else:
        twitter = Twython(settings.PJ_TW_APP_KEY, settings.PJ_TW_APP_SECRET)
        url = (
            request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:twitter_login")
        )
        auth = twitter.get_authentication_tokens(callback_url=url)
        request.session["OAUTH_TOKEN"] = auth["oauth_token"]
        request.session["OAUTH_TOKEN_SECRET"] = auth["oauth_token_secret"]
        return HttpResponseRedirect(auth["auth_url"])


@login_required
def facebook_connect(request):
    if "code" in request.GET:
        accesstoken = get_access_token_from_code(
            request.GET["code"],
            request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:facebook_connect"),
            settings.FB_APP_ID,
            settings.FB_SECRET,
        )
        if "error" in accesstoken.keys():
            message = "Sorry, Your session has been expired"
            reason = "Please kindly try again login to update your profile"
            return render(
                request, "404.html", {"message": message, "reason": reason}, status=404
            )
        graph = GraphAPI(accesstoken["access_token"])
        accesstoken = graph.extend_access_token(settings.FB_APP_ID, settings.FB_SECRET)[
            "accesstoken"
        ]

        profile = graph.get_object(
            "me",
            fields="id, name, email, birthday, hometown, location, link, locale, gender, timezone",
        )
        # email = profile['email'] if 'email' in profile.keys() else ''
        if "email" not in profile.keys():
            message = "Sorry, We didnt find your email id through facebook"
            reason = "Please verify your email id in facebook and try again"
            return render(
                request, "404.html", {"message": message, "reason": reason}, status=404
            )

        hometown = profile["hometown"]["name"] if profile.get("hometown") else ""
        location = profile["location"]["name"] if profile.get("location") else ""
        bday = (
            datetime.strptime(profile["birthday"], "%m/%d/%Y").strftime("%Y-%m-%d")
            if "birthday" in profile.keys()
            else None
        )
        if request.user.is_authenticated:
            Facebook.objects.create(
                user=request.user,
                facebook_url=profile.get("link", ""),
                facebook_id=profile.get("id", ""),
                first_name=profile.get("first_name", ""),
                last_name=profile.get("last_name", ""),
                verified=profile.get("verified", ""),
                name=profile.get("name", ""),
                language=profile.get("locale", ""),
                hometown=hometown,
                email=profile["email"],
                gender=profile.get("gender", ""),
                dob=bday,
                location=location,
                timezone=profile.get("timezone", ""),
                accesstoken=accesstoken,
            )
            email_matches = UserEmail.objects.filter(
                user=request.user, email=profile["email"]
            )
            if not email_matches:
                UserEmail.objects.create(user=request.user, email=profile["email"])

        facebook_pages.delay(accesstoken, request.user.id)
        facebook_friends.delay(accesstoken, request.user.id)
        facebook_groups.delay(accesstoken, request.user.id)

        return HttpResponseRedirect(reverse("my:profile"))

    elif "error" in request.GET:
        return HttpResponseRedirect(reverse("my:profile"))
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
            + reverse("social:facebook_connect")
            + "&scope="
        )
        return HttpResponseRedirect(rty)


@login_required
def google_connect(request):
    if "code" in request.GET:
        params = {
            "grant_type": "authorization_code",
            "code": request.GET.get("code"),
            "redirect_uri": request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:google_connect"),
            "client_id": settings.GP_CLIENT_ID,
            "client_secret": settings.GP_CLIENT_SECRET,
        }

        info = requests.post("https://accounts.google.com/o/oauth2/token", data=params)
        info = info.json()

        url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {"access_token": info["access_token"]}
        kw = dict(params=params, headers={}, timeout=60)
        response = requests.request("GET", url, **kw)
        user_document = response.json()

        link = "https://plus.google.com/" + user_document["id"]
        picture = user_document["picture"] if "picture" in user_document.keys() else ""
        dob = user_document["birthday"] if "birthday" in user_document.keys() else ""
        gender = user_document["gender"] if "gender" in user_document.keys() else ""
        link = user_document["link"] if "link" in user_document.keys() else link

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
        email_matches = UserEmail.objects.filter(
            user=request.user, email=user_document["email"]
        )
        if not email_matches:
            UserEmail.objects.create(user=request.user, email=user_document["email"])

        # gpinfo.delay(id_value,user_document,picture,gender,dob,link,"login")
        add_google_friends.delay(request.user.id, info["access_token"])
        return HttpResponseRedirect(reverse("my:profile"))
    else:
        rty = (
            "https://accounts.google.com/o/oauth2/auth?client_id="
            + settings.GP_CLIENT_ID
            + "&response_type=code"
        )
        rty += (
            "&scope=https://www.googleapis.com/auth/userinfo.profile"
            + " https://www.googleapis.com/auth/userinfo.email"
            + " https://www.googleapis.com/auth/contacts.readonly&redirect_uri="
            + request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:google_connect")
            + "&state=1235dfghjkf123"
        )
        return HttpResponseRedirect(rty)


@login_required
def linkedin_connect(request):
    if "code" in request.GET:
        params = {}
        params["grant_type"] = "authorization_code"
        params["code"] = request.GET.get("code")
        params["redirect_uri"] = (
            request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:linkedin_connect")
        )
        params["client_id"] = settings.LN_API_KEY
        params["client_secret"] = settings.LN_SECRET_KEY
        # params = urllib.urlencode(params)
        # params = params.encode('utf-8')
        # import urllib.request as ur
        # info = ur.urlopen("https://www.linkedin.com/uas/oauth2/accessToken", params)
        params = urllib.parse.urlencode(params)
        params = params.encode("utf-8")
        import urllib.request as ur

        info = ur.urlopen("https://www.linkedin.com/uas/oauth2/accessToken", params)
        accesstoken = json.loads(info.readline().decode("utf8"))["access_token"]

        rty = "https://api.linkedin.com/v2/me:"
        rty += "(id,first-name,last-name,email-address,location,positions,educations,industry,public-profile-url,picture-urls::(original))"
        rty += "?format=json&oauth2_access_token=" + accesstoken
        details = ur.urlopen(rty).read().decode("utf8")
        details = json.loads(details)
        email_matches = UserEmail.objects.filter(email__iexact=details["emailAddress"])

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
        if request.user.is_authenticated:
            # TODO need to add education, industry details of user
            Linkedin.objects.create(
                user=request.user,
                linkedin_id=details.get("id", ""),
                linkedin_url=details.get("publicProfileUrl", ""),
                first_name=details.get("firstName", ""),
                last_name=details.get("lastName", ""),
                location=details["location"]["name"],
                workhistory=positions,
                email=details.get("emailAddress", ""),
                accesstoken=accesstoken,
            )

        email_matches = UserEmail.objects.filter(
            user=request.user, email=details.get("emailAddress", "")
        )
        if not email_matches:
            UserEmail.objects.create(
                user=request.user, email=details.get("emailAddress", "")
            )

        # TODO need to store User groups and frnds in the database

        # lninfo(id_value,details,location,edu,positions,industry,accesstoken,pictureurl,"login")
        # lngroups(id_value,details['id'],accesstoken)
        # lnfrnds(id_value,details['id'],accesstoken)

        return HttpResponseRedirect(reverse("my:profile"))
    else:
        rty = (
            "https://www.linkedin.com/uas/oauth2/authorization?response_type=code&client_id="
            + settings.LN_API_KEY
        )
        rty += "&scope=r_liteprofile r_emailaddress rw_company_admin w_member_social&state=8897239179ramya"
        rty += (
            "&redirect_uri="
            + request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:linkedin_connect")
        )
        return HttpResponseRedirect(rty)


def sofconnect(request):

    if "code" in request.GET:
        print(
            request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:sofconnect")
        )
        params = {}
        params["code"] = request.GET.get("code")
        params["redirect_uri"] = (
            request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:sofconnect")
        )
        params["client_id"] = settings.SOF_APP_ID
        params["client_secret"] = settings.SOF_APP_SECRET
        params["scope"] = "no_expiry"
        info = requests.post(
            "https://stackexchange.com/oauth/access_token", data=params
        )
        access_token = dict(parse_qsl(info.text))["access_token"]
        url = "https://api.stackexchange.com/2.1/me"
        params = {
            "site": "stackoverflow",
            "access_token": access_token,
            "key": settings.SOF_APP_KEY,
            "format": "json",
        }
        headers = {}
        kw = dict(params=params, headers=headers)
        # jsonurl=urllib.urlopen('https://api.stackexchange.com/2.1/me',params={'site': 'stackoverflow','access_token': access_token,'key':SOF_APP_KEY})
        # text = json.loads(jsonurl.read())
        # print text['items'][0]
        response = requests.request("GET", url, **kw)
        response = response.json()
        profile_image = stack_user_id = account_id = display_name = link = ""
        if "items" in response.keys():
            if response["items"]:
                userinfo = response["items"][0]
                profile_image = userinfo.get("profile_image", "")
                stack_user_id = userinfo.get("stack_user_id", "")
                account_id = userinfo.get("account_id", "")
                display_name = userinfo.get("display_name", "")
                link = userinfo.get("link", "")
        StackOverFlow.objects.create(
            user=request.user,
            profile_image=profile_image,
            display_name=display_name,
            link=link,
            account_id=account_id,
            stack_user_id=stack_user_id,
        )
        return HttpResponseRedirect(reverse("my:profile"))
    else:
        rty = (
            "https://stackexchange.com/oauth?client_id="
            + settings.SOF_APP_ID
            + "&scope=no_expiry,write_access,read_inbox,private_info"
        )
        rty += (
            "&redirect_uri="
            + request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + reverse("social:sofconnect")
        )
        return HttpResponseRedirect(rty)


def fbinfo(accesstoken, profile, hometown, bday, location, user):
    facebook = Facebook.objects.create(
        facebook_url=profile["link"],
        facebook_id=profile["id"],
        first_name=profile["first_name"],
        last_name=profile["last_name"],
        verified=profile["verified"],
        name=profile["name"],
        language=profile["locale"],
        hometown=hometown,
        email=profile["email"],
        gender=profile["gender"],
        dob=bday,
        location=location,
        timezone=profile["timezone"],
        accesstoken=accesstoken,
    )
    user.facebook = facebook
    user.save()
