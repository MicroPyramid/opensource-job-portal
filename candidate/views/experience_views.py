import datetime
import json
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from zoneinfo import ZoneInfo

from candidate.forms import WorkExperienceForm
from peeldb.models import EmploymentHistory


@login_required
def add_experience(request):
    if request.method == "GET":
        template = "candidate/add_experience.html"
        return render(request, template)
    work_experience = WorkExperienceForm(request.POST)
    if work_experience.is_valid():
        if request.user.employment_history.filter(
            company=request.POST.get("company"),
            designation=request.POST.get("designation"),
        ):
            data = {
                "error": True,
                "response_message": "Experince with this company and designation already exists",
            }
            return HttpResponse(json.dumps(data))
        experience = work_experience.save(commit=False)
        if request.POST.get("current_job") == "on":
            current_job = True
        else:
            current_job = False
            to = datetime.datetime.strptime(
                request.POST.get("to_date"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
            experience.to_date = to
        experience.from_date = datetime.datetime.strptime(
            request.POST.get("from_date"), "%m/%d/%Y"
        ).strftime("%Y-%m-%d")
        experience.current_job = current_job
        experience.salary = request.POST.get("salary")
        experience.job_profile = request.POST.get("job_profile")

        experience.save()
        user = request.user
        user.employment_history.add(experience)
        user.profile_updated = timezone.now()
        user.save()

        request.user.save()

        data = {"error": False, "response": "experience added"}
        return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "response": work_experience.errors}
        return HttpResponse(json.dumps(data))


@login_required
def edit_experience(request, experience_id):
    experiences = EmploymentHistory.objects.filter(id=experience_id)
    if request.method == "GET":
        if experiences:
            experience = experiences[0]
            template = "candidate/edit_experience.html"
            data = {"experience": experience}
        else:
            template = "404.html"
            data = {
                "message": "Sorry, User with this Experience not exists",
                "reason": "The URL may be misspelled or the experience you're looking for is no longer available.",
            }
        return render(request, template, data, status=200 if experiences else 404)
    work_experience = WorkExperienceForm(request.POST, instance=experiences[0])
    if request.user.employment_history.filter(
        company=request.POST.get("company"), designation=request.POST.get("designation")
    ).exclude(id=experience_id):
        data = {
            "error": True,
            "response_message": "Experince with this company and designation already exists",
        }
        return HttpResponse(json.dumps(data))
    else:
        if work_experience.is_valid():
            experience = work_experience.save(commit=False)
            if request.POST.get("current_job") == "on":
                current_job = True
                experience.to_date = request.POST.get("to_date")
            else:
                current_job = False
                to = datetime.datetime.strptime(
                    request.POST.get("to_date"), "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
                experience.to_date = to
            if request.POST.get("from_date"):
                experience.from_date = datetime.datetime.strptime(
                    request.POST.get("from_date"), "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
            experience.current_job = current_job
            experience.salary = request.POST.get("salary")
            if request.POST.get("job_profile"):
                experience.job_profile = request.POST.get("job_profile")

            experience.save()
            user = request.user
            user.profile_updated = timezone.now()
            user.save()

            data = {"error": False, "response": "work history updated successfully"}
        else:
            data = {"error": True, "response": work_experience.errors}
        return HttpResponse(json.dumps(data))


@login_required
def delete_experience(request, experience_id):
    experiences = EmploymentHistory.objects.filter(id=experience_id)
    if experiences:
        experiences[0].delete()
        user = request.user
        user.profile_updated = timezone.now()
        user.save()
        data = {"error": False, "response": "work history deleted successfully"}
    else:
        data = {"error": True, "response": "work history not exist"}
    return HttpResponse(json.dumps(data))
