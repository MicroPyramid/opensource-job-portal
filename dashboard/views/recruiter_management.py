import math
import re
from datetime import datetime

from django.urls import reverse
from django.db.models import Count, Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from mpcomp.views import (
    get_prev_after_pages_count,
    permission_required,
)
from peeldb.models import (
    JobPost,
    User,
)


# Functions to move here from main views.py:

@permission_required("activity_view", "activity_edit")
def recruiters_list(request, status):
    if str(status) == "inactive":
        recruiters = User.objects.filter(user_type="RR", is_active=False).order_by(
            "-date_joined"
        )
    else:
        recruiters = User.objects.filter(user_type="RR", is_active=True).order_by(
            "-date_joined"
        )
    alphabet_value = request.POST.get("alphabet_value")
    if alphabet_value:
        recruiters = recruiters.filter(email__istartswith=alphabet_value)
    if request.POST.get("search"):
        recruiters = recruiters.filter(
            Q(email__icontains=request.POST.get("search"))
            | Q(username__icontains=request.POST.get("search"))
        )
    if request.POST.get("timestamp"):
        date = request.POST.get("timestamp").split(" - ")
        start_date = datetime.strptime(date[0], "%b %d, %Y %H:%M")
        end_date = datetime.strptime(date[1], "%b %d, %Y %H:%M")
        recruiters = recruiters.filter(date_joined__range=(start_date, end_date))
    items_per_page = 10
    no_pages = int(math.ceil(float(recruiters.count()) / items_per_page))
    page = request.POST.get("page") or request.GET.get("page")
    try:
        page = 1 if int(page) > (no_pages + 1) else int(page)
    except:
        page = 1
    recruiters = recruiters[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    return render(
        request,
        "dashboard/recruiters/list.html",
        {
            "recruiters": recruiters,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "status": status,
        },
    )


@permission_required("activity_view", "activity_edit")
def view_recruiter(request, user_id):
    recruiter = User.objects.filter(id=user_id).first()
    agency_recruiters = []
    if recruiter.is_agency_admin:
        agency_recruiters = User.objects.filter(company=recruiter.company).exclude(
            id=recruiter.id
        )
    if recruiter.agency_admin:
        jobposts = JobPost.objects.filter(user__company=recruiter.company).annotate(
            responses=Count("appliedjobs")
        )
    elif recruiter.is_agency_recruiter:
        jobposts = (
            JobPost.objects.filter(Q(agency_recruiters=recruiter) | Q(user=recruiter))
            .annotate(responses=Count("appliedjobs"))
            .distinct()
        )
    else:
        jobposts = JobPost.objects.filter(user=recruiter).annotate(
            responses=Count("appliedjobs")
        )
    items_per_page = 10
    no_pages = int(math.ceil(float(jobposts.count()) / items_per_page))
    page = request.GET.get("page")
    if page and bool(re.search(r"[0-9]", page)) and int(page) > 0:
        if int(page) > (no_pages + 2):
            return HttpResponseRedirect(reverse("dashboard:functional_areas"))
        page = int(page)
    else:
        page = 1

    jobposts = jobposts[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    return render(
        request,
        "dashboard/recruiters/view.html",
        {
            "recruiter": recruiter,
            "posts": jobposts,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "agency_recruiters": agency_recruiters,
            "last_page": no_pages,
        },
    )





@permission_required("activity_edit")
def recruiter_status_change(request, user_id):
    recruiter = User.objects.get(id=user_id)
    if recruiter.is_active:
        recruiter.is_active = False
        recruiter.save()
    else:
        recruiter.is_active = True
        recruiter.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))




@permission_required("activity_edit")
def recruiter_paid_status_change(request, user_id):
    recruiter = User.objects.get(id=user_id)
    if recruiter.is_paid:
        recruiter.is_paid = False
        recruiter.save()
    else:
        recruiter.is_paid = True
        recruiter.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))




@permission_required("activity_edit")
def recruiter_delete(request, user_id):
    recruiter = get_object_or_404(User, id=user_id)
    if recruiter.is_active:
        status = "active"
    else:
        status = "inactive"
    page = request.POST.get("page")
    recruiter.delete()
    url = (
        reverse("dashboard:recruiters_list", kwargs={"status": status})
        + "?page="
        + page
    )
    return HttpResponseRedirect(url)
