"""
Application Management Views
Handles job application management and applicant interactions
"""
import json
from datetime import datetime

from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.template import loader
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q, Count

from dashboard.tasks import send_email
from mpcomp.views import recruiter_login_required, get_prev_after_pages_count

from peeldb.models import (
    JobPost,
    AppliedJobs,
    User,
    UserMessage,
    AgencyResume,
    AGENCY_RECRUITER_JOB_TYPE,
)

from ..forms import (
    ApplicantResumeForm,
)


# Application Management Views will be moved here
# TODO: Move the following functions from the main views.py:
# - applicants()
# - Related parts of view_job() that handle applicant management




@recruiter_login_required
def applicants(request, job_post_id):
    if request.method == "GET":
        reason = "The URL may be misspelled or the page you're looking for is no longer available."
        return render(
            request,
            "recruiter/recruiter_404.html",
            {
                "message_type": "404",
                "message": "Looks like you can't access this page",
                "reason": reason,
            },
            status=404,
        )
    jobpost = JobPost.objects.filter(id=job_post_id)
    if jobpost:
        user_id = request.POST.get("user_id").split("user_status_")[-1]
        if request.POST.get("type") == "resume":
            user = (
                AppliedJobs.objects.filter(
                    resume_applicant_id=user_id, job_post_id=job_post_id
                )
                .prefetch_related("resume_applicant")
                .first()
            )
        else:
            user = (
                AppliedJobs.objects.filter(user_id=user_id, job_post_id=job_post_id)
                .prefetch_related("user")
                .first()
            )
        prev_status = user.status
        user.status = request.POST.get("status")
        user.save()
        next_count = AppliedJobs.objects.filter(
            job_post_id=job_post_id, status=request.POST.get("status")
        ).count()
        prev_count = AppliedJobs.objects.filter(
            job_post_id=job_post_id, status=prev_status
        ).count()
        temp = loader.get_template("email/applicant_apply_job.html")
        subject = "Application Status - PeelJobs"
        if request.POST.get("type") == "resume":
            mto = [user.resume_applicant.email]
        else:
            mto = [user.user.email]
        if request.POST.get("type") == "resume":
            names_dict = {
                "job_post": jobpost[0],
                "user_email": user.resume_applicant.email,
                "user_status": user.status,
                "name": user.resume_applicant.candidate_name,
            }
        else:
            names_dict = {
                "job_post": jobpost[0],
                "user_email": user.user.email,
                "user_status": user.status,
                "name": user.user.get_full_name(),
            }
        rendered = temp.render(names_dict)
        send_email.delay(mto, subject, rendered)
        data = {
            "error": False,
            "response": "Applicant Status changed to " + user.status,
            "prev_count": prev_count,
            "next_count": next_count,
            "prev_status": prev_status,
            "next_status": user.status,
        }
        return HttpResponse(json.dumps(data))
    return HttpResponse(
        json.dumps({"error": True, "response": "Something went wrong!"})
    )
