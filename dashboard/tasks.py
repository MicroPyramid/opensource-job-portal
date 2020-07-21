import json
import math
import urllib
import requests
from datetime import datetime, timedelta
from functools import reduce
from itertools import chain
from operator import __or__ as OR
from bs4 import BeautifulSoup

from celery.task import task
from django.conf import settings

# from pytz import timezone
from django.db.models import Q, F
from django.template import loader, Template, Context
from django_blog_it.django_blog_it.models import Category, Post, Tags
from django.db.models import Case, When
from microurl import google_mini
from twython.api import Twython

from mpcomp.facebook import GraphAPI, get_app_access_token
from mpcomp.views import Memail, get_absolute_url, mongoconnection
from peeldb.models import (
    AppliedJobs,
    City,
    Company,
    User,
    Facebook,
    FacebookGroup,
    FacebookPage,
    FacebookPost,
    Industry,
    JobAlert,
    JobPost,
    Linkedin,
    LinkedinPost,
    Qualification,
    SearchResult,
    SentMail,
    Skill,
    Subscriber,
    TechnicalSkill,
    Ticket,
    Twitter,
    TwitterPost,
    State,
)

db = mongoconnection()


@task
def rebuilding_index():
    from haystack.management.commands import rebuild_index

    rebuild_index.Command().handle(interactive=False)


@task
def updating_jobposts():
    jobposts = JobPost.objects.filter(status="Live")
    for job in jobposts:
        job_url = get_absolute_url(job)
        job.slug = get_absolute_url(job)
        job.save()


@task
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
            mfrom = settings.DEFAULT_FROM_EMAIL
            user_active = True if user.is_active else False
            Memail(mto, mfrom, subject, rendered, user_active)


@task
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
            mfrom = settings.DEFAULT_FROM_EMAIL
            user_active = False
            Memail(mto, mfrom, subject, rendered, user_active)


@task
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
            mfrom = settings.DEFAULT_FROM_EMAIL
            user_active = False
            Memail(mto, mfrom, subject, rendered, user_active)


@task()
def jobpost_published():
    jobposts = JobPost.objects.filter(status="Published")
    for job in jobposts:
        # asia_timezone = timezone(settings.TIMEZONE)
        # asia_time = datetime.now(asia_timezone).strftime('%Y-%m-%d %H:%M:%S')

        # current_date = datetime.strptime(
        #     str(datetime.now().date()), "%Y-%m-%d").strftime("%Y-%m-%d")
        # job_date = job.published_date
        # if str(job.last_date) >= str(current_date):
        # if str(job_date) == str(asia_time) or str(job_date) <=
        # str(asia_time):
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
            # need to check this condition
            # if emp['peelfbpost']:
            posts = FacebookPost.objects.filter(
                job_post=job,
                page_or_group="group",
                is_active=True,
                post_status="Deleted",
            )
            for group in job.fb_groups:
                fb_group = FacebookGroup.objects.get(user=job.user, group_id=group)
                postongroup(job.id, fb_group.id)
                # need to get accetoken for peeljobs twitter
                # page
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
        mfrom = settings.DEFAULT_FROM_EMAIL
        Memail(mto, mfrom, subject, t.render(c), True if job.user.is_active else False)

        user_technical_skills = TechnicalSkill.objects.filter(
            skill__in=job.skills.all().values_list("id", flat=True)
        )
        users = User.objects.filter(user_type="JS", skills__in=user_technical_skills)
        for user in users:
            if not AppliedJobs.objects.filter(user=user, job_post=job):
                AppliedJobs.objects.create(
                    user=user,
                    job_post=job,
                    status="Pending",
                    ip_address="",
                    user_agent="",
                )


def del_jobpost_fb(user, post):
    if user:
        graph = GraphAPI(settings.FB_DEL_ACCESS_TOKEN)
        try:
            post.post_status = "Deleted"
            post.save()
            # urllib.urlopen('https://graph.facebook.com/postid_user[id]?access_token=accesstoken')
            graph.delete_object(post.post_id)
            return "deleted successfully"
        except Exception as e:
            return e
    else:
        return "connect to fb"


@task()
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
            # params = urllib.urlencode(params)
            facebook_id = Facebook.objects.get(user=user).facebook_id
            # response = urllib.urlopen("https://graph.facebook.com/" + facebook_id + "/feed", params).read()
            # response = json.loads(response)

            # params = urllib.parse.urlencode(params)
            # response = urllib.urlopen("https://graph.facebook.com/" + settings.FB_PEELJOBS_PAGEID + "/feed", params).read()
            u = requests.post(
                "https://graph.facebook.com/" + facebook_id + "/feed", params=params
            )
            response = u.json()

            if "error" in response.keys():
                # found error, we need to log it for review.
                pass
            if "id" in response.keys():
                FacebookPost.objects.create(
                    job_post=job_post,
                    page_or_group="page",
                    page_or_group_id=facebook_id,
                    post_id=response["id"],
                    post_status="Posted",
                )
                # db.Jobpost.update({'id':jid},{'$set':{'pfb':{'status':True,'post_id':response['id']}}})
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
        # response = urllib.urlopen("https://graph.facebook.com/" + settings.FB_PEELJOBS_PAGEID + "/feed", params).read()
        u = requests.post(
            "https://graph.facebook.com/" + settings.FB_PEELJOBS_PAGEID + "/feed",
            params=params,
        )
        response = u.json()
        print(params)
        print(response, "response")
        # response = json.loads(response)
        if "error" in response.keys():
            # found error, we need to log it for review.
            pass
        if "id" in response.keys():
            FacebookPost.objects.create(
                job_post=job_post,
                page_or_group="peel_jobs",
                page_or_group_id=settings.FB_PEELJOBS_PAGEID,
                post_id=response["id"],
                post_status="Posted",
            )
            # db.Jobpost.update({'id':jid},{'$set':{'peelfbpost':response['id']}})
            return "posted successfully"
        return "job not posted on page"
    else:
        return "jobpost not exists"


@task()
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
            # params = urllib.urlencode(params)
            params = urllib.parse.urlencode(params)

            for page in pages:
                if page.allow_post:
                    u = requests.post(
                        "https://graph.facebook.com/" + str(page.page_id) + "/feed",
                        params,
                        params=params,
                    )
                    response = u.json()

                    # if 'error' in response.keys():
                    # if response['error']['code'] == 190 and response['error']['error_subcode'] == 460:
                    # need to evaluate this condition
                    # pass
                    # db.Employer.update({'email':user['email']},{'$unset':{'facebook':1,'fb':1,'fb_url':1}})
                    if "id" in response.keys():
                        FacebookPost.objects.create(
                            job_post=job_post,
                            page_or_group=page,
                            page_or_group_id=page.page_id,
                            post_id=response["id"],
                            post_status="Posted",
                        )

                        # db.Jobpost.update({'id':jid},{'$push':{'pfb.pages':{'status':True,'post_id':response['id'],'pageid':page['id']}}})
            data = "posted successfully"
        else:
            data = "page not exists"
    else:
        data = "user not connected to facebook"
    return data


@task()
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
        # from django.utils.html import strip_tags
        # description = strip_tags(job_post.description)
        params["description"] = job_post.company_name
        params["access_token"] = settings.FB_GROUP_ACCESS_TOKEN
        params["actions"] = [{"name": "get peeljobs", "link": settings.PEEL_URL}]
        params = urllib.parse.urlencode(params)
        # response = urllib.urlopen("https://graph.facebook.com/" + str(group.group_id) + "/feed", params).read()
        # response = json.loads(response)
        requests.post(
            "https://graph.facebook.com/" + str(group_id) + "/feed", params=params
        )
        # response = u.json()
        # if 'id' in response.keys():
        #     FacebookPost.objects.create(job_post=job_post, page_or_group='group', page_or_group_id=group.group_id, post_id=response[
        #                                 'id'], post_status='Posted', is_active=is_active)

        # db.Jobpost.update({'id':jid},{'$push':{'pfb.groups':{'status':True,'post_id':response['id'],'groupid':group['id']}}})
        return "posted successfully"
    else:
        return "jobpost not exists"


@task
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
            # from django.utils.html import strip_tags
            # description = strip_tags(job_post.description)
            params["description"] = job_post.company_name
            params["access_token"] = settings.FB_ALL_GROUPS_TOKEN
            params["actions"] = [{"name": "get peeljobs", "link": settings.PEEL_URL}]
            params = urllib.parse.urlencode(params)
            # response = urllib.urlopen("https://graph.facebook.com/" + str(group.group_id) + "/feed", params).read()
            # response = json.loads(response)
            requests.post(
                "https://graph.facebook.com/" + str(group_id) + "/feed", params=params
            )
            # response = u.json()
            # if 'id' in response.keys():
            #     FacebookPost.objects.create(job_post=job_post, page_or_group='group', page_or_group_id=group.group_id, post_id=response[
            #                                 'id'], post_status='Posted', is_active=is_active)

            # db.Jobpost.update({'id':jid},{'$push':{'pfb.groups':{'status':True,'post_id':response['id'],'groupid':group['id']}}})


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


@task()
def del_jobpost_peel_fb(user, post):
    if user:
        try:
            graph = GraphAPI(settings.FB_ACCESS_TOKEN)
            post = FacebookPost.objects.get(id=post)
            post.post_status = "Deleted"
            post.save()
            # urllib.urlopen('https://graph.facebook.com/postid_user[id]?access_token=accesstoken')
            graph.delete_object(post.post_id)
        except:
            print("not deleted")
        return "deleted successfully"
    return "connect to fb"


@task()
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
        # db.Jobpost.update({'id':jid},{'$set':{'pln':{'status':False}}})
    else:
        return "jobpost not exists"


@task()
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
        job_name = job_name + skill_hash + loc_hash + " @Jobs @PeelJobs"
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

            # db.Jobpost.update({'id':jid},{'$set':{'ptw':{'status':True,'post_id':response['id']}}})
            return "posted successfully"
        return "not posted in twitter"
    else:
        return "jobpost not exists"


@task()
def sending_mail(emailtemplate, recruiters):
    t = loader.get_template("email/email_template.html")
    c = {"text": emailtemplate.message}
    subject = emailtemplate.subject
    rendered = t.render(c)
    mfrom = settings.DEFAULT_FROM_EMAIL
    sent_mail = SentMail.objects.create(template=emailtemplate)
    recruiters = User.objects.filter(id__in=recruiters)
    for recruiter in recruiters:
        recruiter = User.objects.get(id=recruiter)
        sent_mail.recruiter.add(recruiter)
        mto = recruiter.email
        user_active = True if recruiter.is_active else False
        Memail(mto, mfrom, subject, rendered, user_active)
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


@task()
def applicants_notifications():

    current_date = datetime.strptime(
        str(datetime.now().date() - timedelta(days=10)), "%Y-%m-%d"
    ).strftime("%Y-%m-%d")
    today_applicants = User.objects.filter(
        email_notifications=True,
        profile_updated__lte=current_date,
        profile_completeness__lte=50,
        user_type="JS",
        is_bounce=False,
        is_unsubscribe=False,
    )
    for user in today_applicants:
        conditions = get_conditions(user)
        if conditions:
            jobposts = (
                JobPost.objects.filter(reduce(OR, conditions))
                .filter(status="Live")
                .distinct()[:10]
            )
        else:
            jobposts = JobPost.objects.filter(status="Live")[:10]
        # sending an email
        c = {"job_posts": jobposts, "user": user}
        t = loader.get_template("email/applicant.html")
        subject = "Update Your Profile To Get Top Matching Jobs - PeelJobs"
        rendered = t.render(c)
        mto = [user.email]
        mfrom = settings.DEFAULT_FROM_EMAIL
        user_active = True if user.is_active else False
        Memail(mto, mfrom, subject, rendered, user_active)


# sending mail to recruiters about applicants
@task()
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
                    mfrom = settings.DEFAULT_FROM_EMAIL
                    user_active = True if each.is_active else False
                    Memail(mto, mfrom, subject, rendered, user_active)


@task()
def send_dailyapplicantnotifications():
    import datetime as dt

    current_hour = dt.datetime.now().hour
    current_date = dt.datetime.strptime(
        str(dt.datetime.now().date()), "%Y-%m-%d"
    ).strftime("%Y-%m-%d")
    daily_emails_count = db.users.find(
        {"date": current_date, "mail_sent": True}
    ).count()
    users = list(
        db.users.find(
            {
                "$and": [
                    {"email": {"$ne": ""}},
                    {"location": {"$ne": ""}},
                    {"hash_code": {"$exists": True}},
                    {"mail_sent": False},
                    {"unsubscribe": {"$exists": False}},
                ]
            }
        )
    )
    if current_hour >= 9 and current_hour <= 18:
        if daily_emails_count <= 100000:
            # skill = Skill.objects.get(slug='java')
            # job_posts = JobPost.objects.filter(
            #     status='Live', skills__in=[skill])[:10]
            count = 0
            import smtplib
            import email.utils
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            servername = "192.99.18.119"
            username = "admin"
            password = "peel123"
            server = smtplib.SMTP(servername, 2525)
            server.ehlo()

            try:
                # server.set_debuglevel(True)
                # identify ourselves, prompting server for supported features
                # If we can encrypt this SESSION_ENGINE = '', do it
                if server.has_extn("STARTTLS"):
                    server.starttls()
                    server.ehlo()  # re-identify ourselves over TLS connection
                server.login(username, password)
                for user in users:
                    count = count + 1
                    if count == 2273:
                        break
                    each_email = user["email"]
                    c = {
                        "name": "",
                        "email": each_email,
                        "message_id": user["hash_code"],
                    }
                    t = loader.get_template("email/applicant_mail_connect.html")
                    subject = "Peeljobs  - The Best Job Portal"
                    rendered = t.render(c)
                    # Create the message
                    msg = MIMEMultipart("alternative")
                    msg["To"] = email.utils.formataddr((each_email, each_email))
                    msg["From"] = email.utils.formataddr(
                        ("Peeljobs Support", "info@peelster.in")
                    )
                    msg["Subject"] = subject
                    msg["Return-Path"] = email.utils.formataddr(
                        ("Peeljobs Support", "bounce@bounce.peeljobs.com")
                    )
                    msg["Errors-To"] = email.utils.formataddr(
                        ("Peeljobs Support", "bounce@bounce.peeljobs.com")
                    )
                    msg["reply-to"] = email.utils.formataddr(
                        ("Peeljobs Support", "support@peeljobs.com")
                    )
                    import arrow
                    import time

                    today = (
                        arrow.utcnow().to("Asia/Calcutta").format("DD.MM.YYYY HH:mm:ss")
                    )
                    pattern = "%d.%m.%Y %H:%M:%S"
                    epoch = int(time.mktime(time.strptime(today, pattern)))
                    message_id = (
                        "<" + str(user["hash_code"]) + str(epoch) + "@peeljobs.com>"
                    )
                    msg["Message-ID"] = message_id
                    msg["Date"] = email.utils.formatdate(localtime=True)
                    msg.add_header(
                        "List-Unsubscribe",
                        "<mailto:support@peeljobs.com>, <https://peeljobs.com/unsubscribe/nikhila@micropyramid.com/>",
                    )
                    text = """IF THE FIRST STEP OF YOUR CAREER GOES RIGHT,
                            THEN REST OF YOUR CAREER WILL BE BRIGHT
                            CONNECT WITH ANY OF YOUR SOCIAL NETWORKING SITES TO GET HIRED
                            Peeljobs-twitter
                            CONNECT HERE
                            Dear Member,
                            Greetings from Peeljobs!
                            Peeljobs is one of the best job portal website. Where you can search jobs by skill, location, industry, functional area etc.
                            You no need to register into our website.
                            You can log in with your existing social networking sites like Facebook, Google+, Linkedin, Github with one click.
                            Here are few techniques to get into a challenging career.
                            Get job alerts
                            Create job alerts to get opportunities that interest you.
                            So, that you are always first to hear about the jobs that you really care/want about.
                            If you have any further queries, please mail to support@peeljobs.com
                            We are happy to help you.
                            Login/Connect Internship jobs View All Jobs Job Alert FAQs
                            Developed by Micropyramid.comUnsubscribe"""
                    part1 = MIMEText(text, "plain")
                    part2 = MIMEText(rendered, "html")
                    msg.attach(part1)
                    msg.attach(part2)
                    server.sendmail(
                        "bounce@bounce.peeljobs.com", [each_email], msg.as_string()
                    )
                    db.users.update(
                        {"email": each_email},
                        {"$set": {"mail_sent": True, "date": current_date}},
                        False,
                        True,
                    )
            finally:
                server.quit()


@task()
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

    today_mobile_verified_recruiters = today_recruiters_count.filter(
        mobile_verified=True
    )
    today_mobile_not_verified_recruiters = today_recruiters_count.filter(
        mobile_verified=False
    )

    today_agency_recruiters_count = User.objects.filter(
        date_joined__contains=current_date, user_type="AA"
    )

    today_agency_active_recruiters = today_agency_recruiters_count.filter(
        is_active=True
    )
    today_agency_inactive_recruiters = today_agency_recruiters_count.filter(
        is_active=False
    )

    today_mobile_verified_agency_recruiters = today_agency_recruiters_count.filter(
        mobile_verified=True
    )
    today_mobile_not_verified_agency_recruiters = today_agency_recruiters_count.filter(
        mobile_verified=False
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
        "today_mobile_verified_recruiters": today_mobile_verified_recruiters.count(),
        "today_mobile_not_verified_recruiters": today_mobile_not_verified_recruiters.count(),
        "today_agency_recruiters_count": today_agency_recruiters_count.count(),
        "today_agency_active_recruiters": today_agency_active_recruiters.count(),
        "today_agency_inactive_recruiters": today_agency_inactive_recruiters.count(),
        "today_mobile_verified_agency_recruiters": today_mobile_verified_agency_recruiters.count(),
        "today_mobile_not_verified_agency_recruiters": today_mobile_not_verified_agency_recruiters.count(),
    }
    db.statistics.insert(data)
    users = [
        "nikhila@micropyramid.com",
        "vineesha@micropyramid.com",
        "raghubethi@micropyramid.com",
        "anusha@micropyramid.com",
        "kamal.seo@gmail.com",
        "ashwin@micropyramid.com",
    ]

    for each in users:
        temp = loader.get_template("email/daily_report.html")
        subject = "Peeljobs Daily Report For " + formatted_date
        mto = [each]
        mfrom = settings.DEFAULT_FROM_EMAIL
        rendered = temp.render(data)
        Memail(mto, mfrom, subject, rendered, True)


@task()
def applicants_profile_update_notifications_two_hours():
    today_applicants = User.objects.filter(
        user_type="JS",
        profile_completeness__lt=50,
        is_unsubscribe=False,
        is_bounce=False,
        email_notifications=True,
    ).exclude(email__icontains="micropyramid.com")
    for user in today_applicants:
        if user.date_joined and user.date_joined > datetime.today() - timedelta(
            hours=2
        ):
            temp = loader.get_template("email/user_profile_alert.html")
            subject = "Update Your Profile To Get Top Matching Jobs - Peeljobs"
            mto = [user.email]
            mfrom = settings.DEFAULT_FROM_EMAIL
            rendered = temp.render({"user": user})
            user_active = True if user.is_active else False
            Memail(mto, mfrom, subject, rendered, user_active)


@task()
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
            mfrom = settings.DEFAULT_FROM_EMAIL
            rendered = temp.render({"user": each, "job_posts": job_posts})
            user_active = True if each.is_active else False
            Memail([each.email], mfrom, subject, rendered, user_active)
    recruiters = User.objects.filter(
        Q(Q(user_type="RR") | Q(user_type="AA"))
        & Q(
            email_notifications=True,
            is_unsubscribe=False,
            is_bounce=False,
            is_active=False,
        )
    )
    for user in recruiters:
        days = (datetime.today() - user.date_joined).days
        if days == 2 or days % 10 == 0:
            temp = loader.get_template("email/account_inactive.html")
            subject = "Update Your Profile - Peeljobs"
            mfrom = settings.DEFAULT_FROM_EMAIL
            rendered = temp.render({"user": user})
            Memail([user.email], mfrom, subject, rendered, False)
    inactive_users = User.objects.filter(
        is_unsubscribe=False,
        email_notifications=True,
        is_bounce=False,
        is_active=False,
        user_type="JS",
    )
    for user in inactive_users:
        days = (datetime.today() - user.date_joined).days
        if days % 7 == 0:
            temp = loader.get_template("email/account_inactive.html")
            subject = "Verify your Email Address - Peeljobs"
            mfrom = settings.DEFAULT_FROM_EMAIL
            rendered = temp.render({"user": user})
            Memail([user.email], mfrom, subject, rendered, False)
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
        mfrom = settings.DEFAULT_FROM_EMAIL
        rendered = temp.render({"user": user, "resume_update": True})
        user_active = True if user.is_active else False
        Memail([user.email], mfrom, subject, rendered, user_active)


@task()
def applicants_walkin_job_notifications():

    today_applicants = User.objects.filter(
        user_type="JS", is_unsubscribe=False, is_bounce=False, email_notifications=True
    )
    for each in today_applicants:
        job_posts = each.related_walkin_jobs()
        temp = loader.get_template("email/applicant.html")
        subject = "Latest Walkin Jobs - Peeljobs"
        mto = [each.email]
        mfrom = settings.DEFAULT_FROM_EMAIL
        c = {"job_posts": job_posts[:10], "user": each, "walk_in": True}
        rendered = temp.render(c)
        user_active = True if each.is_active else False
        Memail(mto, mfrom, subject, rendered, user_active)


@task()
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
        mfrom = settings.DEFAULT_FROM_EMAIL
        rendered = temp.render({"user": recruiter, "recruiter": True})
        user_active = True if recruiter.is_active else False
        Memail(mto, mfrom, subject, rendered, user_active)


@task()
def applicants_all_job_notifications():

    today_applicants = User.objects.filter(
        user_type="JS", is_unsubscribe=False, is_bounce=False, email_notifications=True
    )

    for each in today_applicants:
        job_posts = each.related_jobs()
        temp = loader.get_template("email/applicant.html")
        subject = "Top matching jobs for you - Peeljobs"
        mto = [each.email]
        mfrom = settings.DEFAULT_FROM_EMAIL
        rendered = temp.render({"job_posts": job_posts[:10], "user": each})
        user_active = True if each.is_active else False
        Memail(mto, mfrom, subject, rendered, user_active)


@task()
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
        mfrom = settings.DEFAULT_FROM_EMAIL
        rendered = temp.render({"jobposts": job_posts[:10], "user": user})
        user_active = True if user.is_active else False
        Memail(mto, mfrom, subject, rendered, user_active)
    users = User.objects.filter(
        user_type="JS", email_notifications=True, is_unsubscribe=False, is_bounce=False
    )
    users = users.filter(
        Q(facebook_user__isnull=True)
        | Q(google_user__isnull=True)
        | Q(linkedin__isnull=True)
        | Q(twitter__isnull=True)
    )
    for user in users:
        temp = loader.get_template("email/social_connect.html")
        subject = "Social Connect - Peeljobs"
        mto = [user.email]
        mfrom = settings.DEFAULT_FROM_EMAIL
        rendered = temp.render({"user": user})
        user_active = True if user.is_active else False
        Memail(mto, mfrom, subject, rendered, user_active)


@task()
def alerting_applicants():
    date = (datetime.today() - timedelta(days=7)).date()
    users = User.objects.filter(
        user_type="JS",
        email_notifications=True,
        is_unsubscribe=False,
        is_bounce=False,
        last_login__icontains=date,
    )
    for user in users:
        temp = loader.get_template("email/user_profile_alert.html")
        subject = "Update Your Profile To Get Top Matching Jobs - PeelJobs"
        mto = [user.email]
        mfrom = settings.DEFAULT_FROM_EMAIL
        rendered = temp.render({"user": user, "inactive_user": True})
        user_active = True if user.is_active else False
        Memail(mto, mfrom, subject, rendered, user_active)
    recruiters = User.objects.filter(
        Q(Q(user_type="RR") | Q(user_type="AA"))
        & Q(
            email_notifications=True,
            is_unsubscribe=False,
            is_bounce=False,
            last_login__icontains=date,
        )
    )
    for recruiter in recruiters:
        temp = loader.get_template("email/user_profile_alert.html")
        subject = "Update Your Profile To Post Unlimited Jobs - PeelJobs"
        mto = [recruiter.email]
        mfrom = settings.DEFAULT_FROM_EMAIL
        rendered = temp.render(
            {"user": recruiter, "recruiter": True, "inactive_user": True}
        )
        user_active = True if recruiter.is_active else False
        Memail(mto, mfrom, subject, rendered, user_active)
    # Sending Birthday Wishes
    current_date = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").strftime(
        "%m-%d"
    )
    users = User.objects.filter(dob__icontains=current_date)
    for user in users:
        temp = loader.get_template("email/birthdays.html")
        subject = (
            "=?UTF-8?Q?=F0=9F=8E=82?="
            + " Birthday Wishes - Peeljobs "
            + "=?UTF-8?Q?=F0=9F=8E=82?="
        )
        mfrom = settings.DEFAULT_FROM_EMAIL
        rendered = temp.render({"user": user})
        user_active = True if user.is_active else False
        Memail(user.email, mfrom, subject, rendered, user_active)


@task()
def send_weekly_login_notifications():
    today_applicants = User.objects.filter(
        user_type="JS", is_unsubscribe=False, is_bounce=False, email_notifications=True
    )
    for each in today_applicants:
        job_posts = each.related_jobs()

        temp = loader.get_template("email/applicant.html")
        subject = "Latest Walkin Jobs - Peeljobs"
        mto = [each.email]
        mfrom = settings.DEFAULT_FROM_EMAIL
        rendered = temp.render({"user": each, "job_posts": job_posts[:10]})
        user_active = True if each.is_active else False
        Memail(mto, mfrom, subject, rendered, user_active)


# def know_organic_status():
#     db = mongoconnection()
#     users = User.objects.filter(user_type='JS')
#     count = 0
#     for user in users:
#         check_users = list(db.users.find({'email': user.email}))
#         if len(check_users) > 0:
#             count = count + 1
#             db.users.update({'email': user.email}, {'$set': {'pj_connected': True}}, False, True)

#     print (count)


@task()
def sending_mobile_campaign():
    users = list(
        db.users.find(
            {
                "$and": [
                    {"mobile": {"$ne": ""}},
                    {"location": "Hyderabad"},
                    {"sms_campaign_sent": {"$exists": False}},
                ]
            }
        )
    )
    count = 0
    current_date = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").strftime(
        "%Y-%m-%d"
    )

    for user in users:
        if count == 3001:
            break
        mobile = user["mobile"]
        message = """Top companies are looking for Java Developers!
                     Connect with us, to get placed https://peeljobs.com/java-fresher-jobs/
                     or https://goo.gl/SX4qbB"""
        SMS_AUTH_KEY = "4a905d1566e5e93bfff35aa56a38660"
        BULK_SMS_FROM = "PEELJB"
        requests.get(
            "http://sms.9sm.in/rest/services/sendSMS/sendGroupSms?AUTH_KEY="
            + str(SMS_AUTH_KEY)
            + "&message="
            + str(message)
            + "&senderId="
            + str(BULK_SMS_FROM)
            + "&routeId=3&mobileNos="
            + str(mobile)
            + "&smsContentType=english"
        )
        db.users.update(
            {"mobile": mobile},
            {"$set": {"sms_campaign_sent": True, "sms_date": current_date}},
            False,
            True,
        )
        count = count + 1


@task()
def sitemap_generation():
    import os

    os.system("rm ../sitemap/*")
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

    jobs_xml_file = open("../sitemap/sitemap-jobs.xml", "w")
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

    skills_xml_file = open("../sitemap/sitemap-skills.xml", "w")
    skills_xml_file.write(skills_xml_cont)
    if no_job_skills_xml_cont != xml_cont:
        no_job_skills_xml_cont = no_job_skills_xml_cont + "</urlset>"
        no_job_skills_xml_file = open("../sitemap/sitemap-skills-without-jobs.xml", "w")
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

    locations_xml_file = open("../sitemap/sitemap-locations.xml", "w")
    locations_xml_file.write(locations_xml_cont)
    if no_job_locations_xml_cont != xml_cont:
        no_job_locations_xml_cont = no_job_locations_xml_cont + "</urlset>"
        no_job_locations_xml_file = open(
            "../sitemap/sitemap-locations-without-jobs.xml", "w"
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

    indsutries_xml_file = open("../sitemap/sitemap-industries.xml", "w")
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

    internship_xml_file = open("../sitemap/sitemap-internships.xml", "w")
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

    skills_walkin_xml_file = open("../sitemap/sitemap-skill-walkins.xml", "w")
    skills_walkin_xml_file.write(skills_walkin_xml_cont)
    no_job_skills_walkin_xml_file = open(
        "../sitemap/sitemap-skill-without-walkins.xml", "w"
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
            "../sitemap/sitemap-skill-locations-" + str(index) + ".xml", "w"
        )
        skills_location_xml_file.write(skills_locations_xml_cont)
        no_job_skills_location_xml_file = open(
            "../sitemap/sitemap-skill-locations-without-jobs-" + str(index) + ".xml",
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
            "../sitemap/sitemap-skill-location-walkins-" + str(index) + ".xml", "w"
        )
        skills_location_walkins_xml_file.write(skills_locations_walkins_xml_cont)
        no_job_skills_location_walkins_xml_file = open(
            "../sitemap/sitemap-skill-location-without-walkins-" + str(index) + ".xml",
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
            "../sitemap/sitemap-skill-location-fresher-jobs-" + str(index) + ".xml", "w"
        )
        skills_location_fresher_xml_file.write(skills_location_fresher_xml_cont)

        no_job_skills_location_fresher_xml_file = open(
            "../sitemap/sitemap-skill-location-without-fresher-jobs-"
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
    locations_walkin_xml_file = open("../sitemap/sitemap-location-walkins.xml", "w")
    locations_walkin_xml_file.write(locations_walkin_xml_cont)

    no_job_locations_walkin_xml_cont = no_job_locations_walkin_xml_cont + "</urlset>"
    no_job_locations_walkin_xml_file = open(
        "../sitemap/sitemap-location-without-walkins.xml", "w"
    )
    no_job_locations_walkin_xml_file.write(no_job_locations_walkin_xml_cont)

    locations_fresher_jobs_xml_cont = locations_fresher_jobs_xml_cont + "</urlset>"
    locations_fresher_jobs_xml_file = open(
        "../sitemap/sitemap-location-fresher-jobs.xml", "w"
    )
    locations_fresher_jobs_xml_file.write(locations_fresher_jobs_xml_cont)
    no_job_locations_fresher_jobs_xml_cont = (
        no_job_locations_fresher_jobs_xml_cont + "</urlset>"
    )
    no_job_locations_fresher_jobs_xml_file = open(
        "../sitemap/sitemap-location-without-fresher-jobs.xml", "w"
    )
    no_job_locations_fresher_jobs_xml_file.write(no_job_locations_fresher_jobs_xml_cont)

    states = State.objects.filter(status="Enabled").exclude(state__name__in=F("name"))
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
    states_jobs_xml_file = open("../sitemap/sitemap-state-jobs.xml", "w")
    states_jobs_xml_file.write(states_jobs_xml_count)
    states_walkins_xml_count = states_walkins_xml_count + "</urlset>"
    states_walkins_xml_file = open("../sitemap/sitemap-state-walkins.xml", "w")
    states_walkins_xml_file.write(states_walkins_xml_count)
    states_fresher_jobs_xml_count = states_fresher_jobs_xml_count + "</urlset>"
    states_fresher_jobs_xml_file = open(
        "../sitemap/sitemap-state-fresher-jobs.xml", "w"
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

    skills_fresher_xml_file = open("../sitemap/sitemap-skill-fresher-jobs.xml", "w")
    skills_fresher_xml_file.write(skills_fresher_xml_cont)
    no_job_skills_fresher_xml_file = open(
        "../sitemap/sitemap-skill-without-fresher-jobs.xml", "w"
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

    educations_xml_file = open("../sitemap/sitemap-education-jobs.xml", "w")
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

    recruiter_xml_file = open("../sitemap/sitemap-recruiters.xml", "w")
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

    companies_xml_file = open("../sitemap/sitemap-companies.xml", "w")
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
    pages_xml_cont = pages_xml_cont + "<url><loc>https://peeljobs.com/blog/" + end_url
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

    pages_xml_file = open("../sitemap/sitemap-pages.xml", "w")
    pages_xml_file.write(pages_xml_cont)

    # blog categories
    blog_categories_xml_cont = xml_cont

    categories = Category.objects.filter(is_active=True)
    for category in categories:
        if Post.objects.filter(status="Published"):
            blog_categories_xml_cont = (
                blog_categories_xml_cont
                + "<url><loc>https://peeljobs.com/blog/category/"
                + category.slug
                + "/"
            )
            blog_categories_xml_cont = blog_categories_xml_cont + end_url

    tags = Tags.objects.filter()
    for tag in tags:
        if Post.objects.filter(tags__in=[tag], status="Published"):
            blog_categories_xml_cont = (
                blog_categories_xml_cont
                + "<url><loc>https://peeljobs.com/blog/tags/"
                + tag.slug
                + "/"
            )
            blog_categories_xml_cont = blog_categories_xml_cont + end_url

    dates = []
    for each_object in (
        Post.objects.filter(category__is_active=True, status="Published")
        .order_by("created_on")
        .values("created_on")
    ):
        for date in each_object.values():
            dates.append((date.year, date.month, 1))
    dates = list(set(dates))

    for each in dates:
        blog_categories_xml_cont = (
            blog_categories_xml_cont
            + "<url><loc>https://peeljobs.com/blog/"
            + str(each[0])
            + "/"
            + str(each[1])
            + "/"
        )
        blog_categories_xml_cont = blog_categories_xml_cont + end_url

    blog_categories_xml_cont = blog_categories_xml_cont + "</urlset>"

    blog_categories_xml_file = open("../sitemap/sitemap-blog-categories.xml", "w")
    blog_categories_xml_file.write(blog_categories_xml_cont)

    # blog categories
    blog_posts_xml_cont = xml_cont

    posts = Post.objects.filter(status="Published").order_by("-created_on")
    for post in posts:
        blog_posts_xml_cont = (
            blog_posts_xml_cont
            + "<url><loc>https://peeljobs.com/blog/"
            + post.slug
            + "/"
            + end_url
        )

    blog_posts_xml_cont = blog_posts_xml_cont + "</urlset>"

    blog_posts_xml_file = open("../sitemap/sitemap-blog-posts.xml", "w")
    blog_posts_xml_file.write(blog_posts_xml_cont)
    directory = settings.BASE_DIR + "/../sitemap/"
    # pages, blog categories, blog posts, resources.

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
    sitemap_xml_file = open("../sitemap/sitemap.xml", "w")
    sitemap_xml_file.write(xml_cont)


@task()
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


# @task()
# def request_logging(path, is_authenticated, view_func, view_args, view_kwargs, device, ip_address, stats):
#     import logging
#     logger = logging.getLogger("request-logging")

#     request_details = {}
#     try:
#         request_details['function_name'] = view_func.__module__ + "." + view_func.__name__
#     except:
#         pass
#     request_details['path'] = path
#     request_details['user_logged_in'] = is_authenticated
#     request_details['view_data'] = view_args
#     request_details['view_data_kwargs'] = view_kwargs
#     request_details['device'] = device
#     if 'Bot' in device:
#         request_details['bot'] = True
#     request_details['ip_address'] = ip_address
#     try:
#         request_details['total_time'] = ("%(total_time)0.3f") % stats
#     except:
#         request_details['total_time'] = 0
#     try:
#         request_details['user_cpu_time'] = ("%(utime)0.3f") % stats
#     except:
#         request_details['user_cpu_time'] = 0
#     try:
#         request_details['system_cpu_time'] = ("%(stime)0.3f") % stats
#     except:
#         request_details['system_cpu_time'] = 0

#     request_jsonized = json.dumps(request_details)
# logger.debug(request_jsonized)


@task()
def handle_sendgrid_bounces():
    bounces = requests.get(
        "https://api.sendgrid.com/api/bounces.get.json?api_user="
        + settings.SG_USER
        + "&api_key="
        + settings.SG_PWD
    )
    for each in bounces.json():
        user = User.objects.filter(email=each["email"]).first()
        if user:
            user.is_bounce = True
            user.save()
        user = db.users.update({"email": each["email"]}, {"$set": {"is_bounce": True}})


def sending_mails_to_applicants_sendgrid():
    users = list(
        db.users.find(
            {
                "$and": [
                    {"email": {"$ne": ""}},
                    {"is_bounce": {"$exists": False}},
                    {"unsubscribe": {"$exists": False}},
                ]
            }
        )
    )
    i = 0
    for user in users:
        if i <= 10000:
            if user and "email" in user.keys():
                pj_user = User.objects.filter(email=user["email"])
                if not pj_user:
                    i = i + 1
                    temp = loader.get_template("email/register_invite.html")
                    subject = "Register With Us - Peeljobs"
                    mfrom = settings.DEFAULT_FROM_EMAIL
                    rendered = temp.render({"user": user})
                    Memail(user["email"], mfrom, subject, rendered, False)


@task()
def check_meta_data():
    host_name = "https://peeljobs.com"

    urls = [
        {"url": host_name + "/", "name": "home_page"},
        {"url": host_name + "/java-jobs/", "name": "skill_jobs"},
        {"url": host_name + "/bcom-jobs/", "name": "education_jobs"},
        {"url": host_name + "/java-bcom-jobs/", "name": "skill_education_jobs"},
        {"url": host_name + "/java-walkins/", "name": "skill_walkin_jobs"},
        {"url": host_name + "/jobs-in-bangalore/", "name": "location_jobs"},
        {"url": host_name + "/walkins-in-bangalore/", "name": "location_walkin_jobs"},
        {"url": host_name + "/java-jobs-in-bangalore/", "name": "skill_location_jobs"},
        {
            "url": host_name + "/java-walkins-in-bangalore/",
            "name": "skill_location_walkin_jobs",
        },
        {"url": host_name + "/java-fresher-jobs/", "name": "skill_fresher_jobs"},
        {
            "url": host_name + "/bangalore-fresher-jobs/",
            "name": "location_fresher_jobs",
        },
        {
            "url": host_name + "/java-fresher-jobs-in-bangalore/",
            "name": "skill_location_fresher_jobs",
        },
        {"url": host_name + "/bpo-industry-jobs/", "name": "industry_jobs"},
        {
            "url": host_name + "/internship-in-bangalore/",
            "name": "location_internship_jobs",
        },
        {"url": host_name + "/walkin-jobs/", "name": "walkin_jobs"},
        {"url": host_name + "/full-time-jobs/", "name": "full_time_jobs"},
        {"url": host_name + "/government-jobs/", "name": "government_jobs"},
        {"url": host_name + "/internship-jobs/", "name": "internship_jobs"},
        {"url": host_name + "/alert/list/", "name": "alerts_list"},
        {"url": host_name + "/recruiters/", "name": "recruiters_list"},
        {"url": host_name + "/recruiters/smitra/", "name": "recruiter_profile"},
        {"url": host_name + "/jobs/", "name": "jobs_list_page"},
        {"url": host_name + "/jobs-by-skill/", "name": "jobs_by_skills"},
        {"url": host_name + "/jobs-by-industry/", "name": "jobs_by_industry"},
        {
            "url": host_name + "/jobs-by-location/",
            "name": "jobs_by_location",
            "job_type": "jobs",
        },
        {"url": host_name + "/calendar/2017/", "name": "year_calendar"},
        {"url": host_name + "/companies/", "name": "companies_list"},
        {"url": host_name + "/integraph-job-openings/", "name": "company_jobs"},
        {"url": host_name + "/blog/", "name": "blog_list"},
        {
            "url": host_name + "/blog/how-to-develop-a-successful-career-plan/",
            "name": "blog_view",
        },
        {"url": host_name + "/blog/2017/1/", "name": "blog_archieve"},
        {"url": host_name + "/blog/category/job-search/", "name": "categories_list"},
        {"url": host_name + "/blog/tags/seo/", "name": "blog_tags"},
        {"url": host_name + "/calendar/2017/month/1/", "name": "month_calendar"},
        {"url": host_name + "/calendar/2017/month/1/week/1/", "name": "week_calendar"},
        {
            "url": host_name + "/jobposts/year/2017/month/1/date/1/",
            "name": "day_calendar",
        },
        {"url": host_name + "/jobs-by-degree/", "name": "jobs_by_degree"},
        {
            "url": host_name + "/junior-python-developer-0-to-2-years-1046/",
            "name": "job_detail_page",
        },
        {"url": host_name + "/post-job/", "name": "post_job"},
        {"url": host_name + "/recruiter/login/", "name": "recruiter_login"},
        {
            "url": host_name + "/walkin-jobs-by-skills/",
            "name": "fresher_jobs_by_skills",
            "job_type": "walkin",
        },
        {
            "url": host_name + "/fresher-jobs-by-skills/",
            "name": "fresher_jobs_by_skills",
            "job_type": "fresher",
        },
        # {'url': host_name + '/page/about-us/', 'name': ''},
        # {'url': host_name + '/page/terms-conditions/', 'name': ''},
        # {'url': host_name + '/page/privacy-policy/', 'name': ''},
        # {'url': host_name + '/page/recruiter-faq/', 'name': ''},
        # {'url': host_name + '/page/faq/', 'name': ''},
    ]

    test_data = {
        "skill": "Java",
        "city": "Bangalore",
        "current_page": "1",
        "industry": "BPO / Call Centre / ITES",
        "company": {"name": "Integraph"},
        "tag": {"name": "SEO"},
        "user": {"username": "smitra"},
        "blog_name": {"title": "How to develop a successful career plan?"},
        "category": {"name": "Job Search"},
        "degree": "B.Com",
        "month": "January 2017",
        "searched_month": "January",
        "date": 1,
        "year": 2017,
        "job": {
            "title": "Junior Python Developer",
            "job_role": "Software Developer",
            "min_year": 0,
            "max_year": 2,
            "location": {"all": [{"name": "Hyderabad"}]},
        },
        "search": "Java, B.Com",
    }
    for each in urls:
        is_meta_title_correct = is_meta_description_correct = is_h1_tag_correct = False
        # url = each['url']
        page_meta_data = db.meta_data.find_one({"name": each["name"]})
        test_data.update(each)
        meta_title = Template(page_meta_data.get("meta_title")).render(
            Context(test_data)
        )
        meta_description = Template(page_meta_data.get("meta_description")).render(
            Context(test_data)
        )
        h1_tag = Template(page_meta_data.get("h1_tag")).render(Context(test_data))
        soup = BeautifulSoup(requests.get(each["url"]).text)
        metas = soup.find_all("meta")
        url_meta_description = [
            meta.attrs["content"]
            for meta in metas
            if "name" in meta.attrs and meta.attrs["name"] == "description"
        ]
        url_meta_title = [
            meta.attrs["content"]
            for meta in metas
            if "property" in meta.attrs and meta.attrs["property"] == "og:title"
        ]
        metas = soup.find_all("h1")
        url_h1_tag = [
            meta.text
            for meta in metas
            if "class" in meta.attrs and meta.attrs["class"] == "internship-text"
        ]
        if url_h1_tag:
            if url_h1_tag[0] == h1_tag:
                is_h1_tag_correct = True
        else:
            is_h1_tag_correct = True
        if url_meta_title and url_meta_title[0] == meta_title:
            is_meta_title_correct = True
        if url_meta_description and url_meta_description[0] == meta_description:
            is_meta_description_correct = True
        each.update(
            {
                "is_h1_tag_correct": is_h1_tag_correct,
                "is_meta_description_correct": is_meta_description_correct,
                "is_meta_title_correct": is_meta_title_correct,
                "url_meta_title[0]": url_meta_title,
                "url_meta_description[0]": url_meta_description,
                "url_h1_tag[0]": url_h1_tag,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "h1_tag": h1_tag,
            }
        )
        db.meta_data.update(
            {"name": each["name"]},
            {
                "$set": {
                    "is_h1_tag_correct": is_h1_tag_correct,
                    "is_meta_description_correct": is_meta_description_correct,
                    "is_meta_title_correct": is_meta_title_correct,
                }
            },
        )
