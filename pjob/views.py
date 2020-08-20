import json
import math
import re
import os
import boto
import tinys3
import random

from django.shortcuts import render, redirect
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from datetime import date, datetime
from django.db.models import Q, F, Case, When, Value
from django.urls import reverse
from django.template import loader, Template, Context
from django.db.models import Count
from django.core import serializers
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from django.contrib.auth import authenticate, login
from django.utils.crypto import get_random_string
from django.template.defaultfilters import slugify
from django.http import QueryDict


from mpcomp.views import (
    jobseeker_login_required,
    Memail,
    get_prev_after_pages_count,
    get_valid_skills_list,
    mongoconnection,
    get_meta_data,
    get_valid_locations_list,
    get_social_referer,
    get_resume_data,
    handle_uploaded_file,
    get_valid_qualifications,
    get_meta,
    save_codes_and_send_mail,
    get_ordered_skill_degrees,
    get_404_meta,
    rand_string,
)
from peeldb.models import (
    JobPost,
    AppliedJobs,
    User,
    City,
    Industry,
    Skill,
    Subscriber,
    VisitedJobs,
    State,
    TechnicalSkill,
    Company,
    UserEmail,
    Qualification,
)
from pjob.calendar_events import (
    create_google_calendar_event,
    get_calendar_events_list,
    delete_google_calendar_event,
    get_service,
)
from psite.forms import (
    SubscribeForm,
    UserEmailRegisterForm,
    UserPassChangeForm,
    AuthenticationForm,
    ForgotPassForm,
)
from .refine_search import refined_search
from django.db.models import Prefetch
from django.core.cache import cache
from dashboard.tasks import save_search_results

db = mongoconnection()


months = [
    {"Name": "Jan", "id": 1},
    {"Name": "Feb", "id": 2},
    {"Name": "Mar", "id": 3},
    {"Name": "Apr", "id": 4},
    {"Name": "May", "id": 5},
    {"Name": "Jun", "id": 6},
    {"Name": "Jul", "id": 7},
    {"Name": "Aug", "id": 8},
    {"Name": "Sep", "id": 9},
    {"Name": "Oct", "id": 10},
    {"Name": "Nov", "id": 11},
    {"Name": "Dec", "id": 12},
]


def get_page_number(request, kwargs, no_pages):
    page = request.POST.get("page") or kwargs.get("page_num", 1)
    try:
        page = int(page)
        if page == 1 or page > 0 and page < (no_pages + 1):
            page = page
        else:
            page = False
    except:
        page = False
    return page


def get_next_year(year, current_year):
    if year == current_year + 1:
        return ""
    return year + 1


def get_prev_year(year, current_year):
    if year == current_year - 1:
        return ""
    return year - 1


def get_next_month(month, year, current_year):
    if month["id"] == 12:
        if get_next_year(year, current_year):
            return next((item for item in months if item["id"] == 1), None)
        return ""
    return next((item for item in months if item["id"] == month["id"] + 1), None)


def get_prev_month(month, year, current_year):
    if month["id"] == 1:
        if get_prev_year(year, current_year):
            return next((item for item in months if item["id"] == 12), None)
        return ""
    return next((item for item in months if item["id"] == month["id"] - 1), None)


def subscribers_creation_with_skills(email, skill, user):
    subscribers = Subscriber.objects.filter(email=email, user=None, skill=skill)
    if subscribers:
        for each in subscribers:
            if user:
                sub = Subscriber.objects.create(
                    email=each.email, skill=each.skill, user=user
                )
                while True:
                    unsubscribe_code = get_random_string(length=15)
                    if not Subscriber.objects.filter(
                        unsubscribe_code__iexact=unsubscribe_code
                    ):
                        break
                while True:
                    subscribe_code = get_random_string(length=15)
                    if not Subscriber.objects.filter(
                        subscribe_code__iexact=unsubscribe_code
                    ):
                        break
                sub.subscribe_code = subscribe_code
                sub.unsubscribe_code = unsubscribe_code
                sub.save()
                each.delete()
    else:
        while True:
            unsubscribe_code = get_random_string(length=15)
            if not Subscriber.objects.filter(unsubscribe_code__iexact=unsubscribe_code):
                break
        if user:
            sub = Subscriber.objects.create(email=email, skill=skill, user=user)
        else:
            sub = Subscriber.objects.create(email=email, skill=skill)
        sub.unsubscribe_code = unsubscribe_code
        while True:
            subscribe_code = get_random_string(length=15)
            if not Subscriber.objects.filter(subscribe_code__iexact=unsubscribe_code):
                break
        sub.subscribe_code = subscribe_code
        sub.save()
    return sub.subscribe_code


def jobs_applied(request):
    if request.user.is_authenticated and request.user.user_type == "JS":
        request.session["formdata"] = ""
        applied_jobs = AppliedJobs.objects.filter(user=request.user).exclude(
            ip_address="", user_agent=""
        )
        suggested_jobs = []
        if not applied_jobs:
            user_skills = Skill.objects.filter(
                id__in=request.user.skills.all().values("skill")
            )
            suggested_jobs = JobPost.objects.filter(
                Q(skills__in=user_skills) | Q(location__in=[request.user.current_city])
            )
            suggested_jobs = list(suggested_jobs.filter(status="Live"))
        suggested_jobs = suggested_jobs + list(
            JobPost.objects.filter(status="Live").order_by("-published_on")[:10]
        )
        items_per_page = 15
        no_of_jobs = applied_jobs.count()

        no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                page = 1
                return HttpResponseRedirect(reverse("jobs:jobs_applied"))
            else:
                page = int(request.GET.get("page"))
        else:
            page = 1
        ids = applied_jobs.values_list("job_post", flat=True)
        applied_jobs = JobPost.objects.filter(id__in=ids)
        applied_jobs = applied_jobs[(page - 1) * items_per_page : page * items_per_page]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        data = {
            "applied_jobs": applied_jobs,
            "year": date.today().year,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "no_of_jobs": no_of_jobs,
            "suggested_jobs": suggested_jobs[:10],
        }
        template = (
            "mobile/jobs/applied_jobs.html"
            if request.is_mobile
            else "candidate/applied_jobs.html"
        )
        return render(request, template, data)
    else:
        return HttpResponseRedirect("/")


def job_detail(request, job_title_slug, job_id):
    if not job_id or bool(re.search(r"[A-Za-z]", job_id)):
        reason = "The URL may be misspelled or the page you're looking for is no longer available."
        template = "mobile/404.html" if request.is_mobile else "404.html"
        return render(
            request,
            template,
            {"message": "Sorry, No Jobs Found", "job_search": True, "reason": reason},
            status=404,
        )
    job = (
        JobPost.objects.filter(id=job_id)
        .select_related("company", "user")
        .prefetch_related(
            "location",
            "skills",
            "industry",
            "functional_area",
            "job_interview_location",
        )
        .first()
    )
    if job:
        if str(job.get_absolute_url()) != str(request.path):
            return redirect(job.get_absolute_url(), permanent=False)
        if job.status == "Live":
            if request.user.is_authenticated:
                visited_jobs = VisitedJobs.objects.filter(
                    user=request.user, job_post=job
                )
                if not visited_jobs:
                    VisitedJobs.objects.create(user=request.user, job_post=job)
            field = get_social_referer(request)
            if field == "fb":
                job.fb_views += 1
            elif field == "tw":
                job.tw_views += 1
            elif field == "ln":
                job.ln_views += 1
            else:
                job.other_views += 1
            job.save()
        elif job.status == "Disabled":
            if job.major_skill and job.major_skill.status == "Active":
                return HttpResponseRedirect(job.major_skill.get_job_url())
            elif job.skills.filter(status="Active").exists():
                return HttpResponseRedirect(
                    job.skills.filter(status="Active").first().get_job_url()
                )
            return HttpResponseRedirect(reverse("jobs:index"))
        else:
            template = "mobile/404.html" if request.is_mobile else "404.html"
            return render(
                request,
                template,
                {
                    "message": "Sorry, No Jobs Found",
                    "job_search": True,
                    "reason": "The URL may be misspelled or the page you're looking for is no longer available.",
                },
                status=404,
            )
        show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
        meta_title = meta_description = ""
        meta = db.meta_data.find_one({"name": "job_detail_page"})
        if meta:
            meta_title = Template(meta.get("meta_title")).render(Context({"job": job}))
            meta_description = Template(meta.get("meta_description")).render(
                Context({"job": job})
            )
        template = (
            "mobile/jobs/detail.html" if request.is_mobile else "jobs/detail.html"
        )
        data = {
            "job": job,
            "show_pop_up": show_pop,
            "meta_title": meta_title,
            "meta_description": meta_description,
        }
        return render(request, template, data)
    else:
        latest = JobPost.objects.order_by("id").last().id
        if int(job_id) < latest:
            return redirect(reverse("jobs:index"), permanent=True)
        message = "Sorry,  no jobs available"
        reason = "Unfortunately, we are unable to locate the job you are looking for"
        template = "mobile/404.html" if request.is_mobile else "404.html"
        return render(
            request,
            template,
            {"message": message, "reason": reason, "job_search": True},
            status=404,
        )


def recruiter_profile(request, recruiter_name, **kwargs):
    current_url = reverse(
        "recruiter_profile", kwargs={"recruiter_name": recruiter_name}
    )
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(current_url, permanent=True)
    if "page" in request.GET:
        url = current_url + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    if re.match(
        r"^/jobs/recruiter/(?P<recruiter_name>[a-zA-Z0-9_-]+)/", request.get_full_path()
    ):
        url = (
            request.get_full_path()
            .replace("jobs/", "")
            .replace("recruiter", "recruiters")
        )
        return redirect(url, permanent=True)

    job_list = (
        JobPost.objects.filter(user__username__iexact=recruiter_name, status="Live")
        .select_related("company", "user")
        .prefetch_related("location", "skills", "industry")
        .order_by("-published_on")
        .distinct()
    )
    no_of_jobs = job_list.count()

    user = User.objects.filter(username__iexact=recruiter_name).prefetch_related(
        "technical_skills", "functional_area", "industry"
    )
    if user:
        items_per_page = 10
        no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
        page = get_page_number(request, kwargs, no_pages)
        if not page:
            return HttpResponseRedirect(current_url)
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        job_list = job_list[(page - 1) * items_per_page : page * items_per_page]
        meta_title = meta_description = h1_tag = ""
        meta = db.meta_data.find_one({"name": "recruiter_profile"})
        if meta:
            meta_title = Template(meta.get("meta_title")).render(
                Context({"current_page": page, "user": user[0]})
            )
            meta_description = Template(meta.get("meta_description")).render(
                Context({"current_page": page, "user": user[0]})
            )
            h1_tag = Template(meta.get("h1_tag")).render(
                Context({"current_page": page, "user": user[0]})
            )
        template = (
            "mobile/jobs/recruiter_detail.html"
            if request.is_mobile
            else "jobs/recruiter_profile.html"
        )
        return render(
            request,
            template,
            {
                "user": user[0],
                "job_list": job_list,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
                "no_of_jobs": no_of_jobs,
                "current_url": current_url,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "h1_tag": h1_tag,
            },
        )
    else:
        template = "mobile/404.html" if request.is_mobile else "404.html"
        return render(
            request,
            template,
            {
                "message": "Sorry, Recruiter profile unavailable",
                "data_empty": True,
                "reason": "Unfortunately, we are unable to locate the recruiter you are looking for",
            },
            status=404,
        )


def recruiters(request, **kwargs):
    if kwargs.get("page_num") == "1":
        return redirect(reverse("recruiters"), permanent=True)
    if "page" in request.GET:
        url = reverse("recruiters") + "page/" + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    recruiters_list = (
        User.objects.filter(
            Q(user_type="RR")
            | Q(user_type="AR")
            | Q(user_type="AA") & Q(is_active=True, mobile_verified=True)
        )
        .annotate(num_posts=Count("jobposts"))
        .prefetch_related("company")
        .order_by("-num_posts")
    )
    if request.POST.get("alphabet_value"):
        recruiters_list = recruiters_list.filter(
            username__istartswith=request.POST.get("alphabet_value")
        )
    items_per_page = 45
    no_pages = int(math.ceil(float(len(recruiters_list)) / items_per_page))
    page = get_page_number(request, kwargs, no_pages)
    if not page:
        return HttpResponseRedirect("/recruiters/")
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    recruiters_list = recruiters_list[
        (page - 1) * items_per_page : page * items_per_page
    ]
    meta_title, meta_description, h1_tag = get_meta("recruiters_list", {"page": page})
    template = (
        "mobile/jobs/recruiters_list.html"
        if request.is_mobile
        else "jobs/recruiters_list.html"
    )
    return render(
        request,
        template,
        {
            "recruiters": recruiters_list,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "current_url": reverse("recruiters"),
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
        },
    )


def index(request, **kwargs):
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(reverse("jobs:index"), permanent=True)
    if "page" in request.GET:
        url = reverse("jobs:index") + request.GET.get("page") + "/"
        return redirect(url, permanent=True)

    # jobs_list = JobPost.objects.filter(
    #     status='Live').select_related('company', 'user').prefetch_related(
    #     'location', 'skills', 'industry').distinct()
    searched_locations = (
        searched_skills
    ) = searched_industry = searched_edu = searched_states = ""
    if request.POST.get("refine_search") == "True":
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(request.POST)
    else:
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search({})

    no_of_jobs = jobs_list.count()

    items_per_page = 20
    no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
    page = get_page_number(request, kwargs, no_pages)
    if not page:
        return HttpResponseRedirect(reverse("jobs:index"))
    jobs_list = jobs_list[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    field = get_social_referer(request)
    show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
    meta_title, meta_description, h1_tag = get_meta("jobs_list_page", {"page": page})
    data = {
        "job_list": jobs_list,
        "aft_page": aft_page,
        "after_page": after_page,
        "prev_page": prev_page,
        "previous_page": previous_page,
        "current_page": page,
        "last_page": no_pages,
        "no_of_jobs": no_of_jobs,
        "is_job_list": True,
        "current_url": reverse("jobs:index"),
        "show_pop_up": show_pop,
        "searched_skills": searched_skills,
        "searched_locations": searched_locations,
        "searched_industry": searched_industry,
        "searched_experience": request.POST.get("experience"),
        "searched_edu": searched_edu,
        "searched_states": searched_states,
        "searched_job_type": request.POST.get("job_type"),
        "meta_title": meta_title,
        "meta_description": meta_description,
        "h1_tag": h1_tag,
    }
    if request.is_mobile:
        data.update(
            {
                "searched_industry": request.POST.get("industry"),
                "searched_functional_area": request.POST.get("functional_area"),
            }
        )
    template = "mobile/jobs/list.html" if request.is_mobile else "jobs/jobs_list.html"
    return render(request, template, data)


def job_locations(request, location, **kwargs):
    current_url = reverse("job_locations", kwargs={"location": location})
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(current_url, permanent=True)
    if "page" in request.GET:
        url = current_url + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    request.session["formdata"] = ""
    final_location = get_valid_locations_list(location)
    state = State.objects.filter(slug__iexact=location)
    if request.POST.get("refine_search") == "True":
        (
            job_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(request.POST)
        final_location = final_location + list(
            searched_states.values_list("name", flat=True)
        )
    elif state:
        final_location = [state[0].name]
        search_dict = QueryDict("", mutable=True)
        search_dict.setlist("refine_state", [state[0].name])
        (
            job_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(search_dict)
    elif final_location:
        search_dict = QueryDict("", mutable=True)
        search_dict.setlist("refine_location", final_location)
        if request.POST.get("experience"):
            search_dict.update(
                {"refine_experience_min": request.POST.get("experience")}
            )
        (
            job_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(search_dict)
    else:
        job_list = []
    if request.POST.get("location"):
        save_search_results.delay(
            request.META["REMOTE_ADDR"],
            request.POST,
            job_list.count() if job_list else 0,
            request.user.id,
        )
    if job_list:
        items_per_page = 20
        searched_industry = searched_skills = searched_edu = ""
        if request.GET.get("job_type"):
            job_list = job_list.filter_and(job_type__in=[request.GET.get("job_type")])
        no_of_jobs = job_list.count()
        no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
        page = get_page_number(request, kwargs, no_pages)
        if not page:
            return HttpResponseRedirect(current_url)
        jobs_list = job_list[(page - 1) * items_per_page : page * items_per_page]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        field = get_social_referer(request)
        show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
        meta_title, meta_description, h1_tag = get_meta_data(
            "location_jobs",
            {
                "locations": searched_locations,
                "final_location": set(final_location),
                "page": page,
                "state": bool(state),
            },
        )
        data = {
            "job_list": jobs_list,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "no_of_jobs": no_of_jobs,
            "current_url": current_url,
            "skill_jobs": True,
            "show_pop_up": show_pop,
            "searched_skills": searched_skills,
            "searched_locations": searched_locations,
            "searched_states": searched_states,
            "searched_industry": searched_industry,
            "searched_experience": request.POST.get("experience"),
            "searched_edu": searched_edu,
            "searched_job_type": request.POST.get("job_type"),
            "searched_functional_area": request.POST.get("functional_area"),
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
            "state": state.first(),
        }
        if request.is_mobile:
            data.update(
                {
                    "searched_industry": request.POST.get("industry"),
                    "searched_functional_area": request.POST.get("functional_area"),
                }
            )
        template = (
            "mobile/jobs/list.html" if request.is_mobile else "jobs/jobs_list.html"
        )
        return render(request, template, data)
    else:
        if final_location:
            search = final_location
            status = 200
            meta_title, meta_description = get_404_meta(
                "location_404", {"city": search}
            )
        else:
            search = [location]
            status = 404
            meta_title = meta_description = ""
        reason = "Only Cities/States names are accepted in location field"
        template = "mobile/404.html" if request.is_mobile else "404.html"
        return render(
            request,
            template,
            {
                "message": "Unfortunately, we are unable to locate the jobs you are looking for",
                "meta_title": meta_title,
                "meta_description": meta_description,
                "job_search": True,
                "reason": reason,
                "searched_locations": search,
                "data_empty": status != 200,
            },
            status=status,
        )


def list_deserializer(key, value, flags):
    import ast

    value = value.decode("utf-8")
    value = ast.literal_eval(value)
    value = [i.strip() for i in value if i.strip()]
    return value


def job_skills(request, skill, **kwargs):

    # from pymemcache.client.base import Client
    # from pymemcache import serde
    # client = Client(('127.0.0.1', 11211),
    #             serializer=serde.python_memcache_serializer,
    #             deserializer=serde.python_memcache_deserializer)

    from pymemcache.client.base import Client

    client = Client(("localhost", 11211), deserializer=list_deserializer)
    current_url = reverse("job_skills", kwargs={"skill": skill})
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(current_url, permanent=True)

    if "page" in request.GET:
        url = current_url + request.GET.get("page") + "/"
        return redirect(url, permanent=True)

    final_skill = client.get("final_skill" + skill)
    if not final_skill:
        final_skill = get_valid_skills_list(skill)
        client.set("final_skill" + skill, final_skill, expire=60 * 60 * 24)
    if final_skill == b"[]":
        final_skill = []

    final_edu = client.get("final_edu" + skill)
    if not final_edu:
        final_edu = get_valid_qualifications(skill)
        client.set("final_edu" + skill, final_edu, expire=60 * 60 * 24)

    if final_edu == b"[]":
        final_edu = []
    if request.POST.get("refine_search") == "True":
        (
            job_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(request.POST)
    else:
        search_dict = QueryDict("", mutable=True)
        if final_skill or final_edu:
            search_dict.setlist("refine_skill", final_skill)
            search_dict.setlist("refine_education", final_edu)
        else:
            search_dict.setlist("refine_skill", [skill])

        if request.POST.get("experience"):
            search_dict.update(
                {"refine_experience_min": request.POST.get("experience")}
            )

        (
            job_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(search_dict)
    searched_text = get_ordered_skill_degrees(
        skill,
        searched_skills.filter(name__in=final_skill),
        searched_edu.filter(name__in=final_edu),
    )

    if request.POST.get("q"):
        save_search_results.delay(
            request.META["REMOTE_ADDR"], request.POST, job_list.count(), request.user.id
        )

    if job_list.count() > 0:

        if request.GET.get("job_type"):
            job_list = job_list.filter_and(job_type__in=[request.GET.get("job_type")])
        no_of_jobs = job_list.count()
        no_pages = int(math.ceil(float(no_of_jobs) / 20))
        page = get_page_number(request, kwargs, no_pages)
        if not page:
            return HttpResponseRedirect(current_url)

        jobs_list = job_list[(page - 1) * 20 : page * 20]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )

        field = get_social_referer(request)
        show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
        meta_title = meta_description = h1_tag = ""
        final_edu = ", ".join(final_edu)
        if searched_edu and not searched_skills:
            meta = db.meta_data.find_one({"name": "education_jobs"})
            if meta:
                meta_title = Template(meta.get("meta_title")).render(
                    Context({"current_page": page, "degree": final_edu})
                )
                meta_description = Template(meta.get("meta_description")).render(
                    Context({"current_page": page, "degree": final_edu})
                )
                h1_tag = Template(meta.get("h1_tag")).render(
                    Context({"current_page": page, "degree": final_edu})
                )
        elif searched_edu and searched_skills:
            meta = db.meta_data.find_one({"name": "skill_education_jobs"})
            if meta:
                search = ", ".join(searched_text)
                meta_title = Template(meta.get("meta_title")).render(
                    Context({"current_page": page, "search": search})
                )
                meta_description = Template(meta.get("meta_description")).render(
                    Context({"current_page": page, "search": search})
                )
                h1_tag = Template(meta.get("h1_tag")).render(
                    Context({"current_page": page, "search": search})
                )
        elif searched_skills:
            meta_title, meta_description, h1_tag = get_meta_data(
                "skill_jobs",
                {"skills": searched_skills, "final_skill": final_skill, "page": page},
            )
        else:
            meta_title, meta_description, h1_tag = get_meta_data(
                "skill_jobs", {"final_skill": [skill], "page": page}
            )
            searched_text = [skill]
        data = {
            "job_list": jobs_list,
            "current_url": current_url,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "no_of_jobs": no_of_jobs,
            "show_pop_up": show_pop,
            "location_jobs": True,
            "searched_skills": searched_skills,
            "searched_locations": searched_locations,
            "searched_industry": searched_industry,
            "searched_edu": searched_edu,
            "searched_states": searched_states,
            "experience": request.POST.get("experience"),
            "searched_job_type": request.POST.get("job_type")
            or request.GET.get("job_type"),
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
            "searched_text": searched_text,
        }

        if request.is_mobile:
            data.update(
                {
                    "searched_industry": request.POST.get("industry"),
                    "searched_functional_area": request.POST.get("functional_area"),
                }
            )
        template = (
            "mobile/jobs/list.html" if request.is_mobile else "jobs/jobs_list.html"
        )
        return render(request, template, data)
    else:
        if final_skill or final_edu:
            search = final_skill + final_edu
            status = 200
            meta_title, meta_description = get_404_meta("skill_404", {"skill": search})
        else:
            search = [skill]
            status = 404
            meta_title = meta_description = ""
        reason = "Only valid Skills/Qualifications names are accepted"
        template = "mobile/404.html" if request.is_mobile else "404.html"
        return render(
            request,
            template,
            {
                "message": "Unfortunately, we are unable to locate the jobs you are looking for",
                "meta_title": meta_title,
                "meta_description": meta_description,
                "job_search": True,
                "reason": reason,
                "searched_skills": search,
                "data_empty": status != 200,
            },
            status=status,
        )


def job_industries(request, industry, **kwargs):
    current_url = reverse("job_industries", kwargs={"industry": industry})
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(current_url, permanent=True)
    if "page" in request.GET:
        url = current_url + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    searched_locations = searched_skills = searched_edu = searched_states = ""
    searched_industry = Industry.objects.filter(slug=industry)
    search_dict = QueryDict("", mutable=True)
    search_dict.setlist("refine_industry", [searched_industry[0].name])

    if request.POST.get("refine_search") == "True":
        (
            job_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(request.POST)
    else:
        (
            job_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(search_dict)

    if job_list:
        no_of_jobs = job_list.count()
        items_per_page = 20
        no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
        page = get_page_number(request, kwargs, no_pages)
        if not page:
            return HttpResponseRedirect(current_url)

        jobs_list = job_list[(page - 1) * items_per_page : page * items_per_page]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )

        field = get_social_referer(request)
        show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
        meta_title = meta_description = h1_tag = ""
        meta = db.meta_data.find_one({"name": "industry_jobs"})
        if meta:
            meta_title = Template(meta.get("meta_title")).render(
                Context({"current_page": page, "industry": searched_industry[0].name})
            )
            meta_description = Template(meta.get("meta_description")).render(
                Context({"current_page": page, "industry": searched_industry[0].name})
            )
            h1_tag = Template(meta.get("h1_tag")).render(
                Context({"current_page": page, "industry": searched_industry[0].name})
            )
        data = {
            "job_list": jobs_list,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "no_of_jobs": no_of_jobs,
            "show_pop_up": show_pop,
            "current_url": current_url,
            "searched_skills": searched_skills,
            "searched_locations": searched_locations,
            "searched_industry": searched_industry,
            "searched_edu": searched_edu,
            "searched_states": searched_states,
            "searched_experience": request.POST.get("experience"),
            "searched_job_type": request.POST.get("job_type"),
            "searched_functional_area": request.POST.get("functional_area"),
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
        }
        if request.is_mobile:
            data.update(
                {
                    "searched_industry": request.POST.get("industry"),
                    "searched_functional_area": request.POST.get("functional_area"),
                }
            )
        template = (
            "mobile/jobs/list.html" if request.is_mobile else "jobs/jobs_list.html"
        )
        return render(request, template, data)
    else:
        if searched_industry:
            reason = "No Jobs available with searched Industry"
            meta_title, meta_description = get_404_meta(
                "industry_404", {"industry": industry}
            )
        else:
            reason = "Unable to locate the Industry you are looking for"
            meta_title = meta_description = ""
        template = "mobile/404.html" if request.is_mobile else "404.html"
        return render(
            request,
            template,
            {
                "message": "Unfortunately, we are unable to locate the jobs you are looking for",
                "meta_title": meta_title,
                "meta_description": meta_description,
                "job_search": True,
                "reason": reason,
                "data_empty": False if searched_industry else True,
            },
            status=200 if searched_industry else 404,
        )


def user_applied_job(request):
    request.session["job_id"] = request.POST.get("job_id")
    data = {"error": False, "response": "User successfully applied for a job"}
    return HttpResponse(json.dumps(data))


@login_required
def job_apply(request, job_id):
    if (
        request.user.is_active or request.GET.get("apply_now")
    ) and request.user.user_type == "JS":
        job_post = JobPost.objects.filter(id=job_id, status="Live").first()
        if job_post:
            if not AppliedJobs.objects.filter(user=request.user, job_post=job_post):
                if (
                    request.user.resume
                    or request.user.profile_completion_percentage >= 50
                ):
                    # need to check user uploaded a resume or not
                    AppliedJobs.objects.create(
                        user=request.user,
                        job_post=job_post,
                        status="Pending",
                        ip_address=request.META["REMOTE_ADDR"],
                        user_agent=request.META["HTTP_USER_AGENT"],
                    )
                    message = (
                        "Your Application successfully sent for "
                        + str(job_post.title)
                        + " at "
                        + job_post.company_name
                    )
                    t = loader.get_template("email/applicant_apply_job.html")
                    c = {
                        "user": request.user,
                        "recruiter": job_post.user,
                        "job_post": job_post,
                    }
                    rendered = t.render(c)
                    if request.user.resume:
                        import urllib.request

                        urllib.request.urlretrieve(
                            "http://s3.amazonaws.com/peeljobs/"
                            + str(
                                request.user.resume.encode("ascii", "ignore").decode(
                                    "ascii"
                                )
                            ),
                            str(request.user.email) + ".docx",
                        )
                    msg = MIMEMultipart()
                    msg["Subject"] = "Resume Alert - " + job_post.title
                    msg["From"] = settings.DEFAULT_FROM_EMAIL
                    msg["To"] = job_post.user.email
                    part = MIMEText(rendered, "html")
                    msg.attach(part)
                    if request.user.resume and os.path.exists(
                        str(request.user.email) + ".docx"
                    ):
                        part = MIMEApplication(
                            open(str(request.user.email) + ".docx", "rb").read()
                        )
                        part.add_header(
                            "Content-Disposition",
                            "attachment",
                            filename=str(request.user.email) + ".docx",
                        )
                        msg.attach(part)
                        os.remove(str(request.user.email) + ".docx")
                    boto.connect_ses(
                        aws_access_key_id=settings.AM_ACCESS_KEY,
                        aws_secret_access_key=settings.AM_PASS_KEY,
                    )
                    conn = boto.ses.connect_to_region(
                        "eu-west-1",
                        aws_access_key_id=settings.AM_ACCESS_KEY,
                        aws_secret_access_key=settings.AM_PASS_KEY,
                    )
                    # and send the message
                    conn.send_raw_email(
                        msg.as_string(), source=msg["From"], destinations=[msg["To"]]
                    )
                    data = {
                        "error": False,
                        "response": message,
                        "url": job_post.get_absolute_url(),
                    }
                    return HttpResponse(json.dumps(data))
                    # else:
                    #     data = {'error': True, 'response': 'Jobpost is already expired'}
                    #     return HttpResponse(json.dumps(data))

                else:
                    data = {
                        "error": True,
                        "response": "Please complete your profile to apply for this job",
                        "url": reverse("my:profile"),
                    }
                    return HttpResponse(json.dumps(data))
            else:
                data = {"error": True, "response": "User already applied for this job"}
                return HttpResponse(json.dumps(data))
        data = {"error": True, "response": "Job you are searching Not found"}
        return HttpResponse(json.dumps(data))
    if request.user.user_type == "RR":
        data = {"error": True, "response": "Recruiter Not allowed to Apply for Jobs"}
        return HttpResponse(json.dumps(data))
    if request.user.is_staff:
        data = {"error": True, "response": "Admin Not allowed to Apply For jobs"}
        return HttpResponse(json.dumps(data))
    data = {
        "error": True,
        "response": "You need to verify your Email to apply For this Job",
    }
    return HttpResponse(json.dumps(data))


def unsubscribe(request, email, job_post_id):
    job_post = JobPost.objects.filter(id=job_post_id)
    if job_post:
        subscribers = Subscriber.objects.filter(
            email=email, skill__in=job_post[0].skills.all()
        )
        if request.method == "POST":
            if str(request.POST["is_delete"]) == "True":
                subscribers.delete()
                data = {
                    "error": False,
                    "response": "Please Update Your Profile To Apply For a job ",
                }
            else:
                data = {
                    "error": True,
                    "response": "Please Update Your Profile To Apply For a job ",
                }
            return HttpResponse(json.dumps(data))
        return render(
            request, "unsubscribe.html", {"email": email, "subscribers": subscribers}
        )
    else:
        message = "Sorry, no jobs available"
        reason = "Unfortunately, we are unable to locate the job you are looking for"
        template = "mobile/404.html" if request.is_mobile else "404.html"
        return render(
            request, template, {"message": message, "reason": reason}, status=404
        )


def year_calendar(request, year):
    if request.POST.get("year"):
        year = int(request.POST.get("year"))
    jobs_list = JobPost.objects.filter(status="Live")

    month = {"Name": "Jan", "id": 1}
    year = int(year)
    calendar_events = []
    # if request.user.is_authenticated:
    #     calendar_events = get_calendar_events_list()
    meta_title, meta_description, h1_tag = get_meta("year_calendar", {"page": 1})
    return render(
        request,
        "calendar/year_calendar.html",
        {
            "months": months,
            "year": year,
            "prev_year": get_prev_year(year, year),
            "next_year": get_next_year(year, year),
            "post_data": "true" if request.POST else "false",
            "jobs_list": jobs_list,
            "calendar_type": "year",
            "month": month,
            "calendar_events": calendar_events,
            "meta_title": meta_title,
            "h1_tag": h1_tag,
            "meta_description": meta_description,
        },
    )


def month_calendar(request, year, month):
    current_year = datetime.now().year
    year = current_year
    month = next((item for item in months if item["id"] == int(month)), None)
    calendar_events = []
    if request.user.is_authenticated:
        calendar_events = get_calendar_events_list(request)

    if request.method == "POST":
        if request.POST.get("year"):
            year = int(request.POST.get("year"))
        if request.POST.get("month"):
            month = next(
                (
                    item
                    for item in months
                    if item["id"] == int(request.POST.get("month"))
                ),
                None,
            )
            # return HttpResponseRedirect(reverse('week_calendar',
            # kwargs={'year': year, 'month': month['id'], 'week':
            # request.POST.get('week')}))

    post_data = False
    if "status" in request.POST.keys():
        post_data = True
    meta_title, meta_description, h1_tag = get_meta("month_calendar", {"page": 1})
    jobs_list = JobPost.objects.filter(status="Live")
    return render(
        request,
        "calendar/year_calendar.html",
        {
            "requested_month": request.POST.get("month")
            if request.POST.get("month")
            else None,
            "months": months,
            "year": year,
            "month": month,
            "prev_year": get_prev_year(year, current_year),
            "next_year": get_next_year(year, current_year),
            "prev_month": get_prev_month(month, year, current_year),
            "next_month": get_next_month(month, year, current_year),
            "jobs_list": jobs_list,
            "calendar_type": "month",
            "post_data": post_data,
            "calendar_events": calendar_events,
            "meta_title": meta_title,
            "h1_tag": h1_tag,
            "meta_description": meta_description,
        },
    )


def week_calendar(request, year, month, week):
    current_year = datetime.now().year
    year = current_year
    month = {"Name": "Jan", "id": 1}
    calendar_events = []
    if request.user.is_authenticated:
        calendar_events = get_calendar_events_list(request)

    if request.POST.get("year"):
        year = int(request.POST.get("year"))
    if request.POST.get("month"):
        month = next(
            (item for item in months if item["id"] == int(request.POST.get("month"))),
            None,
        )
    if request.POST.get("week"):
        week = int(request.POST.get("week"))
    jobs_list = JobPost.objects.filter(status="Live")
    meta_title, meta_description, h1_tag = get_meta("week_calendar", {"page": 1})
    return render(
        request,
        "calendar/year_calendar.html",
        {
            "months": months,
            "year": year,
            "prev_year": get_prev_year(year, year),
            "next_year": get_next_year(year, year),
            "post_data": "true" if request.POST else "false",
            "calendar_type": "week",
            "week": week,
            "month": month,
            "requested_month": month,
            "jobs_list": jobs_list,
            "calendar_events": calendar_events,
            "meta_title": meta_title,
            "h1_tag": h1_tag,
            "meta_description": meta_description,
        },
    )


def jobposts_by_date(request, year, month, date, **kwargs):
    current_url = reverse(
        "jobposts_by_date", kwargs={"year": year, "month": month, "date": date}
    )
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(current_url, permanent=True)
    if "page" in request.GET:
        url = current_url + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    import datetime

    day = datetime.date(int(year), int(month), int(date))
    results = JobPost.objects.filter(status="Live", last_date=day).order_by(
        "-published_on"
    )
    events = get_calendar_events_list(request) if request.user.is_authenticated else []
    event_titles = []
    for event in events:
        if event.get("start_date") and event.get("end_date"):
            if str(day) >= str(event["start_date"]) and str(day) <= str(
                event["end_date"]
            ):
                event_titles.append(event["summary"])
    events = JobPost.objects.filter(title__in=event_titles)
    if not results:
        template = "mobile/404.html" if request.is_mobile else "404.html"
        return render(
            request,
            template,
            {
                "message": "Sorry, no jobs available",
                "job_search": True,
                "data_empty": True,
                "reason": "Unfortunately, we are unable to locate the job you are looking for",
            },
            status=404,
        )
    no_pages = int(math.ceil(float(len(results)) / 20))
    page = get_page_number(request, kwargs, no_pages)
    if not page:
        return HttpResponseRedirect(current_url)
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    meta_title = meta_description = h1_tag = ""
    meta = db.meta_data.find_one({"name": "day_calendar"})
    if meta:
        meta_title = Template(meta.get("meta_title")).render(
            Context({"date": date, "searched_month": day.strftime("%B"), "year": year})
        )
        meta_description = Template(meta.get("meta_description")).render(
            Context({"date": date, "searched_month": day.strftime("%B"), "year": year})
        )
        h1_tag = Template(meta.get("h1_tag")).render(
            Context({"date": date, "month": day.strftime("%B"), "year": year})
        )
    return render(
        request,
        "calendar/calendar_day_results.html",
        {
            "no_of_jobs": len(results),
            "results": results[(page - 1) * 20 : page * 20],
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "month_num": day.month,
            "month": day.strftime("%B"),
            "year": year,
            "date": date,
            "current_url": current_url,
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
            "events": events,
        },
    )


def job_add_event(request):
    is_connected = True
    if request.POST:
        request.session["job_event"] = request.POST.get("job_id")
        if request.user.is_authenticated:
            service, is_connected = get_service(request)
        else:
            return HttpResponseRedirect(reverse("social:google_login"))
    if not is_connected:
        return service
    elif request.session.get("job_event"):
        jobpost = JobPost.objects.get(id=request.session.get("job_event"))
        msg = ""
        for location in jobpost.job_interview_location.all():
            if location.show_location:
                msg = location.venue_details
        event = {
            "summary": str(jobpost.title),
            "location": str(msg),
            "description": str(jobpost.title),
            "start": {"date": str(jobpost.last_date), "timeZone": "Asia/Calcutta",},
            "end": {"date": str(jobpost.last_date), "timeZone": "Asia/Calcutta",},
            "recurrence": ["RRULE:FREQ=DAILY;COUNT=2"],
            "attendees": [{"email": str(request.user.email)},],
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 60 * 15},
                    {"method": "popup", "minutes": 60 * 15},
                ],
            },
        }
        response, created = create_google_calendar_event(request, request.user, event)
        if created == "redirect":
            return response
        elif redirect:
            request.session["job_event"] = ""
            return redirect(
                jobpost.get_absolute_url() + "?event=success", permanent=False
            )
        else:
            return redirect(
                jobpost.get_absolute_url() + "?event=error", permanent=False
            )


def calendar_add_event(request):
    if request.method == "GET":
        return render(request, "calendar/add_calendar_event.html", {})
    start_date = datetime.strptime(
        str(request.POST.get("start_date")), "%m/%d/%Y"
    ).strftime("%Y-%m-%d")
    last_date = datetime.strptime(
        str(request.POST.get("to_date")), "%m/%d/%Y"
    ).strftime("%Y-%m-%d")

    event = {
        "summary": request.POST.get("title"),
        "location": request.POST.get("location"),
        "description": request.POST.get("description"),
        "start": {"date": str(start_date), "timeZone": "Asia/Calcutta",},
        "end": {"date": str(last_date), "timeZone": "Asia/Calcutta",},
        "recurrence": ["RRULE:FREQ=DAILY;COUNT=2"],
        "attendees": [{"email": str(request.user.email)},],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 24 * 60},
                {"method": "popup", "minutes": 10},
            ],
        },
    }
    response = create_google_calendar_event(request.user, event)
    if response:
        data = {"error": False, "response": "Event successfully added"}
    else:
        data = {"error": True, "response": "Please Try again after some time"}
    return HttpResponse(json.dumps(data))


def calendar_event_list(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        response = delete_google_calendar_event(event_id)
        if response:
            data = {"error": False, "response": "Event successfully Deleted"}
        else:
            data = {"error": True, "response": "Please Try again after some time"}
        return HttpResponse(json.dumps(data))
    events = get_calendar_events_list(request)
    return render(request, "calendar/calendar_event_list.html", {"events": events})


def jobs_by_location(request, job_type):
    all_degrees = Qualification.objects.filter(status="Active").order_by("name")
    states = (
        State.objects.annotate(
            num_locations=Count("state"),
            is_duplicate=Count(Case(When(state__name=F("name"), then=Value(1)))),
        )
        .filter(num_locations__gte=1, status="Enabled")
        .prefetch_related(
            Prefetch(
                "state",
                queryset=City.objects.filter(status="Enabled", parent_city=None),
                to_attr="active_cities",
            )
        )
    )
    if request.method == "POST":
        states = states.filter(name__icontains=request.POST.get("location"))
    meta_title = meta_description = h1_tag = ""
    meta = db.meta_data.find_one({"name": "jobs_by_location"})
    if meta:
        meta_title = Template(meta.get("meta_title")).render(
            Context({"job_type": job_type})
        )
        meta_description = Template(meta.get("meta_description")).render(
            Context({"job_type": job_type})
        )
        h1_tag = Template(meta.get("h1_tag")).render(Context({"job_type": job_type}))
    data = {
        "states": states,
        "job_type": job_type,
        "all_degrees": all_degrees[:10],
        "meta_title": meta_title,
        "meta_description": meta_description,
        "h1_tag": h1_tag,
    }
    template = (
        "mobile/jobs/jobs_by_location.html"
        if request.is_mobile
        else "jobs/jobs_by_location.html"
    )
    return render(request, template, data)


def jobs_by_skill(request):
    all_skills = Skill.objects.filter(status="Active")
    if request.method == "POST":
        if str(request.POST.get("alphabet_value")) != "all":
            all_skills = all_skills.filter(
                name__istartswith=request.POST.get("alphabet_value")
            )
        if request.POST.get("sorting_value") and (
            str(request.POST.get("sorting_value")) == "descending"
        ):
            all_skills = all_skills.order_by("-name")
        else:
            all_skills = all_skills.order_by("name")
    meta_title, meta_description, h1_tag = get_meta("jobs_by_skills", {"page": 1})
    data = {
        "all_skills": all_skills,
        "meta_title": meta_title,
        "meta_description": meta_description,
        "h1_tag": h1_tag,
    }
    template = (
        "mobile/jobs/jobs_by_skill.html"
        if request.is_mobile
        else "jobs/jobs_by_skills.html"
    )
    return render(request, template, data)


def fresher_jobs_by_skills(request, job_type):
    all_skills = Skill.objects.filter(status="Active")
    if request.method == "POST":
        if request.POST.get("alphabet_value"):
            all_skills = all_skills.filter(
                name__istartswith=request.POST.get("alphabet_value")
            )
        if (
            request.POST.get("sorting_value")
            and str(request.POST.get("sorting_value")) == "descending"
        ):
            all_skills = all_skills.order_by("-name")
        else:
            all_skills = all_skills.order_by("name")
    meta_title = meta_description = h1_tag = ""
    meta = db.meta_data.find_one({"name": "fresher_jobs_by_skills"})
    if meta:
        meta_title = Template(meta.get("meta_title")).render(
            Context({"job_type": job_type})
        )
        meta_description = Template(meta.get("meta_description")).render(
            Context({"job_type": job_type})
        )
        h1_tag = Template(meta.get("h1_tag")).render(Context({"job_type": job_type}))
    data = {
        "all_skills": all_skills,
        "job_type": job_type,
        "h1_tag": h1_tag,
        "meta_title": meta_title,
        "meta_description": meta_description,
    }
    template = (
        "mobile/jobs/fresher_jobs_by_skills.html"
        if request.is_mobile
        else "jobs/fresher_jobs_by_skills.html"
    )
    return render(request, template, data)


def jobs_by_industry(request):
    all_industries = (
        Industry.objects.filter(status="Active")
        .annotate(num_posts=Count("jobpost"))
        .order_by("-num_posts")
    )
    if request.method == "POST":
        all_industries = all_industries.filter(
            name__icontains=request.POST.get("industry")
        )
        if request.POST.get("sorting_value") and (
            str(request.POST.get("sorting_value")) == "descending"
        ):
            all_industries = all_industries.order_by("-name")
        else:
            all_industries = all_industries.order_by("name")
    meta_title, meta_description, h1_tag = get_meta("jobs_by_industry", {"page": 1})
    data = {
        "all_industries": all_industries,
        "h1_tag": h1_tag,
        "meta_title": meta_title,
        "meta_description": meta_description,
    }
    template = (
        "mobile/jobs/jobs_by_industries.html"
        if request.is_mobile
        else "jobs/jobs_by_industries.html"
    )
    return render(request, template, data)


def jobs_by_degree(request):
    all_degrees = Qualification.objects.filter(status="Active").order_by("name")
    if request.method == "POST":
        if str(request.POST.get("alphabet_value")) != "all":
            all_degrees = all_degrees.filter(
                name__istartswith=request.POST.get("alphabet_value")
            )
        if request.POST.get("sorting_value") and (
            str(request.POST.get("sorting_value")) == "descending"
        ):
            all_degrees = all_degrees.order_by("-name")
        else:
            all_degrees = all_degrees.order_by("name")
    meta_title, meta_description, h1_tag = get_meta("jobs_by_degree", {"page": 1})
    data = {
        "all_degrees": all_degrees,
        "h1_tag": h1_tag,
        "meta_title": meta_title,
        "meta_description": meta_description,
    }
    template = (
        "mobile/jobs/jobs_by_degree.html"
        if request.is_mobile
        else "jobs/jobs_by_degree.html"
    )
    return render(request, template, data)


def full_time_jobs(request, **kwargs):
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(reverse("full_time_jobs"), permanent=True)
    if "page" in request.GET:
        url = reverse("full_time_jobs") + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    request.session["formdata"] = ""

    searched_locations = (
        searched_industry
    ) = searched_skills = searched_edu = searched_states = ""
    if request.POST.get("refine_search") == "True":
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(request.POST)
    else:
        search_dict = QueryDict("", mutable=True)
        search_dict.setlist("job_type", ["full-time"])
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(search_dict)

    no_of_jobs = jobs_list.count()
    items_per_page = 20
    no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
    page = get_page_number(request, kwargs, no_pages)
    if not page:
        return HttpResponseRedirect(reverse("full_time_jobs"))

    jobs_list = jobs_list[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    field = get_social_referer(request)
    show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
    meta_title, meta_description, h1_tag = get_meta("full_time_jobs", {"page": page})
    data = {
        "job_list": jobs_list,
        "aft_page": aft_page,
        "after_page": after_page,
        "prev_page": prev_page,
        "previous_page": previous_page,
        "current_page": page,
        "last_page": no_pages,
        "no_of_jobs": no_of_jobs,
        "current_url": reverse("full_time_jobs"),
        "show_pop_up": show_pop,
        "searched_skills": searched_skills,
        "searched_locations": searched_locations,
        "searched_industry": searched_industry,
        "searched_edu": searched_edu,
        "searched_states": searched_states,
        "experience": request.POST.get("experience"),
        "searched_job_type": "full-time",
        "meta_title": meta_title,
        "meta_description": meta_description,
        "h1_tag": h1_tag,
    }
    if request.is_mobile:
        data.update(
            {
                "searched_industry": request.POST.get("industry"),
                "searched_functional_area": request.POST.get("functional_area"),
            }
        )
    template = "mobile/jobs/list.html" if request.is_mobile else "jobs/jobs_list.html"
    return render(request, template, data)


def internship_jobs(request, **kwargs):
    request.session["formdata"] = ""
    jobs_list = (
        JobPost.objects.filter(status="Live", job_type="internship")
        .select_related("company")
        .prefetch_related("location", "skills")[:9]
    )
    no_of_jobs = jobs_list.count()
    no_pages = int(math.ceil(float(no_of_jobs) / 20))
    page = get_page_number(request, kwargs, no_pages)
    if not page:
        return HttpResponseRedirect(reverse("internship_jobs"))

    jobs_list = jobs_list[(page - 1) * 20 : page * 20]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    field = get_social_referer(request)
    show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
    meta_title, meta_description, h1_tag = get_meta("internship_jobs", {"page": page})
    if request.is_mobile:
        return render(
            request,
            "mobile/jobs/list.html",
            {
                "job_list": jobs_list,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "current_url": reverse("internship_jobs"),
                "last_page": no_pages,
                "no_of_jobs": no_of_jobs,
                "show_pop_up": show_pop,
                "internship": True,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "h1_tag": h1_tag,
            },
        )
    return render(
        request,
        "internship.html",
        {
            "jobs_list": jobs_list[:10],
            "cities": City.objects.filter(status="Enabled"),
            "show_pop_up": show_pop,
            "meta_title": meta_title,
            "meta_description": meta_description,
        },
    )


def city_internship_jobs(request, location, **kwargs):
    current_url = reverse("city_internship_jobs", kwargs={"location": location})
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(current_url, permanent=True)
    if "page" in request.GET:
        url = current_url + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    request.session["formdata"] = ""
    location = City.objects.filter(slug=location)
    searched_locations = (
        searched_industry
    ) = searched_skills = searched_edu = searched_states = ""
    if request.POST.get("refine_search") == "True":
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(request.POST)
    else:
        search_dict = QueryDict("", mutable=True)
        search_dict.setlist("job_type", ["internship"])
        search_dict.setlist("refine_location", [location[0].name])

        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(search_dict)

    no_of_jobs = jobs_list.count()
    items_per_page = 20
    no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
    page = get_page_number(request, kwargs, no_pages)
    if not page:
        return HttpResponseRedirect(current_url)

    jobs_list = jobs_list[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    field = get_social_referer(request)
    show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
    meta_title, meta_description, h1_tag = get_meta_data(
        "location_internship_jobs",
        {
            "searched_locations": [location],
            "final_location": [location[0].name],
            "page": page,
        },
    )
    data = {
        "job_list": jobs_list,
        "aft_page": aft_page,
        "after_page": after_page,
        "prev_page": prev_page,
        "previous_page": previous_page,
        "current_page": page,
        "last_page": no_pages,
        "no_of_jobs": no_of_jobs,
        "internship_location": location,
        "current_url": current_url,
        "show_pop_up": show_pop,
        "searched_skills": searched_skills,
        "searched_locations": searched_locations,
        "searched_industry": searched_industry,
        "searched_edu": searched_edu,
        "searched_states": searched_states,
        "searched_experience": request.POST.get("experience"),
        "searched_job_type": "internship",
        "meta_title": meta_title,
        "meta_description": meta_description,
        "h1_tag": h1_tag,
    }
    if request.is_mobile:
        data.update(
            {
                "searched_industry": request.POST.get("industry"),
                "searched_functional_area": request.POST.get("functional_area"),
            }
        )
    template = "mobile/jobs/list.html" if request.is_mobile else "jobs/jobs_list.html"
    return render(request, template, data)


def walkin_jobs(request, **kwargs):
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(reverse("walkin_jobs"), permanent=True)
    if "page" in request.POST:
        url = reverse("walkin_jobs") + request.POST.get("page") + "/"
        return redirect(url, permanent=True)
    request.session["formdata"] = ""
    jobs_list = (
        JobPost.objects.filter(status="Live", job_type="walk-in")
        .select_related("company", "user")
        .prefetch_related("location", "skills", "industry")
    )

    searched_locations = (
        searched_industry
    ) = searched_skills = searched_edu = searched_states = ""
    if request.POST.get("refine_search") == "True":
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(request.POST)

    no_of_jobs = jobs_list.count()
    items_per_page = 20
    no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
    page = get_page_number(request, kwargs, no_pages)
    if not page:
        return HttpResponseRedirect(reverse("walkin_jobs"))

    jobs_list = jobs_list[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    current_date = datetime.now()
    field = get_social_referer(request)
    show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
    meta_title, meta_description, h1_tag = get_meta("walkin_jobs", {"page": page})
    data = {
        "job_list": jobs_list,
        "aft_page": aft_page,
        "after_page": after_page,
        "prev_page": prev_page,
        "previous_page": previous_page,
        "current_page": page,
        "last_page": no_pages,
        "no_of_jobs": no_of_jobs,
        "current_url": reverse("walkin_jobs"),
        "show_pop_up": show_pop,
        "current_date": current_date,
        "searched_skills": searched_skills,
        "searched_locations": searched_locations,
        "searched_industry": searched_industry,
        "searched_edu": searched_edu,
        "searched_states": searched_states,
        "searched_experience": request.POST.get("experience"),
        "searched_job_type": "walk-in",
        "meta_title": meta_title,
        "meta_description": meta_description,
        "h1_tag": h1_tag,
    }
    if request.is_mobile:
        data.update(
            {
                "searched_industry": request.POST.get("industry"),
                "searched_functional_area": request.POST.get("functional_area"),
            }
        )
    template = "mobile/jobs/list.html" if request.is_mobile else "jobs/jobs_list.html"
    return render(request, template, data)


def government_jobs(request, **kwargs):
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(reverse("government_jobs"), permanent=True)
    if "page" in request.GET:
        url = reverse("government_jobs") + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    request.session["formdata"] = ""
    jobs_list = (
        JobPost.objects.filter(status="Live", job_type="government")
        .select_related("company", "user")
        .prefetch_related("location", "skills", "industry")
    )

    no_of_jobs = jobs_list.count()
    items_per_page = 20
    no_pages = int(math.ceil(float(len(jobs_list)) / items_per_page))
    page = get_page_number(request, kwargs, no_pages)
    if not page:
        return HttpResponseRedirect(reverse("government_jobs"))
    jobs_list = jobs_list[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    field = get_social_referer(request)
    show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
    meta_title, meta_description, h1_tag = get_meta("government_jobs", {"page": page})
    data = {
        "job_list": jobs_list,
        "aft_page": aft_page,
        "after_page": after_page,
        "prev_page": prev_page,
        "previous_page": previous_page,
        "current_page": page,
        "last_page": no_pages,
        "no_of_jobs": no_of_jobs,
        "job_type": "government",
        "current_url": reverse("government_jobs"),
        "show_pop_up": show_pop,
        "meta_title": meta_title,
        "meta_description": meta_description,
        "h1_tag": h1_tag,
    }
    template = "mobile/jobs/list.html" if request.is_mobile else "jobs/jobs_list.html"
    return render(request, template, data)


def each_company_jobs(request, company_name, **kwargs):
    current_url = reverse("company_jobs", kwargs={"company_name": company_name})
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(current_url, permanent=True)
    if "page" in request.GET:
        url = current_url + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    company = Company.objects.filter(slug=company_name, is_active=True)
    request.session["formdata"] = ""
    if not company:
        data = {
            "message": "Sorry, no jobs available for " + company_name + " jobs",
            "reason": "Unfortunately, we are unable to locate the job you are looking for",
            "meta_title": "404 - Page Not Found - " + company_name + " - Peeljobs",
            "meta_description": "404 No Jobs available for "
            + company_name
            + " - Peeljobs",
            "data_empty": True,
        }
        if request.user.is_authenticated:
            if str(request.user.user_type) == "RR":
                return render(request, "recruiter/recruiter_404.html", data, status=404)
            elif request.user.is_staff:
                return render(request, "dashboard/404.html", data, status=404)
        template = "mobile/404.html" if request.is_mobile else "404.html"
        return render(request, template, data, status=404)
    else:
        company = company[0]
        items_per_page = 10
        job_list = (
            company.get_jobposts()
            .select_related("company", "user")
            .prefetch_related("location", "skills", "industry")
            .order_by("-published_on")
        )
        no_of_jobs = job_list.count()
        no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
        page = get_page_number(request, kwargs, no_pages)
        if not page:
            return HttpResponseRedirect(current_url)
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        skills = Skill.objects.filter(status="Active")
        industries = Industry.objects.filter(status="Active")[:6]

        jobs_list = job_list[(page - 1) * items_per_page : page * items_per_page]
        field = get_social_referer(request)
        show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
        meta_title = meta_description = h1_tag = ""
        meta = list(db.meta_data.find({"name": "company_jobs"}))
        if meta:
            meta_title = Template(meta[0]["meta_title"]).render(
                Context({"current_page": page, "company": company})
            )
            meta_description = Template(meta[0]["meta_description"]).render(
                Context({"current_page": page, "company": company})
            )
            h1_tag = Template(meta[0]["h1_tag"]).render(
                Context({"current_page": page, "company": company})
            )
        data = {
            "job_list": jobs_list,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "skills": skills,
            "company": company,
            "current_url": current_url,
            "show_pop_up": show_pop,
            "industries": industries,
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
        }
        template = (
            "mobile/jobs/company_jobs.html"
            if request.is_mobile
            else "jobs/company_jobs.html"
        )
        return render(request, template, data)


def companies(request, **kwargs):
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(reverse("companies"), permanent=True)
    if "page" in request.GET:
        url = reverse("companies") + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    companies = (
        Company.objects.annotate(num_posts=Count("jobpost"))
        .filter(is_active=True)
        .order_by("-num_posts")
    )
    alphabet_value = request.POST.get("alphabet_value")
    if alphabet_value:
        companies = companies.filter(name__istartswith=alphabet_value)
    no_of_jobs = companies.count()
    items_per_page = 48
    no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
    page = get_page_number(request, kwargs, no_pages)
    if not page:
        return HttpResponseRedirect(reverse("companies"))

    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    companies = companies[(page - 1) * items_per_page : page * items_per_page]
    meta_title, meta_description, h1_tag = get_meta("companies_list", {"page": page})
    data = {
        "companies": companies,
        "aft_page": aft_page,
        "after_page": after_page,
        "prev_page": prev_page,
        "previous_page": previous_page,
        "current_page": page,
        "last_page": no_pages,
        "no_of_jobs": no_of_jobs,
        "alphabet_value": alphabet_value if alphabet_value else None,
        "current_url": reverse("companies"),
        "meta_title": meta_title,
        "meta_description": meta_description,
        "h1_tag": h1_tag,
    }
    template = (
        "mobile/jobs/companies_list.html"
        if request.is_mobile
        else "jobs/companies_list.html"
    )
    return render(request, template, data)


def get_skills(request):
    skills = cache.get("subscribing_skills")
    if not skills:
        skills = Skill.objects.filter(status="Active").order_by("name")
        skills = serializers.serialize("json", skills)
        cache.set("subscribing_skills", skills, 60 * 60 * 24)
    return HttpResponse(json.dumps({"response": skills}))


def skill_fresher_jobs(request, skill_name, **kwargs):
    current_url = reverse("skill_fresher_jobs", kwargs={"skill_name": skill_name})
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(current_url, permanent=True)
    if "page" in request.GET:
        url = current_url + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    final_skill = get_valid_skills_list(skill_name)
    final_locations = get_valid_locations_list(skill_name)
    if final_locations:
        return redirect(
            reverse("location_fresher_jobs", kwargs={"city_name": skill_name}),
            permanent=True,
        )
    if request.POST.get("refine_search") == "True":
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(request.POST)
    elif final_skill:
        search_dict = QueryDict("", mutable=True)
        search_dict.setlist("refine_skill", final_skill)
        search_dict.update({"job_type": "Fresher"})
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(search_dict)
    else:
        jobs_list = searched_skills = []
    if request.POST.get("q"):
        ip_address = request.META["REMOTE_ADDR"]
        save_search_results.delay(
            ip_address,
            request.POST,
            jobs_list.count() if jobs_list else 0,
            request.user.id,
        )
    if jobs_list:
        no_of_jobs = jobs_list.count()
        items_per_page = 20
        no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
        page = get_page_number(request, kwargs, no_pages)
        if not page:
            return HttpResponseRedirect(current_url)
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        jobs_list = jobs_list[(page - 1) * items_per_page : page * items_per_page]
        field = get_social_referer(request)
        show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
        meta_title, meta_description, h1_tag = get_meta_data(
            "skill_fresher_jobs",
            {
                "skills": searched_skills,
                "fresher": True,
                "final_skill": final_skill,
                "page": page,
            },
        )
        data = {
            "job_list": jobs_list,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "no_of_jobs": no_of_jobs,
            "is_job_list": False,
            "fresher": True,
            "current_url": current_url,
            "show_pop_up": show_pop,
            "searched_skills": searched_skills,
            "searched_locations": searched_locations,
            "searched_industry": searched_industry,
            "searched_edu": searched_edu,
            "searched_states": searched_states,
            "searched_experience": request.POST.get("experience"),
            "searched_job_type": "Fresher",
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
        }
        template = "jobs/jobs_list.html"
        if request.is_mobile:
            data.update(
                {
                    "searched_industry": request.POST.get("industry"),
                    "searched_functional_area": request.POST.get("functional_area"),
                }
            )
            template = "mobile/jobs/list.html"
        return render(request, template, data)
    else:
        meta_title = meta_description = ""
        if searched_skills:
            reason = "Only valid Skill names are accepted in search field"
            skills = final_skill
            status = 200
            meta_title, meta_description = get_404_meta(
                "skill_404", {"skill": skills, "fresher": True}
            )
        else:
            status = 404
            skills = list(filter(None, request.POST.get("q", "").split(", "))) or [
                skill_name
            ]
            reason = "Only valid Skill/city names are accepted"
        template = "mobile/404.html" if request.is_mobile else "404.html"
        return render(
            request,
            template,
            {
                "message": "Unfortunately, we are unable to locate the jobs you are looking for",
                "searched_job_type": "Fresher",
                "job_search": True,
                "reason": reason,
                "searched_skills": skills,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "data_empty": status != 200,
            },
            status=status,
        )


def location_fresher_jobs(request, city_name, **kwargs):
    current_url = reverse("location_fresher_jobs", kwargs={"city_name": city_name})
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(current_url, permanent=True)
    if "page" in request.GET:
        url = current_url + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    state = State.objects.filter(slug__iexact=city_name)
    final_locations = get_valid_locations_list(city_name)
    if request.POST.get("refine_search") == "True":
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(request.POST)
        final_locations = final_locations + list(
            searched_states.values_list("name", flat=True)
        )
    elif state:
        final_locations = [state[0].name]
        search_dict = QueryDict("", mutable=True)
        search_dict.setlist("refine_state", final_locations)
        search_dict.update({"job_type": "Fresher"})
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(search_dict)
    elif final_locations:
        search_dict = QueryDict("", mutable=True)
        search_dict.setlist("refine_location", final_locations)
        search_dict.update({"job_type": "Fresher"})
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(search_dict)
    else:
        jobs_list = searched_locations = []
    if request.POST.get("location") or request.POST.get("q"):
        ip_address = request.META["REMOTE_ADDR"]
        save_search_results.delay(
            ip_address,
            request.POST,
            jobs_list.count() if jobs_list else 0,
            request.user.id,
        )
    if jobs_list:
        no_of_jobs = jobs_list.count()
        items_per_page = 20
        no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
        page = get_page_number(request, kwargs, no_pages)
        if not page:
            return HttpResponseRedirect(current_url)
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        jobs_list = jobs_list[(page - 1) * items_per_page : page * items_per_page]
        field = get_social_referer(request)
        show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
        meta_title, meta_description, h1_tag = get_meta_data(
            "location_fresher_jobs",
            {
                "locations": searched_locations,
                "final_location": set(final_locations),
                "page": page,
                "state": bool(state),
                "fresher": True,
            },
        )
        data = {
            "job_list": jobs_list,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "no_of_jobs": no_of_jobs,
            "is_job_list": False,
            "fresher": True,
            "current_url": current_url,
            "show_pop_up": show_pop,
            "searched_skills": searched_skills,
            "searched_locations": searched_locations,
            "searched_industry": searched_industry,
            "searched_edu": searched_edu,
            "searched_states": searched_states,
            "searched_experience": request.POST.get("experience"),
            "searched_job_type": "Fresher",
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
            "state": state.first(),
        }
        template = "jobs/jobs_list.html"
        if request.is_mobile:
            data.update(
                {
                    "searched_industry": request.POST.get("industry"),
                    "searched_functional_area": request.POST.get("functional_area"),
                }
            )
            template = "mobile/jobs/list.html"
        return render(request, template, data)
    else:
        if final_locations:
            status = 200
            reason = "Only valid cities names are accepted"
            location = final_locations
            meta_title, meta_description = get_404_meta(
                "location_404", {"city": location, "fresher": True}
            )
        else:
            status = 404
            meta_title = meta_description = ""
            location = list(
                filter(None, request.POST.get("location", "").split(", "))
            ) or [city_name]
            reason = "Only valid Skill/city names are accepted"
        template = "mobile/404.html" if request.is_mobile else "404.html"
        return render(
            request,
            template,
            {
                "message": "Unfortunately, we are unable to locate the jobs you are looking for",
                "searched_job_type": "Fresher",
                "job_search": True,
                "reason": reason,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "searched_locations": location,
                "data_empty": status != 200,
            },
            status=status,
        )


def skill_location_walkin_jobs(request, skill_name, **kwargs):
    if "-in-" in request.path:
        current_url = reverse("location_walkin_jobs", kwargs={"skill_name": skill_name})
    else:
        current_url = reverse("skill_walkin_jobs", kwargs={"skill_name": skill_name})
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(current_url, permanent=True)
    if "page" in request.GET:
        url = current_url + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    final_skill = get_valid_skills_list(skill_name)
    final_locations = get_valid_locations_list(skill_name)
    state = State.objects.filter(slug__iexact=skill_name)
    if request.POST.get("refine_search") == "True":
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(request.POST)
        final_locations = final_locations + list(
            searched_states.values_list("name", flat=True)
        )
    elif state:
        searched_locations = state
        final_locations = [state[0].name]
        search_dict = QueryDict("", mutable=True)
        search_dict.setlist("refine_state", final_locations)
        search_dict.update({"job_type": "Walk-in"})
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(search_dict)
    elif final_locations or final_skill:
        search_dict = QueryDict("", mutable=True)
        search_dict.setlist("refine_skill", final_skill)
        search_dict.setlist("refine_location", final_locations)
        search_dict.update({"job_type": "walk-in"})
        if request.POST.get("experience"):
            search_dict.update(
                {"refine_experience_min": request.POST.get("experience")}
            )
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(search_dict)
    else:
        jobs_list = []
    if request.POST.get("location") or request.POST.get("q"):
        ip_address = request.META["REMOTE_ADDR"]
        save_search_results.delay(
            ip_address,
            request.POST,
            jobs_list.count() if jobs_list else 0,
            request.user.id,
        )
    if jobs_list:
        no_of_jobs = jobs_list.count()
        items_per_page = 20
        no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
        page = get_page_number(request, kwargs, no_pages)
        if not page:
            return HttpResponseRedirect(current_url)
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        jobs_list = jobs_list[(page - 1) * items_per_page : page * items_per_page]
        field = get_social_referer(request)
        show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
        if final_locations:
            meta_title, meta_description, h1_tag = get_meta_data(
                "location_walkin_jobs",
                {
                    "locations": searched_locations,
                    "walkin": True,
                    "final_location": set(final_locations),
                    "page": page,
                    "state": bool(state),
                },
            )
        else:
            meta_title, meta_description, h1_tag = get_meta_data(
                "skill_walkin_jobs",
                {
                    "skills": searched_skills,
                    "walkin": True,
                    "final_skill": final_skill,
                    "page": page,
                },
            )
        data = {
            "job_list": jobs_list,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "no_of_jobs": no_of_jobs,
            "is_job_list": False,
            "walkin": True,
            "current_url": current_url,
            "show_pop_up": show_pop,
            "searched_skills": searched_skills,
            "searched_locations": searched_locations,
            "searched_industry": searched_industry,
            "searched_edu": searched_edu,
            "searched_states": searched_states,
            "experience": request.POST.get("experience"),
            "searched_job_type": "walk-in",
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
            "state": state.first(),
        }
        template = "jobs/jobs_list.html"
        if request.is_mobile:
            data.update(
                {
                    "searched_industry": request.POST.get("industry"),
                    "searched_functional_area": request.POST.get("functional_area"),
                }
            )
            template = "mobile/jobs/list.html"
        return render(request, template, data)

    else:
        if "-in-" in request.path:
            if final_locations:
                location, skills = final_locations, []
                status = 200
                meta_title, meta_description = get_404_meta(
                    "location_404", {"city": location, "walkin": True}
                )
            else:
                location, skills = (
                    list(filter(None, request.POST.get("location", "").split(", ")))
                    or [skill_name],
                    [],
                )
                status = 404
                meta_title = meta_description = ""
        else:
            if final_skill:
                skills, location = final_skill, []
                status = 200
                meta_title, meta_description = get_404_meta(
                    "skill_404", {"skill": skills, "walkin": True}
                )
            else:
                status = 404
                skills, location = (
                    list(filter(None, request.POST.get("q", "").split(", ")))
                    or [skill_name],
                    [],
                )
                meta_title = meta_description = ""
        reason = "Only valid Skill/City names are accepted in search field"
        template = "mobile/404.html" if request.is_mobile else "404.html"
        return render(
            request,
            template,
            {
                "message": "Unfortunately, we are unable to locate the jobs you are looking for",
                "searched_job_type": "walk-in",
                "job_search": True,
                "reason": reason,
                "searched_skills": skills,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "searched_locations": location,
                "data_empty": status != 200,
            },
            status=status,
        )


def skill_location_wise_fresher_jobs(request, skill_name, city_name, **kwargs):
    current_url = reverse(
        "skill_location_wise_fresher_jobs",
        kwargs={"skill_name": skill_name, "city_name": city_name},
    )
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(current_url, permanent=True)
    if "page" in request.GET:
        url = current_url + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    final_skill = get_valid_skills_list(skill_name)
    final_location = get_valid_locations_list(city_name)
    if request.POST.get("refine_search") == "True":
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(request.POST)
    elif final_skill and final_location:
        search_dict = QueryDict("", mutable=True)
        search_dict.setlist("refine_skill", final_skill)
        search_dict.setlist("refine_location", final_location)
        search_dict.update({"job_type": "Fresher"})
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(search_dict)
    else:
        jobs_list = []
    if request.POST.get("location") or request.POST.get("q"):
        ip_address = request.META["REMOTE_ADDR"]
        save_search_results.delay(
            ip_address,
            request.POST,
            jobs_list.count() if jobs_list else 0,
            request.user.id,
        )
    if jobs_list:
        no_of_jobs = jobs_list.count()
        items_per_page = 20
        no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
        page = get_page_number(request, kwargs, no_pages)
        if not page:
            return HttpResponseRedirect(current_url)
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        jobs_list = jobs_list[(page - 1) * items_per_page : page * items_per_page]
        field = get_social_referer(request)
        show_pop = True if field == "fb" or field == "tw" or field == "ln" else False
        meta_title, meta_description, h1_tag = get_meta_data(
            "skill_location_fresher_jobs",
            {
                "skills": searched_skills,
                "locations": searched_locations,
                "final_location": final_location,
                "final_skill": final_skill,
                "page": page,
            },
        )
        data = {
            "job_list": jobs_list,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "no_of_jobs": no_of_jobs,
            "is_job_list": False,
            "show_pop_up": show_pop,
            "current_url": current_url,
            "searched_skills": searched_skills,
            "searched_locations": searched_locations,
            "searched_industry": searched_industry,
            "searched_edu": searched_edu,
            "searched_states": searched_states,
            "searched_experience": request.POST.get("experience"),
            "searched_job_type": "Fresher",
            "fresher": True,
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
        }
        template = "jobs/jobs_list.html"
        if request.is_mobile:
            data.update(
                {
                    "searched_industry": request.POST.get("industry"),
                    "searched_functional_area": request.POST.get("functional_area"),
                }
            )
            template = "mobile/jobs/list.html"
        return render(request, template, data)
    else:
        status = 200 if final_skill and final_location else 404
        reason = "Only valid Skill names are accepted in search field"
        skills = (
            final_skill
            or list(filter(None, request.POST.get("q", "").split(", ")))
            or [skill_name]
        )
        location = (
            final_location
            or list(filter(None, request.POST.get("location", "").split(", ")))
            or [city_name]
        )
        template = "mobile/404.html" if request.is_mobile else "404.html"
        if status == 200:
            meta_title, meta_description = get_404_meta(
                "skill_location_404",
                {"skill": skills, "city": location, "fresher": True},
            )
        else:
            meta_title = meta_description = ""
        return render(
            request,
            template,
            {
                "message": "Unfortunately, we are unable to locate the jobs you are looking for",
                "searched_job_type": "Fresher",
                "job_search": True,
                "reason": reason,
                "searched_skills": skills,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "searched_locations": location,
                "data_empty": status != 200,
            },
            status=status,
        )


def add_other_location_to_user(user, request):
    location = City.objects.filter(
        name__iexact=request.POST.get("other_location").strip()
    )
    if location:
        user.current_city = location[0]
    else:
        location = City.objects.create(
            name=request.POST.get("other_location"),
            status="Disabled",
            slug=slugify(request.POST.get("other_location")),
            state=State.objects.get(id=16),
        )
        user.current_city = location
    user.save()


def register_using_email(request):
    if request.method == "POST":
        if request.FILES.get("get_resume"):
            handle_uploaded_file(
                request.FILES["get_resume"], request.FILES["get_resume"].name
            )
            email, mobile, text = get_resume_data(request.FILES["get_resume"])
            data = {
                "error": False,
                "resume_email": email,
                "resume_mobile": mobile,
                "text": text,
            }
            return HttpResponse(json.dumps(data))
        validate_user = UserEmailRegisterForm(request.POST, request.FILES)
        if validate_user.is_valid():
            if not (
                User.objects.filter(email__iexact=request.POST.get("email"))
                or User.objects.filter(username__iexact=request.POST.get("email"))
            ):
                email = request.POST.get("email")
                password = request.POST.get("password")
                registered_from = request.POST.get("register_from", "Email")
                user = User.objects.create(
                    username=email,
                    email=email,
                    user_type="JS",
                    registered_from=registered_from,
                )
                user = UserEmailRegisterForm(request.POST, instance=user)
                user = user.save(commit=False)
                if request.POST.get("other_loc"):
                    add_other_location_to_user(user, request)
                user.email_notifications = (
                    request.POST.get("email_notifications") == "on"
                )
                user.set_password(password)
                user.referer = request.session.get("referer", "")
                user.save()
                save_codes_and_send_mail(user, request, password)
                if "resume" in request.FILES:
                    conn = tinys3.Connection(
                        settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY
                    )
                    random_string = "".join(
                        random.choice("0123456789ABCDEF") for i in range(3)
                    )
                    user_id = str(user.id) + str(random_string)
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
                    user.resume = path
                    user.profile_updated = datetime.now(timezone.utc)
                    user.save()
                registered_user = authenticate(username=user.username)
                if registered_user:
                    login(request, registered_user)
                UserEmail.objects.create(user=user, email=email, is_primary=True)
                redirect_url = reverse("user_reg_success")
                if request.POST.get("detail_page"):
                    redirect_url = request.POST.get("detail_page")
                data = {
                    "error": False,
                    "response": "Registered Successfully",
                    "redirect_url": redirect_url,
                }
                return HttpResponse(json.dumps(data))
            else:
                data = {
                    "error": True,
                    "response": "User With This Email Already exists ",
                }
                return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "response": validate_user.errors}
            return HttpResponse(json.dumps(data))
    return HttpResponseRedirect("/index")


def user_activation(request, user_id):
    user = User.objects.filter(activation_code__iexact=str(user_id))
    if user:
        usr = user[0]
        registered_user = authenticate(username=usr.username)
        if registered_user:
            login(request, registered_user)
            url = "/profile/" if usr.is_active else "/profile/?verify=true"
            usr.is_active = True
            usr.email_verified = True
            usr.save()
            return HttpResponseRedirect(url)
    else:
        message = "Looks like Activation Url Expired"
        reason = "The URL may be misspelled or the user you're looking for is no longer available."
        template = "mobile/404.html" if request.is_mobile else "404.html"
        return render(
            request, template, {"message": message, "reason": reason}, status=404
        )


def login_user_email(request):
    if request.method == "POST":
        validate_user = AuthenticationForm(request.POST)
        if validate_user.is_valid():
            email = request.POST.get("email")
            password = request.POST.get("password")
            usr = authenticate(username=email, password=password)
            if usr:
                usr.last_login = datetime.now()
                usr.save()
                login(request, usr)
                data = {"error": False, "response": "Logged In Successfully"}
                data["redirect_url"] = "/profile/"
                if request.user.user_type == "JS" and request.session.get("job_id"):
                    post = JobPost.objects.filter(
                        id=request.session["job_id"], status="Live"
                    ).first()
                    if (
                        post
                        and usr.is_active
                        and usr.profile_completion_percentage >= 50
                        or usr.resume
                    ):
                        job_apply(request, request.session["job_id"])
                        data["redirect_url"] = (
                            post.get_absolute_url() + "?job_apply=applied"
                            if post
                            else "/"
                        )
                    else:
                        url = post.slug + "?job_apply=apply" if post else "/profile/"
                        data["redirect_url"] = url
                elif request.user.is_recruiter or request.user.is_agency_recruiter:
                    data["redirect_url"] = "/recruiter/"
                else:
                    data["redirect_url"] = "/dashboard/"
                if request.POST.get("next"):
                    data["redirect_url"] = request.POST.get("next")
                if request.POST.get("detail_page"):
                    data["rediret_url"] = request.POST.get("detail_page")
            else:
                data = {
                    "error": True,
                    "response_message": "Username Password didn't match",
                }
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "response": validate_user.errors}
            return HttpResponse(json.dumps(data))
    return HttpResponseRedirect("/")


def set_password(request, user_id, passwd):
    user = User.objects.filter(id=user_id)
    if request.method == "POST":
        validate_changepassword = UserPassChangeForm(request.POST)
        if validate_changepassword.is_valid():
            if request.POST["new_password"] != request.POST["retype_password"]:
                return HttpResponse(
                    json.dumps(
                        {
                            "error": True,
                            "response_message": "Password and ConfirmPasswords did not match",
                        }
                    )
                )
            user = user[0]
            user.set_password(request.POST["new_password"])
            user.save()
            usr = authenticate(
                username=user.email, password=request.POST["new_password"]
            )
            if usr:
                usr.last_login = datetime.now()
                usr.save()
                login(request, usr)
            if user.user_type == "JS":
                url = "/profile/"
            else:
                url = reverse("recruiter:list")
            return HttpResponse(
                json.dumps(
                    {
                        "error": False,
                        "message": "Password changed successfully",
                        "url": url,
                    }
                )
            )
        else:
            return HttpResponse(
                json.dumps({"error": True, "response": validate_changepassword.errors})
            )
    if user:
        usr = authenticate(username=user[0].username, password=passwd)
        if usr:
            return render(request, "set_password.html")
    template = "mobile/404.html" if request.is_mobile else "404.html"
    return render(
        request,
        template,
        {"message": "Not Found", "reason": "URL may Expired"},
        status=404,
    )


def forgot_password(request):
    form_valid = ForgotPassForm(request.POST)
    if form_valid.is_valid():
        user = User.objects.filter(email=request.POST.get("email")).first()
        if user:
            new_pass = get_random_string(length=10).lower()
            user.set_password(new_pass)
            user.save()
            temp = loader.get_template("email/subscription_success.html")
            subject = "Password Reset - PeelJobs"
            mto = request.POST.get("email")
            mfrom = settings.DEFAULT_FROM_EMAIL
            url = (
                request.scheme
                + "://"
                + request.META["HTTP_HOST"]
                + "/user/set_password/"
                + str(user.id)
                + "/"
                + str(new_pass)
                + "/"
            )
            c = {"randpwd": new_pass, "user": user, "redirect_url": url}
            rendered = temp.render(c)
            user_active = True if user.is_active else False
            Memail(mto, mfrom, subject, rendered, user_active)
            data = {"error": False, "response": "Success", "redirect_url": "/"}
        else:
            data = {
                "error": True,
                "response_message": "User doesn't exist with this Email",
            }
        return HttpResponse(json.dumps(data))
    data = {"error": True, "response": form_valid.errors}
    return HttpResponse(json.dumps(data))


@jobseeker_login_required
def user_reg_success(request):
    if not request.user.is_authenticated:
        reason = "The URL may be misspelled or the page you're looking for is no longer available."
        template = "mobile/404.html" if request.is_mobile else "404.html"
        return render(
            request,
            template,
            {"message": "Sorry, Page Not Found", "reason": reason},
            status=404,
        )
    if request.method == "POST":
        validate_user = UserEmailRegisterForm(
            request.POST, request.FILES, instance=request.user
        )
        if validate_user.is_valid():
            user = validate_user.save(commit=False)
            while True:
                unsubscribe_code = get_random_string(length=15)
                if not User.objects.filter(unsubscribe_code__iexact=unsubscribe_code):
                    break
            user.unsubscribe_code = unsubscribe_code
            user.save()
            for s in request.POST.getlist("technical_skills"):
                skill = Skill.objects.filter(id=s)
                if skill:
                    skill = skill[0]
                    tech_skill = TechnicalSkill.objects.create(skill=skill)
                    user.skills.add(tech_skill)
            if "resume" in request.FILES:
                conn = tinys3.Connection(
                    settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY
                )
                random_string = "".join(
                    random.choice("0123456789ABCDEF") for i in range(3)
                )
                user_id = str(user.id) + str(random_string)
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
                user.resume = path
            user.profile_updated = datetime.now(timezone.utc)
            user.save()
            data = {"error": False, "response": "Profile Updated Successfully"}
            return HttpResponse(json.dumps(data))
        data = {"error": True, "response": validate_user.errors}
        return HttpResponse(json.dumps(data))
    if request.user.registered_from == "Social" and not request.user.mobile:
        template_name = (
            "mobile/profile/social_register.html"
            if request.is_mobile
            else "candidate/social_register.html"
        )
        return render(request, template_name)
    template = (
        "mobile/profile/user_reg_success.html"
        if request.is_mobile
        else "candidate/user_reg_success.html"
    )
    return render(request, template)


def user_subscribe(request):
    skills = Skill.objects.filter(status="Active")
    if request.method == "POST":
        validate_subscribe = SubscribeForm(request.POST)
        email = request.POST.get("email")
        user = User.objects.filter(email__iexact=email).first()
        if user and not user.user_type == "JS":
            data = {
                "error": True,
                "response_message": "Admin is not allowed to Subscribe"
                if user.is_staff
                else "Recruiter/Agency is not allowed to Subscribe",
            }
            return HttpResponse(json.dumps(data))
        if validate_subscribe.is_valid():
            all_subscribers = (
                Subscriber.objects.filter(user=request.user)
                if request.user.is_authenticated
                else Subscriber.objects.filter(email=email, user=None)
            )
            if request.POST.get("subscribe_from"):
                if not all_subscribers:
                    for skill in skills:
                        sub_code = subscribers_creation_with_skills(
                            email,
                            skill,
                            request.user if request.user.is_authenticated else "",
                        )
                    data = {"error": False, "response": "Successfully Subscribed"}
                else:
                    data = {
                        "error": True,
                        "response_message": "User with this email id already subscribed",
                    }
            elif request.POST.getlist("skill"):
                all_subscribers = all_subscribers.filter(
                    skill__in=request.POST.getlist("skill")
                )
                if int(all_subscribers.count()) != int(
                    len(request.POST.getlist("skill"))
                ):
                    for skill in request.POST.getlist("skill"):
                        skill = Skill.objects.get(id=skill)
                        sub_code = subscribers_creation_with_skills(
                            email,
                            skill,
                            request.user if request.user.is_authenticated else "",
                        )
                    data = {"error": False, "response": "experience added"}
                else:
                    data = {
                        "error": True,
                        "response_message": "User with this email id and skill(s) already subscribed",
                    }
            else:
                data = {
                    "error": True,
                    "response_message": "Please Enter atleast one skill",
                }
            if not data.get("error"):
                t = loader.get_template("email/subscription_success.html")
                skills = Skill.objects.filter(id__in=request.POST.getlist("skill"))
                url = (
                    request.scheme
                    + "://"
                    + request.META["HTTP_HOST"]
                    + "/subscriber/verification/"
                    + str(sub_code)
                    + "/"
                )
                c = {"user_email": email, "skills": skills, "redirect_url": url}
                subject = "PeelJobs New Subscription"
                rendered = t.render(c)
                mfrom = settings.DEFAULT_FROM_EMAIL
                Memail([email], mfrom, subject, rendered, False)
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "response": validate_subscribe.errors}
            return HttpResponse(json.dumps(data))
    return HttpResponseRedirect("/")


def process_email(request):
    body_unicode = request.body.decode("utf-8")
    body = json.loads(body_unicode)
    search = re.search(r"[\w\.-]+@[\w\.-]+", body.get("Message"))
    if search:
        email = search.group(0)
        users = User.objects.filter(email__iexact=email)
        if not users:
            user = User.objects.create(
                username=email, email=email, user_type="JS", registered_from="Careers"
            )
            randpwd = rand_string(size=10).lower()
            user.set_password(randpwd)
            user.save()
            save_codes_and_send_mail(user, request, randpwd)
    return HttpResponseRedirect("/")
