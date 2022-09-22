import json
import math
import urllib
from datetime import datetime, timedelta
from functools import reduce
from itertools import chain
from operator import __or__ as OR

import requests
from django.conf import settings
from django.core.mail import EmailMessage
# from pytz import timezone
from django.db.models import Case, Q, When
from django.template import loader
# from jobsp.celery import app
from jobsp.celery import app
from microurl import google_mini
from mpcomp.facebook import GraphAPI, get_app_access_token
from mpcomp.views import get_absolute_url
from peeldb.models import (AppliedJobs, City, Company, Facebook, FacebookGroup,
                           FacebookPage, FacebookPost, Industry, JobAlert,
                           JobPost, Linkedin, LinkedinPost, Qualification,
                           SearchResult, SentMail, Skill, State, Subscriber,
                           Ticket, Twitter, TwitterPost, User)
from twython.api import Twython


@app.task
def send_email(mto, msubject, mbody):
    if not isinstance(mto, list):
        mto = [mto]
    msg = EmailMessage(msubject, mbody, settings.DEFAULT_FROM_EMAIL, mto)
    msg.content_subtype = "html"
    msg.send()


@app.task
def rebuilding_index():
    from haystack.management.commands import rebuild_index

    rebuild_index.Command().handle(interactive=False)


@app.task
def updating_jobposts():
    jobposts = JobPost.objects.filter(status="Live")
    for job in jobposts:
        job_url = get_absolute_url(job)
        job.slug = get_absolute_url(job)
        # job.minified_url = google_mini('https://peeljobs.com' + job_url, settings.wMINIFIED_URL)
        job.save()


@app.task
def job_alerts_to_users():
    from_date = datetime.now() - timedelta(days=1)
    job_posts = JobPost.objects.filter(
        published_on__range=(from_date, datetime.now()), status="Live"
    )
    users = User.objects.filter(
        email_notifications=True,
        user_type="JS",
        is_bounce=False,
        is_unsubscribe=False,
        skills__skill__id__in=job_posts.values_list("skills", flat=True),
    ).distinct()
    for user in users:
        user_skills = user.skills.values_list("skill", flat=True)
        user_posts = job_posts.filter(
            skills__id__in=user_skills, location__in=[user.current_city]
        )
        if user_posts:
            if user_posts.count() < 10:
                job_order = Case(
                    *[When(pk=pk.id, then=pos) for pos, pk in enumerate(user_posts)]
                )
                user_posts = user_posts | JobPost.objects.filter(
                    skills__in=user_skills, status="Live"
                )
                user_posts = user_posts.order_by(job_order)
            c = {"jobposts": user_posts.distinct()[:10], "user": user}
            t = loader.get_template("email/job_alert.html")
            subject = "Top Matching Jobs for your Profile - PeelJobs"
            rendered = t.render(c)
            mto = [user.email]
            user_active = True if user.is_active else False
            send_email.delay(mto, subject, rendered)


@app.task
def job_alerts_to_subscribers():
    from_date = datetime.now() - timedelta(days=1)
    to_date = datetime.now()
    jobs = JobPost.objects.filter(
        published_on__range=(from_date, to_date), status="Live"
    )
    job_skills = jobs.values_list("skills", flat=True).distinct()
    for sub in Subscriber.objects.filter(
        skill__id__in=job_skills, is_verified=True
    ).distinct("email"):
        skills = Subscriber.objects.filter(email=sub.email).values_list(
            "skill__name", flat=True
        )
        sub_jobs = jobs.filter(skills__name__in=skills)
        if sub_jobs:
            if sub_jobs.count() < 10:
                job_order = Case(
                    *[When(pk=pk.id, then=pos) for pos, pk in enumerate(sub_jobs)]
                )
                sub_jobs = sub_jobs | JobPost.objects.filter(
                    skills__name__in=skills, status="Live"
                ).order_by(job_order)
            c = {
                "subscriber": sub,
                "jobposts": sub_jobs.distinct()[:10],
                "sub_skills": skills,
            }
            t = loader.get_template("email/job_alert.html")
            subject = "Top Matching jobs for your subscription - PeelJobs"
            rendered = t.render(c)
            mto = [sub.email]
            user_active = False
            send_email.delay(mto, subject, rendered)


@app.task
def job_alerts_to_alerts():
    from_date = datetime.now() - timedelta(days=1)
    to_date = datetime.now()
    job_posts = JobPost.objects.filter(
        published_on__range=(from_date, to_date), status="Live"
    )
    job_skills = set(job_posts.values_list("skills", flat=True))
    alerts = JobAlert.objects.filter(skill__in=job_skills, is_verified=True).distinct()
    for alert in alerts:
        alert_jobs = job_posts.filter(
            Q(skills__in=alert.skill.all())
            & Q(
                Q(location__in=alert.location.all())
                | Q(industry__in=alert.industry.all())
                | Q(max_year=alert.max_year)
                | Q(max_salary=alert.max_salary)
                | Q(min_salary=alert.min_salary)
            )
        )
        if alert_jobs:
            job_order = Case(
                *[When(pk=pk.id, then=pos) for pos, pk in enumerate(alert_jobs)]
            )
            if alert_jobs.count() < 10:
                alert_jobs = alert_jobs | JobPost.objects.filter(
                    skills__in=alert.skill.all(), status="Live"
                )
                alert_jobs = alert_jobs.order_by(job_order)
            c = {"alert": alert, "jobposts": alert_jobs.distinct()[:10]}
            t = loader.get_template("email/job_alert.html")
            subject = "Top Matching Jobs For your alert " + alert.name
            rendered = t.render(c)
            mto = [alert.email]
            user_active = False
            send_email.delay(mto, subject, rendered)


@app.task()
def jobpost_published():
    jobposts = JobPost.objects.filter(status="Published")
    for job in jobposts:

        job.status = "Live"
        job.published_on = datetime.now()
        job_url = get_absolute_url(job)
        job.slug = job_url
        job.save()
        posts = FacebookPost.objects.filter(job_post=job)
        for each in posts:
            del_jobpost_fb(job.user, each)
            del_jobpost_peel_fb(job.user, each)
        postonpeel_fb(job)
        postontwitter(job.user.id, job.id, "Page")
        if job.post_on_fb:
            fbpost(job.user.id, job.id)
            postonpage(job.user.id, job.id)
            posts = FacebookPost.objects.filter(
                job_post=job,
                page_or_group="group",
                is_active=True,
                post_status="Deleted",
            )
            for group in job.fb_groups:
                fb_group = FacebookGroup.objects.get(user=job.user, group_id=group)
                postongroup(job.id, fb_group.id)
        posts = TwitterPost.objects.filter(job_post=job)
        for each in posts:
            del_jobpost_tw(job.user, each)

        if job.post_on_tw:
            postontwitter(job.user.id, job.id, "Profile")

        postonlinkedin(job.user.id, job)

        c = {"job_post": job, "user": job.user}
        t = loader.get_template("email/jobpost.html")
        subject = "PeelJobs JobPost Status"
        mto = [settings.DEFAULT_FROM_EMAIL, job.user.email]
        rendered = t.render(c)
        send_email.delay(mto, subject, rendered)


def del_jobpost_fb(user, post):
    if user:
        graph = GraphAPI(settings.FB_DEL_ACCESS_TOKEN)
        try:
            post.post_status = "Deleted"
            post.save()
            graph.delete_object(post.post_id)
            return "deleted successfully"
        except Exception as e:
            return e
    else:
        return "connect to fb"


@app.task()
def fbpost(user, job_post):
    user = User.objects.filter(id=user).first()
    if user.is_fb_connected:
        access_token = get_app_access_token(settings.FB_APP_ID, settings.FB_SECRET)
        job_post = JobPost.objects.filter(id=job_post).first()
        if job_post and access_token:
            params = {}
            params["access_token"] = access_token
            skill_hash = "".join(
                [
                    " #" + name.replace(" ", "").lower()
                    for name in job_post.skills.values_list("name", flat=True)
                ]
            )
            loc_hash = "".join(
                [
                    " #" + name.replace(" ", "").lower()
                    for name in job_post.location.values_list("name", flat=True)
                ]
            )
            params["message"] = (
                (job_post.published_message or job_post.title)
                + skill_hash
                + loc_hash
                + " #Jobs #Peeljobs"
            )
            params["picture"] = settings.LOGO
            params["link"] = "http://peeljobs.com" + str(job_post.get_absolute_url())

            params["name"] = job_post.title
            params["description"] = job_post.company_name
            params["privacy"] = {"value": "ALL_FRIENDS"}
            facebook_id = Facebook.objects.get(user=user).facebook_id
            u = requests.post(
                "https://graph.facebook.com/" + facebook_id + "/feed", params=params
            )
            response = u.json()

            if "error" in response.keys():
                pass
            if "id" in response.keys():
                FacebookPost.objects.create(
                    job_post=job_post,
                    page_or_group="page",
                    page_or_group_id=facebook_id,
                    post_id=response["id"],
                    post_status="Posted",
                )
                return "posted successfully"
            return "error occured in posting"
        else:
            return "jobpost not exists"
    else:
        return "connect with fb first"


def postonpeel_fb(job_post):
    if job_post:
        params = {}
        skill_hash = "".join(
            [
                " #" + name.replace(" ", "").lower()
                for name in job_post.skills.values_list("name", flat=True)
            ]
        )
        loc_hash = "".join(
            [
                " #" + name.replace(" ", "").lower()
                for name in job_post.location.values_list("name", flat=True)
            ]
        )
        params["message"] = (
            (job_post.published_message or job_post.title)
            + skill_hash
            + loc_hash
            + " #Jobs #Peeljobs"
        )
        if job_post.company.profile_pic and job_post.company.is_active:
            params["picture"] = (
                job_post.company.profile_pic
                if "https" in str(job_post.company.profile_pic)
                else "https://cdn.peeljobs.com/" + str(job_post.company.profile_pic)
            )
        elif job_post.major_skill and job_post.major_skill.icon:
            params["picture"] = job_post.major_skill.icon
        elif (
            job_post.skills.all()[0].icon
            and job_post.skills.all()[0].status == "Active"
        ):
            params["picture"] = job_post.skills.all()[0].icon
        else:
            params["picture"] = "https://cdn.peeljobs.com/jobopenings1.png"
        params["link"] = "http://peeljobs.com" + str(job_post.get_absolute_url())
        job_name = job_post.title

        params["description"] = (
            job_post.company.name if job_post.company else job_post.company_name
        )
        params["access_token"] = settings.FB_PAGE_ACCESS_TOKEN
        params["actions"] = [{"name": "get peeljobs", "link": settings.PEEL_URL}]

        params["name"] = job_name
        params["caption"] = "http://peeljobs.com"
        params["actions"] = [{"name": "get peeljobs", "link": "http://peeljobs.com/"}]

        params = urllib.parse.urlencode(params)
        u = requests.post(
            "https://graph.facebook.com/" + settings.FB_PEELJOBS_PAGEID + "/feed",
            params=params,
        )
        response = u.json()
        print(params)
        print(response, "response")
        if "error" in response.keys():
            pass
        if "id" in response.keys():
            FacebookPost.objects.create(
                job_post=job_post,
                page_or_group="peel_jobs",
                page_or_group_id=settings.FB_PEELJOBS_PAGEID,
                post_id=response["id"],
                post_status="Posted",
            )
            return "posted successfully"
        return "job not posted on page"
    else:
        return "jobpost not exists"


@app.task()
def postonpage(user, job_post):
    user = User.objects.filter(id=user).first()
    if user.is_fb_connected:
        pages = FacebookPage.objects.filter(user=user)
        if pages:
            job_post = JobPost.objects.filter(id=job_post).first()
            params = {}
            skill_hash = "".join(
                [
                    " #" + name.replace(" ", "").lower()
                    for name in job_post.skills.values_list("name", flat=True)
                ]
            )
            loc_hash = "".join(
                [
                    " #" + name.replace(" ", "").lower()
                    for name in job_post.location.values_list("name", flat=True)
                ]
            )
            params["message"] = (
                (job_post.published_message or job_post.title)
                + skill_hash
                + loc_hash
                + " #Jobs #Peeljobs"
            )
            params["picture"] = settings.LOGO
            params["link"] = settings.PEEL_URL + str(job_post.slug)
            params["name"] = job_post.title
            params["description"] = job_post.company_name
            params["actions"] = [{"name": "get peeljobs", "link": settings.PEEL_URL}]
            params["access_token"] = pages[0].accesstoken
            params = urllib.parse.urlencode(params)

            for page in pages:
                if page.allow_post:
                    u = requests.post(
                        "https://graph.facebook.com/" + str(page.page_id) + "/feed",
                        params,
                        params=params,
                    )
                    response = u.json()

                    if "id" in response.keys():
                        FacebookPost.objects.create(
                            job_post=job_post,
                            page_or_group=page,
                            page_or_group_id=page.page_id,
                            post_id=response["id"],
                            post_status="Posted",
                        )

            data = "posted successfully"
        else:
            data = "page not exists"
    else:
        data = "user not connected to facebook"
    return data


@app.task()
def postongroup(job_post, group_id):
    job_post = JobPost.objects.filter(id=job_post).first()
    if job_post:
        params = {}
        skill_hash = "".join(
            [
                " #" + name.replace(" ", "").lower()
                for name in job_post.skills.values_list("name", flat=True)
            ]
        )
        loc_hash = "".join(
            [
                " #" + name.replace(" ", "").lower()
                for name in job_post.location.values_list("name", flat=True)
            ]
        )
        params["message"] = (
            (job_post.published_message or job_post.title)
            + skill_hash
            + loc_hash
            + " #Jobs #Peeljobs"
        )

        skills = job_post.get_skills()
        params["picture"] = (
            skills[0].icon if skills and skills[0].icon else settings.LOGO
        )

        PEEL_URL = "https://peeljobs.com"
        params["link"] = PEEL_URL + str(job_post.get_absolute_url())

        params["name"] = job_post.title
        params["description"] = job_post.company_name
        params["access_token"] = settings.FB_GROUP_ACCESS_TOKEN
        params["actions"] = [{"name": "get peeljobs", "link": settings.PEEL_URL}]
        params = urllib.parse.urlencode(params)
        requests.post(
            "https://graph.facebook.com/" + str(group_id) + "/feed", params=params
        )
        return "posted successfully"
    else:
        return "jobpost not exists"


@app.task
def poston_allfb_groups(job_post):
    job_post = JobPost.objects.filter(id=job_post).first()
    with open("mpcomp/fb_groups.json") as data_file:
        data = json.load(data_file)
        for each in data:
            group_id = each["id"]
            params = {}

            job_name = (
                str(job_post.title)
                + ", for Exp "
                + str(job_post.min_year)
                + " - "
                + str(job_post.min_year)
            )
            skill_hash = " #" + " #".join(
                job_post.skills.values_list("name", flat=True)
            )
            loc_hash = " #" + " #".join(
                job_post.location.values_list("name", flat=True)
            )
            params["message"] = (
                job_post.published_message
                or job_post.title + skill_hash + loc_hash + " #jobs #peeljobs"
            )
            skills = job_post.get_skills()

            params["picture"] = (
                skills[0].icon if skills and skills[0].icon else settings.LOGO
            )

            PEEL_URL = "https://peeljobs.com"
            params["link"] = PEEL_URL + str(job_post.get_absolute_url())

            params["name"] = job_name
            params["description"] = job_post.company_name
            params["access_token"] = settings.FB_ALL_GROUPS_TOKEN
            params["actions"] = [{"name": "get peeljobs", "link": settings.PEEL_URL}]
            params = urllib.parse.urlencode(params)
            requests.post(
                "https://graph.facebook.com/" + str(group_id) + "/feed", params=params
            )


def del_jobpost_tw(user, post):
    if user:
        user_twitter = Twitter.objects.filter(user=user)
        if user_twitter:
            user_twitter = user_twitter[0]
            twitter = Twython(
                settings.TW_APP_KEY,
                settings.TW_APP_SECRET,
                user_twitter.oauth_token,
                user_twitter.oauth_secret,
            )
            if twitter and user_twitter:
                try:
                    twitter.destroy_status(id=post.post_id)
                    post.delete()
                except Exception as e:
                    return e
            else:
                return "connect to twitter"
        else:
            return "connect to twitter"
    else:
        return "connect to twitter"


@app.task()
def del_jobpost_peel_fb(user, post):
    if user:
        try:
            graph = GraphAPI(settings.FB_ACCESS_TOKEN)
            post = FacebookPost.objects.get(id=post)
            post.post_status = "Deleted"
            post.save()
            graph.delete_object(post.post_id)
        except:
            print("not deleted")
        return "deleted successfully"
    return "connect to fb"


@app.task()
def postonlinkedin(user, job_post):
    user = User.objects.get(id=user)
    job_post = Jobpost.objects.get(id=job_post)
    link = Linkedin.objects.filter(user__id=user).first()
    job_post = JobPost.objects.filter(id=job_post).first()
    if job_post:
        job_name = (
            str(job_post.title)
            + ", for Exp "
            + str(job_post.min_year)
            + " - "
            + str(job_post.min_year)
            + " in "
        )
        locations = job_post.location.values_list("name", flat=True)
        job_name += ", ".join(locations)
        post = {
            "visibility": {"code": "anyone",},
            "comment": job_post.published_message,
            "content": {
                "title": job_name,
                "submitted-url": "http://peeljobs.com"
                + str(job_post.get_absolute_url()),
                "submitted-image-url": settings.LOGO,
                "description": job_name,
            },
        }

        url = (
            "https://api.linkedin.com/v1/companies/"
            + settings.LN_COMPANYID
            + "/shares?format=json"
        )
        headers = {"x-li-format": "json", "Content-Type": "application/json"}
        pj_linkedin = Linkedin.objects.get(user__email="raghubethi@micropyramid.com")
        params = {"oauth2_access_token": pj_linkedin.accesstoken}
        kw = dict(data=json.dumps(post), params=params, headers=headers, timeout=60)
        response = requests.request("POST", url, **kw)
        response = response.json()
        if "updatekey" in response.keys():
            LinkedinPost.objects.create(
                job_post=job_post,
                profile_or_group="Profile",
                post_id=response["updatekey"],
                post_status="True",
                update_url=response["update_url"],
            )
        if link:
            url = "https://api.linkedin.com/v1/people/~/shares"
            params["oauth2_access_token"] = link.accesstoken
            response = requests.request("POST", url, **kw)
            response = response.json()
            if "updatekey" in response.keys():
                LinkedinPost.objects.create(
                    job_post=job_post,
                    profile_or_group="Profile",
                    post_id=response["updatekey"],
                    post_status="True",
                    update_url=response["update_url"],
                )
        return "posted successfully"
    else:
        return "jobpost not exists"


@app.task()
def postontwitter(user, job_post, page_or_profile):
    job_post = JobPost.objects.filter(id=job_post).first()
    if job_post:
        user = User.objects.filter(id=user).first()
        user_twitter = Twitter.objects.filter(user=user)
        if page_or_profile == "Profile" and user_twitter:
            user_twitter = user_twitter[0]
            twitter = Twython(
                settings.TW_APP_KEY,
                settings.TW_APP_SECRET,
                user_twitter.oauth_token,
                user_twitter.oauth_secret,
            )
        else:
            twitter = Twython(
                settings.TW_APP_KEY,
                settings.TW_APP_SECRET,
                settings.OAUTH_TOKEN,
                settings.OAUTH_SECRET,
            )
        job_name = job_post.title
        skill_hash = "".join(
            [
                " @" + name.replace(" ", "").lower()
                for name in job_post.skills.values_list("name", flat=True)
            ]
        )
        loc_hash = "".join(
            [
                " @" + name.replace(" ", "").lower()
                for name in job_post.location.values_list("name", flat=True)
            ]
        )
        job_name = job_name + skill_hash + loc_hash + " #Jobs #PeelJobs"
        twitter_status = (
            job_name + "  http://peeljobs.com" + str(job_post.get_absolute_url())
        )
        try:
            response = twitter.update_status(status=twitter_status)
        except:
            response = {"empty": ""}
        if "id" in response.keys():
            if page_or_profile == "Profile":
                TwitterPost.objects.create(
                    job_post=job_post,
                    page_or_profile=page_or_profile,
                    post_id=response["id"],
                    post_status="Posted",
                )
            else:
                TwitterPost.objects.create(
                    job_post=job_post,
                    page_or_profile=page_or_profile,
                    post_id=response["id"],
                    post_status="Posted",
                )

            return "posted successfully"
        return "not posted in twitter"
    else:
        return "jobpost not exists"


@app.task()
def sending_mail(emailtemplate, recruiters):
    t = loader.get_template("email/email_template.html")
    c = {"text": emailtemplate.message}
    subject = emailtemplate.subject
    rendered = t.render(c)
    sent_mail = SentMail.objects.create(template=emailtemplate)
    recruiters = User.objects.filter(id__in=recruiters)
    for recruiter in recruiters:
        recruiter = User.objects.get(id=recruiter)
        sent_mail.recruiter.add(recruiter)
        mto = recruiter.email
        user_active = True if recruiter.is_active else False
        send_email.delay(mto, subject, rendered)
    return ""


def get_conditions(user):
    user = User.objects.filter(id=user).first()
    conditions = []
    if user.current_city:
        conditions.append(Q(location__in=[user.current_city]))
    if user.preferred_city.all():
        conditions.append(
            Q(location__in=user.preferred_city.all().values_list("id", flat=True))
        )
    if user.prefered_industry:
        conditions.append(Q(industry__in=[user.prefered_industry]))
    if user.year:
        conditions.append(Q(min_year=user.year))
        conditions.append(Q(max_year=user.year))
    if user.current_salary:
        if isinstance(user.current_salary, float):
            conditions.append(Q(min_salary=float(user.current_salary)))
            conditions.append(Q(max_salary=float(user.current_salary)))
    if user.expected_salary:
        if isinstance(user.expected_salary, float):
            conditions.append(Q(min_salary=float(user.expected_salary)))
            conditions.append(Q(max_salary=float(user.expected_salary)))
    if user.employment_history.all():
        conditions.append(Q(job_role__icontains=user.job_role))
    if user.education.all():
        conditions.append(
            Q(
                edu_qualification__in=user.education.all().values_list(
                    "degree", flat=True
                )
            )
        )
    if user.skills.all():
        conditions.append(Q(skills__in=user.skills.all().values_list("id", flat=True)))
    return conditions


# @app.task()
# def applicants_notifications():

#     current_date = datetime.strptime(
#         str(datetime.now().date() - timedelta(days=10)), "%Y-%m-%d"
#     ).strftime("%Y-%m-%d")
#     today_applicants = User.objects.filter(
#         email_notifications=True,
#         profile_updated__lte=current_date,
#         profile_completeness__lte=50,
#         user_type="JS",
#         is_bounce=False,
#         is_unsubscribe=False,
#     )
#     for user in today_applicants:
#         conditions = get_conditions(user)
#         if conditions:
#             jobposts = (
#                 JobPost.objects.filter(reduce(OR, conditions))
#                 .filter(status="Live")
#                 .distinct()[:10]
#             )
#         else:
#             jobposts = JobPost.objects.filter(status="Live")[:10]
#         # sending an email
#         c = {"job_posts": jobposts, "user": user}
#         t = loader.get_template("email/applicant.html")
#         subject = "Update Your Profile To Get Top Matching Jobs - PeelJobs"
#         rendered = t.render(c)
#         mto = [user.email]
#         user_active = True if user.is_active else False
#         send_email.delay(mto, subject, rendered)


# sending mail to recruiters about applicants
@app.task()
def recruiter_jobpost_applicants():
    recruiters = User.objects.filter(
        user_type="RR", is_bounce=False, is_unsubscribe=False, email_notifications=True
    )
    current_date = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").strftime(
        "%Y-%m-%d"
    )
    for each in recruiters:
        if each.get_jobposts_count() > 1:
            job_posts = JobPost.objects.filter(
                user=each, status="Live", send_email_notifications=True
            )
            for job in job_posts:
                applicants = AppliedJobs.objects.filter(
                    job_post=job, applied_on__date=current_date
                )
                if len(applicants) >= 10:
                    c = {"jobposts": job, "user": each, "applicants": applicants[:10]}
                    t = loader.get_template("email/job_applicants.html")
                    subject = "No. Of Applicants Applied For Your Job"
                    rendered = t.render(c)
                    mto = [each.email]
                    user_active = True if each.is_active else False
                    send_email.delay(mto, subject, rendered)


@app.task()
def daily_report():
    current_date = datetime.strptime(
        str(datetime.now().date() - timedelta(days=1)), "%Y-%m-%d"
    ).strftime("%Y-%m-%d")

    today_jobs_count = JobPost.objects.filter(
        published_on__icontains=current_date
    ).exclude(user__is_superuser=True)

    today_full_time_jobs_count = JobPost.objects.filter(
        job_type="full-time", published_on__icontains=current_date
    ).exclude(user__is_superuser=True)
    today_govt_jobs_count = JobPost.objects.filter(
        job_type="government", published_on__icontains=current_date
    ).exclude(user__is_superuser=True)
    today_internship_jobs_count = JobPost.objects.filter(
        job_type="internship", published_on__icontains=current_date
    ).exclude(user__is_superuser=True)
    today_walkin_jobs_count = JobPost.objects.filter(
        job_type="walk-in", published_on__icontains=current_date
    ).exclude(user__is_superuser=True)

    today_admin_jobs_count = JobPost.objects.filter(
        published_on__icontains=current_date, user__is_superuser=True
    )

    today_admin_full_time_jobs_count = JobPost.objects.filter(
        job_type="full-time",
        published_on__icontains=current_date,
        user__is_superuser=True,
    )
    today_admin_govt_jobs_count = JobPost.objects.filter(
        job_type="government",
        published_on__icontains=current_date,
        user__is_superuser=True,
    )
    today_admin_internship_jobs_count = JobPost.objects.filter(
        job_type="internship",
        published_on__icontains=current_date,
        user__is_superuser=True,
    )
    today_admin_walkin_jobs_count = JobPost.objects.filter(
        job_type="walk-in",
        published_on__icontains=current_date,
        user__is_superuser=True,
    )

    today_applicants_count = User.objects.filter(
        date_joined__contains=current_date, user_type="JS", registered_from="Social"
    )

    today_register_applicants_count = User.objects.filter(
        date_joined__contains=current_date, user_type="JS", registered_from="Email"
    )

    resume_applicants_count = User.objects.filter(
        date_joined__contains=current_date, user_type="JS", registered_from="Resume"
    )

    resumepool_applicants = User.objects.filter(
        date_joined__contains=current_date, user_type="JS", registered_from="ResumePool"
    )

    today_total_recruiters = User.objects.filter(
        date_joined__contains=current_date
    ).exclude(user_type="JS")

    today_recruiters_count = User.objects.filter(
        date_joined__contains=current_date, user_type="RR"
    )

    today_agency_recruiters_count = User.objects.filter(
        date_joined__contains=current_date, user_type="AA"
    )

    today_total_recruiters = (
        today_recruiters_count.count() + today_agency_recruiters_count.count()
    )

    today_active_recruiters = today_recruiters_count.filter(is_active=True)
    today_inactive_recruiters = today_recruiters_count.filter(is_active=False)

    today_agency_recruiters_count = User.objects.filter(
        date_joined__contains=current_date, user_type="AA"
    )

    today_agency_active_recruiters = today_agency_recruiters_count.filter(
        is_active=True
    )
    today_agency_inactive_recruiters = today_agency_recruiters_count.filter(
        is_active=False
    )

    today_job_applications = AppliedJobs.objects.filter(
        applied_on__contains=current_date
    )

    job_applied_users = User.objects.filter(
        id__in=today_job_applications.values("user")
    )
    today_tickets = Ticket.objects.filter(created_on__contains=current_date)

    formatted_date = datetime.strptime(str(current_date), "%Y-%m-%d").strftime(
        "%d-%m-%Y"
    )

    data = {
        "current_date": current_date,
        "today_active_tickets": today_tickets.filter(status="Open").count(),
        "today_closed_tickets": today_tickets.filter(status="Closed").count(),
        "today_job_applications": today_job_applications.count(),
        "today_jobs_count": today_jobs_count.count(),
        "today_jobs_draft_count": today_jobs_count.filter(status="Draft").count(),
        "today_jobs_pending_count": today_jobs_count.filter(status="Pending").count(),
        "today_jobs_published_count": today_jobs_count.filter(
            status="Published"
        ).count(),
        "today_jobs_live_count": today_jobs_count.filter(status="Live").count(),
        "today_jobs_disabled_count": today_jobs_count.filter(status="Disabled").count(),
        "today_all_applicants_count": User.objects.filter(
            date_joined__contains=current_date, user_type="JS"
        ).count(),
        "today_full_time_jobs_count": today_full_time_jobs_count.count(),
        "today_full_time_draft_jobs_count": today_full_time_jobs_count.filter(
            status="Draft"
        ).count(),
        "today_full_time_pending_jobs_count": today_full_time_jobs_count.filter(
            status="Pending"
        ).count(),
        "today_full_time_published_jobs_count": today_full_time_jobs_count.filter(
            status="Published"
        ).count(),
        "today_full_time_live_jobs_count": today_full_time_jobs_count.filter(
            status="Live"
        ).count(),
        "today_full_time_disabled_jobs_count": today_full_time_jobs_count.filter(
            status="Disabled"
        ).count(),
        "today_govt_jobs_count": today_govt_jobs_count.count(),
        "today_govt_jobs_draft_count": today_govt_jobs_count.filter(
            status="Draft"
        ).count(),
        "today_govt_jobs_pending_count": today_govt_jobs_count.filter(
            status="Pending"
        ).count(),
        "today_govt_jobs_published_count": today_govt_jobs_count.filter(
            status="Published"
        ).count(),
        "today_govt_jobs_live_count": today_govt_jobs_count.filter(
            status="Live"
        ).count(),
        "today_govt_jobs_disabled_count": today_govt_jobs_count.filter(
            status="Disabled"
        ).count(),
        "today_internship_jobs_count": today_internship_jobs_count.count(),
        "today_internship_jobs_draft_count": today_internship_jobs_count.filter(
            status="Draft"
        ).count(),
        "today_internship_jobs_pending_count": today_internship_jobs_count.filter(
            status="Pending"
        ).count(),
        "today_internship_jobs_published_count": today_internship_jobs_count.filter(
            status="Published"
        ).count(),
        "today_internship_jobs_live_count": today_internship_jobs_count.filter(
            status="Live"
        ).count(),
        "today_internship_jobs_disabled_count": today_internship_jobs_count.filter(
            status="Disabled"
        ).count(),
        "today_walkin_jobs_count": today_walkin_jobs_count.count(),
        "today_walkin_jobs_draft_count": today_walkin_jobs_count.filter(
            status="Draft"
        ).count(),
        "today_walkin_jobs_pending_count": today_walkin_jobs_count.filter(
            status="Pending"
        ).count(),
        "today_walkin_jobs_published_count": today_walkin_jobs_count.filter(
            status="Published"
        ).count(),
        "today_walkin_jobs_live_count": today_walkin_jobs_count.filter(
            status="Live"
        ).count(),
        "today_walkin_jobs_disabled_count": today_walkin_jobs_count.filter(
            status="Disabled"
        ).count(),
        "today_admin_jobs_count": today_admin_jobs_count.count(),
        "today_admin_draft_jobs_count": today_admin_jobs_count.filter(
            status="Draft"
        ).count(),
        "today_admin_pending_jobs_count": today_admin_jobs_count.filter(
            status="Pending"
        ).count(),
        "today_admin_published_jobs_count": today_admin_jobs_count.filter(
            status="Published"
        ).count(),
        "today_admin_live_jobs_count": today_admin_jobs_count.filter(
            status="Live"
        ).count(),
        "today_admin_disabled_jobs_count": today_admin_jobs_count.filter(
            status="Disabled"
        ).count(),
        "today_admin_full_time_draft_jobs_count": today_admin_full_time_jobs_count.filter(
            status="Draft"
        ).count(),
        "today_admin_full_time_pending_jobs_count": today_admin_full_time_jobs_count.filter(
            status="Pending"
        ).count(),
        "today_admin_full_time_published_jobs_count": today_admin_full_time_jobs_count.filter(
            status="Published"
        ).count(),
        "today_admin_full_time_jobs_count": today_admin_full_time_jobs_count.count(),
        "today_admin_full_time_live_jobs_count": today_admin_full_time_jobs_count.filter(
            status="Live"
        ).count(),
        "today_admin_full_time_disabled_jobs_count": today_admin_full_time_jobs_count.filter(
            status="Disabled"
        ).count(),
        "today_admin_govt_jobs_count": today_admin_govt_jobs_count.count(),
        "today_admin_govt_draft_jobs_count": today_admin_govt_jobs_count.filter(
            status="Draft"
        ).count(),
        "today_admin_govt_pending_jobs_count": today_admin_govt_jobs_count.filter(
            status="Pending"
        ).count(),
        "today_admin_govt_published_jobs_count": today_admin_govt_jobs_count.filter(
            status="Published"
        ).count(),
        "today_admin_govt_live_jobs_count": today_admin_govt_jobs_count.filter(
            status="Live"
        ).count(),
        "today_admin_govt_disabled_jobs_count": today_admin_govt_jobs_count.filter(
            status="Disabled"
        ).count(),
        "today_admin_internship_jobs_count": today_admin_internship_jobs_count.count(),
        "today_admin_internship_draft_jobs_count": today_admin_internship_jobs_count.filter(
            status="Draft"
        ).count(),
        "today_admin_internship_pending_jobs_count": today_admin_internship_jobs_count.filter(
            status="Pending"
        ).count(),
        "today_admin_internship_published_jobs_count": today_admin_internship_jobs_count.filter(
            status="Published"
        ).count(),
        "today_admin_internship_live_jobs_count": today_admin_internship_jobs_count.filter(
            status="Live"
        ).count(),
        "today_admin_internship_disabled_jobs_count": today_admin_internship_jobs_count.filter(
            status="Disabled"
        ).count(),
        "today_admin_walkin_jobs_count": today_admin_walkin_jobs_count.count(),
        "today_admin_walkin_draft_jobs_count": today_admin_walkin_jobs_count.filter(
            status="Draft"
        ).count(),
        "today_admin_walkin_pending_jobs_count": today_admin_walkin_jobs_count.filter(
            status="Pending"
        ).count(),
        "today_admin_walkin_published_jobs_count": today_admin_walkin_jobs_count.filter(
            status="Published"
        ).count(),
        "today_admin_walkin_live_jobs_count": today_admin_walkin_jobs_count.filter(
            status="Live"
        ).count(),
        "today_admin_walkin_disabled_jobs_count": today_admin_walkin_jobs_count.filter(
            status="Disabled"
        ).count(),
        "today_applicants_count": today_applicants_count.count(),
        "today_login_only_once_applicants_count": today_applicants_count.filter(
            is_login=False
        ).count(),
        "today_resume_applicants_count": today_applicants_count.exclude(
            resume=""
        ).count(),
        "today_profile_applicants_count": today_applicants_count.filter(
            profile_completeness__gte=50
        ).count(),
        "today_applied_applicants_count": job_applied_users.filter(
            registered_from="Social"
        ).count(),
        "resume_applicants_count": resume_applicants_count.count(),
        "resume_login_once_applicants_count": resume_applicants_count.filter(
            is_login=False
        ).count(),
        "resume_uploaded_applicants_count": resume_applicants_count.exclude(
            resume=""
        ).count(),
        "resume_profile_applicants_count": resume_applicants_count.filter(
            profile_completeness__gte=50
        ).count(),
        "resume_applied_applicants_count": job_applied_users.filter(
            registered_from="Resume"
        ).count(),
        "resumepool_applicants": resumepool_applicants.count(),
        "resumepool_login_once_applicants": resumepool_applicants.filter(
            is_login=False
        ).count(),
        "resumepool_profile_applicants": resumepool_applicants.filter(
            profile_completeness__gte=50
        ).count(),
        "resumepool_applied_applicants": job_applied_users.filter(
            registered_from="Resume"
        ).count(),
        "today_register_applicants_count": today_register_applicants_count.count(),
        "today_register_login_only_once_applicants_count": today_register_applicants_count.filter(
            is_login=False
        ).count(),
        "today_register_resume_applicants_count": today_register_applicants_count.filter()
        .exclude(resume="")
        .count(),
        "today_register_profile_applicants_count": today_register_applicants_count.filter(
            profile_completeness__gte=50
        ).count(),
        "today_register_applied_applicants_count": job_applied_users.filter(
            registered_from="Email"
        ).count(),
        "today_total_recruiters": today_total_recruiters,
        "today_recruiters_count": today_recruiters_count.count(),
        "today_active_recruiters": today_active_recruiters.count(),
        "today_inactive_recruiters": today_inactive_recruiters.count(),
        "today_agency_recruiters_count": today_agency_recruiters_count.count(),
        "today_agency_active_recruiters": today_agency_active_recruiters.count(),
        "today_agency_inactive_recruiters": today_agency_inactive_recruiters.count(),
    }
    users = settings.DAILY_REPORT_USERS

    for each in users:
        temp = loader.get_template("email/daily_report.html")
        subject = "Peeljobs Daily Report For " + formatted_date
        mto = [each]
        rendered = temp.render(data)
        send_email.delay(mto, subject, rendered)


# @app.task()
# def applicants_profile_update_notifications_two_hours():
#     today_applicants = User.objects.filter(
#         user_type="JS",
#         profile_completeness__lt=50,
#         is_unsubscribe=False,
#         is_bounce=False,
#         email_notifications=True,
#     ).exclude(email__icontains="micropyramid.com")
#     for user in today_applicants:
#         if user.date_joined and user.date_joined > datetime.today() - timedelta(
#             hours=2
#         ):
#             temp = loader.get_template("email/user_profile_alert.html")
#             subject = "Update Your Profile To Get Top Matching Jobs - Peeljobs"
#             mto = [user.email]
#             rendered = temp.render({"user": user})
#             user_active = True if user.is_active else False
#             send_email.delay(mto, subject, rendered)


@app.task()
def applicants_profile_update_notifications():
    today_applicants = User.objects.filter(
        user_type="JS",
        profile_completeness__lt=50,
        is_unsubscribe=False,
        is_bounce=False,
        email_notifications=True,
    ).exclude(email__icontains="micropyramid.com")
    for each in today_applicants:
        days = (datetime.today() - each.date_joined).days
        if days == 4 or days == 6 or days % 7 == 0:
            skills = Skill.objects.filter(
                id__in=each.skills.all().values_list("skill_id", flat=True)
            )
            if skills:
                job_posts = JobPost.objects.filter(status="Live", skills__in=skills)[
                    :15
                ]
            else:
                job_posts = JobPost.objects.filter(status="Live")[:15]
            temp = loader.get_template("email/user_profile_alert.html")
            if days == 4:
                subject = "Recruiters are unable to contact you - Peeljobs"
            if days == 6:
                subject = (
                    "Your Peeljobs account is missing Critical Information - Peeljobs"
                )
            else:
                subject = "Update Your Profile To Get Top Matching Jobs - Peeljobs"
            rendered = temp.render({"user": each, "job_posts": job_posts})
            user_active = True if each.is_active else False
            mto = [each.email]
            send_email.delay(mto, subject, rendered)
    recruiters = User.objects.filter(
        Q(Q(user_type="RR") | Q(user_type="AA"))
        & Q(
            email_notifications=True,
            is_unsubscribe=False,
            is_bounce=False,
            is_active=False,
        )
    )
    # for user in recruiters:
    #     days = (datetime.today() - user.date_joined).days
    #     if days == 2 or days % 10 == 0:
    #         temp = loader.get_template("email/account_inactive.html")
    #         subject = "Update Your Profile - Peeljobs"
    #         rendered = temp.render({"user": user})
    #         mto = [user.email]
    #         send_email.delay(mto, subject, rendered)
 
    day = datetime.today() - timedelta(days=2)
    users = User.objects.filter(
        user_type="JS",
        resume="",
        email_notifications=True,
        date_joined__contains=day.date(),
        is_unsubscribe=False,
        is_bounce=False,
    )
    for user in users:
        temp = loader.get_template("email/user_profile_alert.html")
        subject = "Upload your Resume/cv - Peeljobs"
        rendered = temp.render({"user": user, "resume_update": True})
        user_active = True if user.is_active else False
        mto = [user.email]
        send_email.delay(mto, subject, rendered)


@app.task()
def recruiter_profile_update_notifications():
    recruiters = User.objects.filter(
        Q(Q(user_type="RR") | Q(user_type="AA"))
        & Q(
            email_notifications=True,
            is_unsubscribe=False,
            is_bounce=False,
            profile_completeness__lt=50,
        )
    )
    for recruiter in recruiters:
        temp = loader.get_template("email/user_profile_alert.html")
        subject = "Update Your Profile To Get More Applicants - Peeljobs"
        mto = [recruiter.email]
        rendered = temp.render({"user": recruiter, "recruiter": True})
        user_active = True if recruiter.is_active else False
        send_email.delay(mto, subject, rendered)


@app.task()
def applicants_all_job_notifications():

    today_applicants = User.objects.filter(
        user_type="JS", is_unsubscribe=False, is_bounce=False, email_notifications=True
    )

    for each in today_applicants:
        job_posts = each.related_jobs()
        temp = loader.get_template("email/applicant.html")
        subject = "Top matching jobs for you - Peeljobs"
        mto = [each.email]
        rendered = temp.render({"job_posts": job_posts[:10], "user": each})
        user_active = True if each.is_active else False
        send_email.delay(mto, subject, rendered)


@app.task()
def applicants_job_notifications():
    users = User.objects.filter(
        user_type="JS", is_unsubscribe=False, is_bounce=False, email_notifications=True
    ).exclude(email__icontains="micropyramid.com")
    for user in users:
        job_posts = []
        if user.skills.all():
            tech_skills = Skill.objects.filter(id__in=user.skills.all().values("skill"))
            job_posts = JobPost.objects.filter(status="Live", skills__in=tech_skills)
        if user.current_city and job_posts:
            job_posts = job_posts.filter(location=user.current_city)
        else:
            job_posts = JobPost.objects.filter(
                status="Live", location=user.current_city
            )
        if len(job_posts) < 10:
            job_posts = list(job_posts) + list(JobPost.objects.filter(status="Live"))
        temp = loader.get_template("email/applicant.html")
        subject = "Top matching jobs for you - Peeljobs"
        mto = [user.email]
        rendered = temp.render({"jobposts": job_posts[:10], "user": user})
        user_active = True if user.is_active else False
        send_email.delay(mto, subject, rendered)


# @app.task()
# def alerting_applicants():
#     date = (datetime.today() - timedelta(days=7)).date()
#     users = User.objects.filter(
#         user_type="JS",
#         email_notifications=True,
#         is_unsubscribe=False,
#         is_bounce=False,
#         last_login__icontains=date,
#     )
#     for user in users:
#         temp = loader.get_template("email/user_profile_alert.html")
#         subject = "Update Your Profile To Get Top Matching Jobs - PeelJobs"
#         mto = [user.email]
#         rendered = temp.render({"user": user, "inactive_user": True})
#         user_active = True if user.is_active else False
#         send_email.delay(mto, subject, rendered)
#     recruiters = User.objects.filter(
#         Q(Q(user_type="RR") | Q(user_type="AA"))
#         & Q(
#             email_notifications=True,
#             is_unsubscribe=False,
#             is_bounce=False,
#             last_login__icontains=date,
#         )
#     )
#     for recruiter in recruiters:
#         temp = loader.get_template("email/user_profile_alert.html")
#         subject = "Update Your Profile To Post Unlimited Jobs - PeelJobs"
#         mto = [recruiter.email]
#         rendered = temp.render(
#             {"user": recruiter, "recruiter": True, "inactive_user": True}
#         )
#         user_active = True if recruiter.is_active else False
#         send_email.delay(mto, subject, rendered)
#     # Sending Birthday Wishes
#     current_date = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").strftime(
#         "%m-%d"
#     )
#     users = User.objects.filter(dob__icontains=current_date)
#     for user in users:
#         temp = loader.get_template("email/birthdays.html")
#         subject = (
#             "=?UTF-8?Q?=F0=9F=8E=82?="
#             + " Birthday Wishes - Peeljobs "
#             + "=?UTF-8?Q?=F0=9F=8E=82?="
#         )
#         rendered = temp.render({"user": user})
#         user_active = True if user.is_active else False
#         mto = user.email
#         send_email.delay(mto, subject, rendered)


@app.task()
def sitemap_generation():
    print("Sitemap Generation started")
    import os

    try:
        os.system("rm sitemap/*")
    except:
        pass
    xml_cont = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">"""

    xml_cont = (
        xml_cont
        + "<url><loc>https://peeljobs.com/</loc>"
        + "<changefreq>always</changefreq><priority>1.0</priority></url>"
    )

    end_url = "</loc><changefreq>daily</changefreq><priority>0.5</priority></url>"

    # jobs
    jobs_xml_cont = xml_cont
    jobs = JobPost.objects.filter(status="Live")
    for job in jobs:
        jobs_xml_cont = (
            jobs_xml_cont + "<url><loc>https://peeljobs.com" + job.slug + end_url
        )

    jobs_xml_cont = jobs_xml_cont + "</urlset>"

    try:
        open("sitemap/")
    except:
        os.makedirs("sitemap", exist_ok=True)
    jobs_xml_file = open("sitemap/sitemap-jobs.xml", "w")
    jobs_xml_file.write(jobs_xml_cont.encode("ascii", "ignore").decode("ascii"))

    # skills
    skills_xml_cont = xml_cont
    no_job_skills_xml_cont = xml_cont
    skills = Skill.objects.filter(status="Active").exclude(name__iexact="Fresher")

    for skill in skills:
        jobs = JobPost.objects.filter(status="Live", skills=skill).count()
        if jobs > 0:
            skills_xml_cont = (
                skills_xml_cont
                + "<url><loc>https://peeljobs.com"
                + skill.get_job_url()
                + end_url
            )
        else:
            no_job_skills_xml_cont = (
                no_job_skills_xml_cont
                + "<url><loc>https://peeljobs.com"
                + skill.get_job_url()
                + end_url
            )
    skills_xml_cont = skills_xml_cont + "</urlset>"

    skills_xml_file = open("sitemap/sitemap-skills.xml", "w")
    skills_xml_file.write(skills_xml_cont)
    if no_job_skills_xml_cont != xml_cont:
        no_job_skills_xml_cont = no_job_skills_xml_cont + "</urlset>"
        no_job_skills_xml_file = open("sitemap/sitemap-skills-without-jobs.xml", "w")
        no_job_skills_xml_file.write(no_job_skills_xml_cont)

    # locations
    locations_xml_cont = xml_cont
    no_job_locations_xml_cont = xml_cont
    locations = City.objects.filter(status="Enabled", parent_city=None)

    for location in locations:
        jobs = JobPost.objects.filter(status="Live", location=location).count()
        if jobs > 0:
            locations_xml_cont = (
                locations_xml_cont
                + "<url><loc>https://peeljobs.com"
                + location.get_job_url()
                + end_url
            )
        else:
            no_job_locations_xml_cont = (
                no_job_locations_xml_cont
                + "<url><loc>https://peeljobs.com"
                + location.get_job_url()
                + end_url
            )
    locations_xml_cont = locations_xml_cont + "</urlset>"

    locations_xml_file = open("sitemap/sitemap-locations.xml", "w")
    locations_xml_file.write(locations_xml_cont)
    if no_job_locations_xml_cont != xml_cont:
        no_job_locations_xml_cont = no_job_locations_xml_cont + "</urlset>"
        no_job_locations_xml_file = open(
            "sitemap/sitemap-locations-without-jobs.xml", "w"
        )
        no_job_locations_xml_file.write(no_job_locations_xml_cont)

    # industries
    industries = Industry.objects.filter(status="Active")
    industries_xml_cont = xml_cont

    for industry in industries:
        industries_xml_cont = (
            industries_xml_cont
            + "<url><loc>https://peeljobs.com"
            + industry.get_job_url()
            + end_url
        )
    industries_xml_cont = industries_xml_cont + "</urlset>"

    indsutries_xml_file = open("sitemap/sitemap-industries.xml", "w")
    indsutries_xml_file.write(industries_xml_cont)

    # internship locations
    internship_xml_cont = xml_cont

    all_jobs = (
        JobPost.objects.filter(job_type="internship", status="Live")
        .values_list("location", flat=True)
        .distinct()
    )
    internships = City.objects.filter(id__in=all_jobs, status="Enabled")

    for internship in internships:
        internship_xml_cont = (
            internship_xml_cont
            + "<url><loc>https://peeljobs.com/internship-jobs-in-"
            + internship.slug
            + "/"
            + end_url
        )
    internship_xml_cont = internship_xml_cont + "</urlset>"

    internship_xml_file = open("sitemap/sitemap-internships.xml", "w")
    internship_xml_file.write(internship_xml_cont)

    # skill walkins
    skills_walkin_xml_cont = xml_cont
    no_job_skills_walkin_xml_cont = xml_cont

    for skill in skills:
        jobs = JobPost.objects.filter(
            status="Live", skills=skill, job_type="walk-in"
        ).count()
        if jobs > 0:
            skills_walkin_xml_cont = (
                skills_walkin_xml_cont
                + "<url><loc>https://peeljobs.com/"
                + str(skill.slug)
                + "-walkins/"
                + end_url
            )
        else:
            no_job_skills_walkin_xml_cont = (
                no_job_skills_walkin_xml_cont
                + "<url><loc>https://peeljobs.com/"
                + str(skill.slug)
                + "-walkins/"
                + end_url
            )
    skills_walkin_xml_cont = skills_walkin_xml_cont + "</urlset>"
    no_job_skills_walkin_xml_cont = no_job_skills_walkin_xml_cont + "</urlset>"

    skills_walkin_xml_file = open("sitemap/sitemap-skill-walkins.xml", "w")
    skills_walkin_xml_file.write(skills_walkin_xml_cont)
    no_job_skills_walkin_xml_file = open(
        "sitemap/sitemap-skill-without-walkins.xml", "w"
    )
    no_job_skills_walkin_xml_file.write(no_job_skills_walkin_xml_cont)

    # skill locations
    lol = lambda lst, sz: [locations[i : i + sz] for i in range(0, len(locations), sz)]
    locations = lol(locations, 40)
    for index, each in enumerate(locations):
        skills_locations_xml_cont = xml_cont
        no_job_skills_locations_xml_cont = xml_cont
        skills_locations_walkins_xml_cont = xml_cont
        no_job_skills_locations_walkins_xml_cont = xml_cont
        for location in each:
            for skill in skills:
                jobs = JobPost.objects.filter(
                    status="Live", skills=skill, location=location
                ).count()
                walkins = JobPost.objects.filter(
                    status="Live", skills=skill, job_type="walk-in", location=location
                ).count()
                if jobs > 0:
                    skills_locations_xml_cont = (
                        skills_locations_xml_cont
                        + "<url><loc>https://peeljobs.com/"
                        + str(skill.slug)
                        + "-jobs-in-"
                        + str(location.slug)
                        + "/"
                        + end_url
                    )
                else:
                    no_job_skills_locations_xml_cont = (
                        no_job_skills_locations_xml_cont
                        + "<url><loc>https://peeljobs.com/"
                        + str(skill.slug)
                        + "-jobs-in-"
                        + str(location.slug)
                        + "/"
                        + end_url
                    )
                if walkins > 0:
                    skills_locations_walkins_xml_cont = (
                        skills_locations_walkins_xml_cont
                        + "<url><loc>https://peeljobs.com/"
                        + str(skill.slug)
                        + "-walkins-in-"
                        + str(location.slug)
                        + "/"
                        + end_url
                    )
                else:
                    no_job_skills_locations_walkins_xml_cont = (
                        no_job_skills_locations_walkins_xml_cont
                        + "<url><loc>https://peeljobs.com/"
                        + str(skill.slug)
                        + "-walkins-in-"
                        + str(location.slug)
                        + "/"
                        + end_url
                    )
        skills_locations_xml_cont = skills_locations_xml_cont + "</urlset>"
        no_job_skills_locations_xml_cont = (
            no_job_skills_locations_xml_cont + "</urlset>"
        )

        skills_location_xml_file = open(
            "sitemap/sitemap-skill-locations-" + str(index) + ".xml", "w"
        )
        skills_location_xml_file.write(skills_locations_xml_cont)
        no_job_skills_location_xml_file = open(
            "sitemap/sitemap-skill-locations-without-jobs-" + str(index) + ".xml",
            "w",
        )
        no_job_skills_location_xml_file.write(no_job_skills_locations_xml_cont)

        skills_locations_walkins_xml_cont = (
            skills_locations_walkins_xml_cont + "</urlset>"
        )
        no_job_skills_locations_walkins_xml_cont = (
            no_job_skills_locations_walkins_xml_cont + "</urlset>"
        )

        skills_location_walkins_xml_file = open(
            "sitemap/sitemap-skill-location-walkins-" + str(index) + ".xml", "w"
        )
        skills_location_walkins_xml_file.write(skills_locations_walkins_xml_cont)
        no_job_skills_location_walkins_xml_file = open(
            "sitemap/sitemap-skill-location-without-walkins-" + str(index) + ".xml",
            "w",
        )
        no_job_skills_location_walkins_xml_file.write(
            no_job_skills_locations_walkins_xml_cont
        )

    for index, each in enumerate(locations):
        skills_location_fresher_xml_cont = xml_cont
        no_job_skills_location_fresher_xml_cont = xml_cont
        for location in each:
            for skill in skills:
                jobs = JobPost.objects.filter(
                    status="Live", skills=skill, location=location, min_year=0
                ).count()
                if jobs > 0:
                    skills_location_fresher_xml_cont = (
                        skills_location_fresher_xml_cont
                        + "<url><loc>https://peeljobs.com/"
                        + str(skill.slug)
                        + "-fresher-jobs-in-"
                        + str(location.slug)
                        + "/"
                        + end_url
                    )
                else:
                    no_job_skills_location_fresher_xml_cont = (
                        no_job_skills_location_fresher_xml_cont
                        + "<url><loc>https://peeljobs.com/"
                        + str(skill.slug)
                        + "-fresher-jobs-in-"
                        + str(location.slug)
                        + "/"
                        + end_url
                    )
        skills_location_fresher_xml_cont = (
            skills_location_fresher_xml_cont + "</urlset>"
        )
        no_job_skills_location_fresher_xml_cont = (
            no_job_skills_location_fresher_xml_cont + "</urlset>"
        )

        skills_location_fresher_xml_file = open(
            "sitemap/sitemap-skill-location-fresher-jobs-" + str(index) + ".xml", "w"
        )
        skills_location_fresher_xml_file.write(skills_location_fresher_xml_cont)

        no_job_skills_location_fresher_xml_file = open(
            "sitemap/sitemap-skill-location-without-fresher-jobs-"
            + str(index)
            + ".xml",
            "w",
        )
        no_job_skills_location_fresher_xml_file.write(
            no_job_skills_location_fresher_xml_cont
        )

    locations_walkin_xml_cont = xml_cont
    locations_fresher_jobs_xml_cont = xml_cont
    no_job_locations_walkin_xml_cont = xml_cont
    no_job_locations_fresher_jobs_xml_cont = xml_cont
    locations = City.objects.filter(status="Enabled", parent_city=None)
    for each in locations:
        walkins = JobPost.objects.filter(
            status="Live", location=each, job_type="walk-in"
        ).count()
        fresher_jobs = JobPost.objects.filter(
            status="Live", location=each, min_year=0
        ).count()
        if walkins > 0:
            locations_walkin_xml_cont = (
                locations_walkin_xml_cont
                + "<url><loc>https://peeljobs.com/"
                + "walkins-in-"
                + str(each.slug)
                + "/"
                + end_url
            )
        else:
            no_job_locations_walkin_xml_cont = (
                no_job_locations_walkin_xml_cont
                + "<url><loc>https://peeljobs.com/"
                + "walkins-in-"
                + str(each.slug)
                + "/"
                + end_url
            )
        if fresher_jobs > 0:
            locations_fresher_jobs_xml_cont = (
                locations_fresher_jobs_xml_cont
                + "<url><loc>https://peeljobs.com/"
                + "fresher-jobs-in-"
                + str(each.slug)
                + "/"
                + end_url
            )
        else:
            no_job_locations_fresher_jobs_xml_cont = (
                no_job_locations_fresher_jobs_xml_cont
                + "<url><loc>https://peeljobs.com/"
                + "fresher-jobs-in-"
                + str(each.slug)
                + "/"
                + end_url
            )
    locations_walkin_xml_cont = locations_walkin_xml_cont + "</urlset>"
    locations_walkin_xml_file = open("sitemap/sitemap-location-walkins.xml", "w")
    locations_walkin_xml_file.write(locations_walkin_xml_cont)

    no_job_locations_walkin_xml_cont = no_job_locations_walkin_xml_cont + "</urlset>"
    no_job_locations_walkin_xml_file = open(
        "sitemap/sitemap-location-without-walkins.xml", "w"
    )
    no_job_locations_walkin_xml_file.write(no_job_locations_walkin_xml_cont)

    locations_fresher_jobs_xml_cont = locations_fresher_jobs_xml_cont + "</urlset>"
    locations_fresher_jobs_xml_file = open(
        "sitemap/sitemap-location-fresher-jobs.xml", "w"
    )
    locations_fresher_jobs_xml_file.write(locations_fresher_jobs_xml_cont)
    no_job_locations_fresher_jobs_xml_cont = (
        no_job_locations_fresher_jobs_xml_cont + "</urlset>"
    )
    no_job_locations_fresher_jobs_xml_file = open(
        "sitemap/sitemap-location-without-fresher-jobs.xml", "w"
    )
    no_job_locations_fresher_jobs_xml_file.write(no_job_locations_fresher_jobs_xml_cont)

    states = State.objects.filter(status="Enabled")
    states_jobs_xml_count = xml_cont
    states_walkins_xml_count = xml_cont
    states_fresher_jobs_xml_count = xml_cont
    for state in states:
        states_jobs_xml_count = (
            states_jobs_xml_count
            + "<url><loc>https://peeljobs.com/"
            + "jobs-in-"
            + str(state.slug)
            + "/"
            + end_url
        )
        states_walkins_xml_count = (
            states_walkins_xml_count
            + "<url><loc>https://peeljobs.com/"
            + "walkins-in-"
            + str(state.slug)
            + "/"
            + end_url
        )
        states_fresher_jobs_xml_count = (
            states_fresher_jobs_xml_count
            + "<url><loc>https://peeljobs.com/"
            + "fresher-jobs-in-"
            + str(state.slug)
            + "/"
            + end_url
        )
    states_jobs_xml_count = states_jobs_xml_count + "</urlset>"
    states_jobs_xml_file = open("sitemap/sitemap-state-jobs.xml", "w")
    states_jobs_xml_file.write(states_jobs_xml_count)
    states_walkins_xml_count = states_walkins_xml_count + "</urlset>"
    states_walkins_xml_file = open("sitemap/sitemap-state-walkins.xml", "w")
    states_walkins_xml_file.write(states_walkins_xml_count)
    states_fresher_jobs_xml_count = states_fresher_jobs_xml_count + "</urlset>"
    states_fresher_jobs_xml_file = open(
        "sitemap/sitemap-state-fresher-jobs.xml", "w"
    )
    states_fresher_jobs_xml_file.write(states_fresher_jobs_xml_count)

    # skill fresher jobs
    skills_fresher_xml_cont = xml_cont
    no_job_skills_fresher_xml_cont = xml_cont

    for skill in skills:
        jobs = JobPost.objects.filter(status="Live", skills=skill, min_year=0).count()
        if jobs > 0:
            skills_fresher_xml_cont = (
                skills_fresher_xml_cont
                + "<url><loc>https://peeljobs.com/"
                + str(skill.slug)
                + "-fresher-jobs/"
                + end_url
            )
        else:
            no_job_skills_fresher_xml_cont = (
                no_job_skills_fresher_xml_cont
                + "<url><loc>https://peeljobs.com/"
                + str(skill.slug)
                + "-fresher-jobs/"
                + end_url
            )
    skills_fresher_xml_cont = skills_fresher_xml_cont + "</urlset>"
    no_job_skills_fresher_xml_cont = no_job_skills_fresher_xml_cont + "</urlset>"

    skills_fresher_xml_file = open("sitemap/sitemap-skill-fresher-jobs.xml", "w")
    skills_fresher_xml_file.write(skills_fresher_xml_cont)
    no_job_skills_fresher_xml_file = open(
        "sitemap/sitemap-skill-without-fresher-jobs.xml", "w"
    )
    no_job_skills_fresher_xml_file.write(no_job_skills_fresher_xml_cont)

    # Educations jobs
    educations = Qualification.objects.filter(status="Active")
    educations_xml_cont = xml_cont

    for edu in educations:
        educations_xml_cont = (
            educations_xml_cont
            + "<url><loc>https://peeljobs.com/"
            + str(edu.slug)
            + "-jobs/"
            + end_url
        )
    educations_xml_cont = educations_xml_cont + "</urlset>"

    educations_xml_file = open("sitemap/sitemap-education-jobs.xml", "w")
    educations_xml_file.write(educations_xml_cont)

    # recruiters
    recruiters_xml_cont = xml_cont

    recruiters = User.objects.filter(
        Q(user_type="RR") | Q(user_type="AR") | Q(user_type="AA") & Q(is_active=True)
    )
    for recruiter in recruiters:
        recruiters_xml_cont = (
            recruiters_xml_cont
            + "<url><loc>https://peeljobs.com/recruiters/"
            + str(recruiter.username)
            + "/"
            + end_url
        )

    recruiters_xml_cont = recruiters_xml_cont + "</urlset>"

    recruiter_xml_file = open("sitemap/sitemap-recruiters.xml", "w")
    recruiter_xml_file.write(
        recruiters_xml_cont.encode("ascii", "ignore").decode("ascii")
    )

    # companies
    companies_xml_cont = xml_cont

    companies = Company.objects.filter(is_active=True)
    for company in companies:
        companies_xml_cont = (
            companies_xml_cont
            + "<url><loc>https://peeljobs.com/"
            + str(company.slug)
            + "-job-openings/"
            + end_url
        )
    companies_xml_cont = companies_xml_cont + "</urlset>"

    companies_xml_file = open("sitemap/sitemap-companies.xml", "w")
    companies_xml_file.write(companies_xml_cont)

    # pages
    pages_xml_cont = xml_cont
    full_jobposts = JobPost.objects.filter(status="Live", job_type="full-time")
    internships = JobPost.objects.filter(status="Live", job_type="internship")
    walk_ins = JobPost.objects.filter(status="Live", job_type="walk-in")
    government_jobs = JobPost.objects.filter(status="Live", job_type="government")
    jobposts = list(chain(full_jobposts, internships, walk_ins, government_jobs))
    items_per_page = 100
    no_pages = int(math.ceil(float(len(jobposts)) / items_per_page))

    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/sitemap/" + end_url
    )

    for each in range(1, no_pages):
        pages_xml_cont = (
            pages_xml_cont
            + "<url><loc>https://peeljobs.com/sitemap/"
            + str(each)
            + "/"
            + end_url
        )

    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/post-job/" + end_url
    )

    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/internship-jobs/" + end_url
    )
    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/government-jobs/" + end_url
    )
    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/full-time-jobs/" + end_url
    )
    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/walkin-jobs/" + end_url
    )

    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/alert/list/" + end_url
    )

    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/jobs-by-location/" + end_url
    )
    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/jobs-by-skill/" + end_url
    )
    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/jobs-by-industry/" + end_url
    )

    pages_xml_cont = (
        pages_xml_cont
        + "<url><loc>https://peeljobs.com/calendar/"
        + str(datetime.now().year)
        + "/"
        + end_url
    )
    pages_xml_cont = (
        pages_xml_cont
        + "<url><loc>https://peeljobs.com/calendar/"
        + str(datetime.now().year)
        + "/month/"
        + str(datetime.now().month)
        + "/"
        + end_url
    )

    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/page/about-us/" + end_url
    )
    pages_xml_cont = (
        pages_xml_cont
        + "<url><loc>https://peeljobs.com/page/terms-conditions/"
        + end_url
    )
    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/page/privacy-policy/" + end_url
    )
    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/page/contact-us/" + end_url
    )
    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/page/faq/" + end_url
    )
    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/page/recruiter-faq/" + end_url
    )
    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/recruiters/" + end_url
    )
    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/companies/" + end_url
    )
    pages_xml_cont = pages_xml_cont + "<url><loc>https://peeljobs.com/jobs/" + end_url
    pages_xml_cont = (
        pages_xml_cont
        + "<url><loc>https://peeljobs.com/fresher-jobs-by-skills/"
        + end_url
    )
    pages_xml_cont = (
        pages_xml_cont
        + "<url><loc>https://peeljobs.com/walkin-jobs-by-skills/"
        + end_url
    )
    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/walkins-by-location/" + end_url
    )
    pages_xml_cont = (
        pages_xml_cont + "<url><loc>https://peeljobs.com/jobs-by-degree/" + end_url
    )
    pages_xml_cont = (
        pages_xml_cont
        + "<url><loc>https://peeljobs.com/fresher-jobs-by-location/"
        + end_url
    )

    pages_xml_cont = pages_xml_cont + "</urlset>"

    pages_xml_file = open("sitemap/sitemap-pages.xml", "w")
    pages_xml_file.write(pages_xml_cont)

    directory = settings.BASE_DIR + "/sitemap/"

    xml_cont = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">"""

    end_url = "</loc><changefreq>daily</changefreq><priority>0.5</priority></url>"

    xml_cont = (
        xml_cont
        + "<url><loc>https://peeljobs.com/</loc>"
        + "<changefreq>always</changefreq><priority>1.0</priority></url>"
    )
    for d in os.listdir(directory):
        if d.endswith(".xml") and not d.endswith("sitemap.xml"):
            xml_cont = (
                xml_cont + "<url><loc>https://peeljobs.com/sitemap/" + str(d) + end_url
            )

    xml_cont = xml_cont + "</urlset>"
    sitemap_xml_file = open("sitemap/sitemap.xml", "w")
    sitemap_xml_file.write(xml_cont)
    print("Sitemap Generation ended")


@app.task()
def save_search_results(ip_address, data, results, user):
    user = User.objects.filter(id=user).first()
    search_result = SearchResult.objects.create(ip_address=ip_address)
    skills = data.get("q", "").strip(", ")
    locations = data.get("location", "").strip(", ")
    search_result.search_text = {"skills": skills, "locations": locations}
    if skills:
        search_skills = skills.split(", ")
        for skill in search_skills:
            skills = Skill.objects.filter(Q(slug__iexact=skill) | Q(name__iexact=skill))
            if skills:
                search_result.skills.add(skills[0].id)
            else:
                search_result.other_skill += (
                    "," + skill if search_result.other_skill else skill
                )
    if locations:
        serch_locations = locations.split(", ")
        for loc in serch_locations:
            location = City.objects.filter(Q(slug__iexact=loc) | Q(name__iexact=loc))
            if location:
                search_result.locations.add(location[0].id)
            else:
                search_result.other_location += (
                    "," + loc if search_result.other_location else loc
                )
    if user:
        search_result.user = user
    search_result.job_post = results
    search_result.save()
