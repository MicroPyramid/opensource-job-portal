from django.shortcuts import render
from django.core.cache import cache
from django.db.models import Q

from mpcomp.views import get_social_referer, get_meta
from peeldb.models import JobPost, State, JOB_TYPE


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
