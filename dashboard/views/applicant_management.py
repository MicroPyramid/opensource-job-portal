import json
import math
import re
from datetime import datetime

from django.db.models import Q
from django.urls import reverse
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from mpcomp.views import (
    get_prev_after_pages_count,
    permission_required,
)
from peeldb.models import (
    AppliedJobs,
    JobAlert,
    Subscriber,
    User,
)


# Functions to move here from main views.py:


@permission_required("activity_view", "activity_edit")
def applicants(request, status="all"):
    applicant = User.objects.filter(user_type="JS")
    if status == "social":
        applicant = User.objects.filter(user_type="JS", registered_from="Social")
    if status == "email":
        applicant = User.objects.filter(user_type="JS", registered_from="Email")
    if status == "resume":
        applicant = User.objects.filter(user_type="JS", registered_from="Resume")
    if status == "resume-pool":
        applicant = User.objects.filter(user_type="JS", registered_from="ResumePool")
    if request.GET.get("profile_completed"):
        applicant = applicant.filter(profile_completeness__gte=50)
    if request.GET.get("resume_uploaded"):
        applicant = applicant.filter().exclude(resume="")
    if request.GET.get("login_once"):
        applicant = applicant.filter(is_login=False)
    if request.GET.get("appliedto_jobs"):
        applicant = applicant.filter(
            id__in=AppliedJobs.objects.filter().values_list("user", flat=True)
        )
    if request.GET.get("active"):
        applicant = applicant.filter(is_active=True)

    if request.GET.get("inactive"):
        applicant = applicant.filter(is_active=False)

    if request.POST.get("search"):
        applicant = applicant.filter(
            Q(email__icontains=request.POST.get("search"))
            | Q(username__icontains=request.POST.get("search"))
            | Q(referer__contains=request.POST.get("search"))
        )
    search_location = request.POST.getlist("location")
    search_skills = request.POST.getlist("skills")
    if search_location:
        applicant = applicant.filter(current_city__id__in=search_location)
    if search_skills:
        applicant = applicant.filter(skills__skill__id__in=search_skills)
    if request.POST.get("profile_completion"):
        applicant = applicant.filter(
            profile_completeness__gte=int(request.POST.get("profile_completion"))
        )
    if request.POST.get("timestamp"):
        date = request.POST.get("timestamp").split(" - ")
        start_date = datetime.strptime(date[0], "%b %d, %Y %H:%M")
        end_date = datetime.strptime(date[1], "%b %d, %Y %H:%M")
        applicant = applicant.filter(date_joined__range=(start_date, end_date))
    applicant = applicant.order_by("-date_joined")
    items_per_page = 50
    no_pages = int(math.ceil(float(applicant.count()) / items_per_page))
    if (
        "page" in request.POST
        and bool(re.search(r"[0-9]", request.POST.get("page")))
        and int(request.POST.get("page")) > 0
    ):
        if int(request.POST.get("page")) > (no_pages + 2):
            return HttpResponseRedirect(reverse("dashboard:applicants"))
        page = int(request.POST.get("page"))
    else:
        page = 1

    applicant = applicant[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    return render(
        request,
        "dashboard/jobseeker/list.html",
        {
            "applicants": applicant,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "status": status,
            "search_skills": search_skills,
            "search_location": search_location,
        },
    )


@permission_required("activity_view", "activity_edit")
def view_applicant(request, user_id):
    applicants = User.objects.filter(id=user_id)
    if applicants:
        return render(
            request, "dashboard/jobseeker/view.html", {"applicant": applicants[0]}
        )
    message = "Sorry, the page you requested can not be found"
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "dashboard/404.html",
        {"message_type": "404", "message": message, "reason": reason},
        status=404,
    )


@permission_required("activity_view", "activity_edit")
def applicant_actions(request, user_id):
    job_seeker_obj = get_object_or_404(User, id=user_id)
    if request.GET.get("action_type") == "delete":
        job_seeker_obj.delete()
        Subscriber.objects.filter(
            Q(user=job_seeker_obj) | Q(email=job_seeker_obj.email)
        ).delete()
        JobAlert.objects.filter(email=job_seeker_obj.email).delete()
    elif request.GET.get("action_type") == "disable":
        job_seeker_obj.is_active = False
        job_seeker_obj.save()
    elif request.GET.get("action_type") == "enable":
        job_seeker_obj.is_active = True
        job_seeker_obj.save()
    data = {"error": False}
    return HttpResponse(json.dumps(data))
