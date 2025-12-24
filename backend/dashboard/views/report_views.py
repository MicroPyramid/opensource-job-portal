import json
import math
import re
from datetime import datetime

from django.urls import reverse
from django.db.models import Count, Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import render

from mpcomp.views import (
    get_prev_after_pages_count,
    permission_required,
)
from peeldb.models import (
    City,
    JobPost,
    SearchResult,
    Skill,
    Subscriber,
    User,
)


@permission_required("activity_view", "activity_edit")
def reports(request):
    cities = City.objects.filter()
    skills = [
        "java",
        "html",
        "php",
        "android",
        ".net",
        "bpo",
        "testing",
        "javascript",
        "c#",
        "adobe photoshop",
        "fresher",
        "css",
        "mysql",
        "j2ee",
        "sql server",
        "sales",
        "marketing",
        "accounting",
        "technical support",
        "python",
    ]
    all_skills = Skill.objects.filter()
    location = []
    jobs_location = []

    job_posts = []
    active_recruiters = []
    inactive_recruiters = []
    skills_names = []
    skill_wise_jobs_count = []
    for city in cities:
        users = User.objects.filter(city=city).exclude(user_type="JS")
        if request.method == "POST" and request.POST.get("timestamp"):
            date = request.POST.get("timestamp").split(" - ")
            start_date = datetime.strptime(date[0], "%b %d, %Y %H:%M")
            end_date = datetime.strptime(date[1], "%b %d, %Y %H:%M")
            users = users.filter(date_joined__range=(start_date, end_date))
        if users:
            location.append(str(city.name))
            active_recruiters.append(int(users.filter(is_active=True).count()))
            inactive_recruiters.append(int(users.filter(is_active=False).count()))
        jobs = JobPost.objects.filter(location__in=[city], status="Live")
        if request.method == "POST" and request.POST.get("timestamp"):

            date = request.POST.get("timestamp").split(" - ")
            start_date = datetime.strptime(date[0], "%b %d, %Y %H:%M")
            end_date = datetime.strptime(date[1], "%b %d, %Y %H:%M")

            jobs = jobs.filter(published_on__range=(start_date, end_date))

        if jobs:
            jobs_location.append(str(city.name))
            job_posts.append(jobs.count())
    if request.POST.getlist("skills"):
        skills = Skill.objects.filter(
            id__in=request.POST.getlist("skills")
        ).values_list("name", flat=True)
    for skill in skills:
        skill = Skill.objects.filter(name__iexact=skill)
        jobs_skills = JobPost.objects.filter(skills__in=skill, status="Live")
        if request.method == "POST" and request.POST.get("timestamp"):

            date = request.POST.get("timestamp").split(" - ")
            start_date = datetime.strptime(date[0], "%b %d, %Y %H:%M")
            end_date = datetime.strptime(date[1], "%b %d, %Y %H:%M")

           

            jobs_skills = jobs_skills.filter(published_on__range=(start_date, end_date))
        if jobs_skills:
            skills_names.append(skill[0].name)
            skill_wise_jobs_count.append(jobs_skills.count())

    return render(
        request,
        "dashboard/reports.html",
        {
            "location": json.dumps(location),
            "job_posts": json.dumps(job_posts),
            "cities": cities,
            "skills": skills,
            "active_recruiters": json.dumps(active_recruiters),
            "inactive_recruiters": json.dumps(inactive_recruiters),
            "skill_wise_jobs_count": json.dumps(skill_wise_jobs_count),
            "skills_names": json.dumps(skills_names),
            "all_skills": all_skills,
            "selected_skills": request.POST.getlist("skills"),
            "jobs_location": json.dumps(jobs_location),
        },
    )



@permission_required("activity_view", "activity_edit")
def search_log(request):
    search_logs = SearchResult.objects.all().order_by("-search_on")
    items_per_page = 500
    no_pages = int(math.ceil(float(len(search_logs)) / items_per_page))

    if (
        "page" in request.GET
        and bool(re.search(r"[0-9]", request.GET.get("page")))
        and int(request.GET.get("page")) > 0
    ):
        if int(request.GET.get("page")) > (no_pages + 2):
            return HttpResponseRedirect(reverse("dashboard:search_log"))
        page = int(request.GET.get("page"))
    else:
        page = 1

    search_logs = search_logs[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    return render(
        request,
        "dashboard/search/list.html",
        {
            "search_logs": search_logs,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
        },
    )


@permission_required("activity_view", "activity_edit")
def view_search_log(request, search_log_id):
    search_logs = SearchResult.objects.filter(id=search_log_id)
    if search_logs:
        search_log = search_logs[0]
        return render(request, "dashboard/search/view.html", {"search_log": search_log})
    return render(request, "dashboard/404.html", status=404)




@permission_required("activity_view", "activity_edit")
def subscribers(request):
    subscribers = Subscriber.objects.values_list("skill_id", flat=True).distinct()
    skills = []
    for each in subscribers:
        skill = Skill.objects.get(id=each)
        skills.append(skill)
    return render(request, "dashboard/subscribers/list.html", {"skills": skills})


@permission_required("activity_view", "activity_edit")
def view_subscribers(request, skill_id):
    subscribers = Subscriber.objects.filter(skill_id=skill_id)
    return render(
        request, "dashboard/subscribers/view.html", {"subscribers": subscribers}
    )




@permission_required("activity_edit", "activity_view")
def search_summary(request, search_type):
    values = []
    count = []
    if request.POST.get("timestamp"):
        date = request.POST.get("timestamp").split(" - ")
        start_date = datetime.strptime(date[0], "%b %d, %Y %H:%M")
        end_date = datetime.strptime(date[1], "%b %d, %Y %H:%M")
    if search_type == "other-skills":
        summary = (
            SearchResult.objects.exclude(other_skill="")
            .values("other_skill")
            .annotate(num=Count("other_skill"))
            .order_by("-num")
        )
        if request.POST.get("search"):
            search = request.POST.get("search")
            summary = summary.filter(other_skill=search)
        if request.POST.get("timestamp"):
            summary = summary.filter(search_on__range=(start_date, end_date))
        for each in summary[:20]:
            values.append(each["other_skill"])
            count.append(each["num"])
    elif search_type == "other-locations":
        summary = (
            SearchResult.objects.exclude(other_location="")
            .values("other_location")
            .annotate(num=Count("other_location"))
            .order_by("-num")
        )
        if request.POST.get("search"):
            search = request.POST.get("search")
            summary = summary.filter(other_location=search)
        if request.POST.get("timestamp"):
            summary = summary.filter(search_on__range=(start_date, end_date))
        for each in summary[:20]:
            values.append(each["other_location"])
            count.append(each["num"])
    elif search_type == "skills":
        summary = (
            SearchResult.objects.values("skills__name")
            .annotate(num=Count("skills"))
            .order_by("-num")
        )
        if request.POST.get("search"):
            search = request.POST.get("search").split(",")
            summary = summary.filter(
                Q(skills__name__in=search) | Q(skills__slug__in=search)
            )
        if request.POST.get("timestamp"):
            summary = summary.filter(search_on__range=(start_date, end_date))
        for each in summary[:20]:
            values.append(each["skills__name"])
            count.append(each["num"])
    else:
        summary = (
            SearchResult.objects.values("locations__name")
            .annotate(num=Count("locations"))
            .order_by("-num")
        )
        if request.POST.get("search"):
            search = request.POST.get("search").split(",")
            summary = summary.filter(
                Q(locations__name__in=search) | Q(locations__slug__in=search)
            )
        if request.POST.get("timestamp"):
            summary = summary.filter(search_on__range=(start_date, end_date))
        for each in summary[:20]:
            values.append(each["locations__name"])
            count.append(each["num"])
    return render(
        request,
        "dashboard/search_summary.html",
        {
            "values": json.dumps(values),
            "count": json.dumps(count),
            "search_type": search_type,
        },
    )

