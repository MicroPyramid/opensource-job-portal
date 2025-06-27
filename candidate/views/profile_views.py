import datetime
import json
from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from zoneinfo import ZoneInfo

from mpcomp.views import jobseeker_login_required
from candidate.forms import (
    PersonalInfoForm,
    ProfileDescriptionForm,
    ProfessinalInfoForm,
    YEARS,
    MONTHS,
    MAR_TYPES,
)
from peeldb.models import (
    User,
    City,
    Country,
    UserEmail,
    Industry,
    Language,
    FunctionalArea,
    Skill,
    UserMessage,
)
from pjob.views import add_other_location_to_user
from psite.forms import UserPassChangeForm


@jobseeker_login_required
def profile(request):
    """need to check user login or not"""
    if request.user.is_authenticated:
        messages = UserMessage.objects.filter(message_to=request.user.id, is_read=False)
        user = request.user
        user.profile_completeness = user.profile_completion_percentage
        user.save()

        nationality = ""
        functional_areas = FunctionalArea.objects.filter(status="Active").order_by(
            "name"
        )
        cities = (
            City.objects.filter(status="Enabled")
            .exclude(slug__icontains="india")
            .order_by("name")
        )
        skills = Skill.objects.filter(status="Active").order_by("name")
        industries = (
            Industry.objects.filter(status="Active").order_by("name").exclude(id=36)
        )
        if request.user.nationality:
            nationality = Country.objects.get(id=request.user.nationality)
        return render(
            request,
            "candidate/view_userinfo.html",
            {
                "nationality": nationality,
                "cities": cities,
                "skills": skills,
                "years": YEARS,
                "months": MONTHS,
                "industries": industries,
                "languages": Language.objects.all(),
                "martial_status": MAR_TYPES,
                "functional_areas": functional_areas,
                "unread_messages": messages.count(),
            },
        )
    return HttpResponseRedirect("/")


@jobseeker_login_required
def edit_personalinfo(request):
    if request.method == "POST":
        validate_personalform = PersonalInfoForm(request.POST, instance=request.user)
        if validate_personalform.is_valid():
            user = validate_personalform.save(commit=False)
            if request.POST.get("dob"):
                dob = datetime.datetime.strptime(
                    request.POST.get("dob"), "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
                user.dob = dob
            user.marital_status = (
                request.POST.get("marital_status")
                if request.POST.get("marital_status")
                else None
            )
            user.first_name = request.POST.get("first_name")
            user.last_name = (
                request.POST.get("last_name") if request.POST.get("last_name") else None
            )
            user.alternate_mobile = (
                request.POST.get("alternate_mobile")
                if request.POST.get("alternate_mobile")
                else None
            )
            user.pincode = (
                request.POST.get("pincode") if request.POST.get("pincode") else None
            )
            user.gender = (
                request.POST.get("gender") if request.POST.get("gender") else None
            )
            user.address = request.POST.get("address")
            user.permanent_address = request.POST.get("permanent_address")
            user.resume_title = (
                request.POST.get("resume_title")
                if request.POST.get("resume_title")
                else None
            )
            user.nationality = 1
            if request.POST.get("current_city"):
                user.current_city = City.objects.get(
                    id=int(request.POST.get("current_city"))
                )
            user.mobile_verified = True
            user.last_mobile_code_verified_on = timezone.now()
            user.profile_updated = timezone.now()
            user.save()
            if request.POST.get("other_loc"):
                add_other_location_to_user(user, request)
            user.preferred_city.clear()
            user.preferred_city.add(*request.POST.getlist("preferred_city"))
            user.industry.clear()
            user.industry.add(*request.POST.getlist("industry"))
            user.functional_area.clear()
            user.functional_area.add(*request.POST.getlist("functional_area"))
            data = {
                "error": False,
                "response": "Presonal Info edited successfully",
                "profile_percantage": request.user.profile_completion_percentage,
                "personal_info": True,
                "first_name": user.first_name,
                "mobile": user.mobile,
                "resume_title": user.resume_title,
                "dob": datetime.datetime.strptime(str(user.dob), "%Y-%m-%d").strftime(
                    "%b %d, %Y"
                ),
                "current_city": user.current_city.name,
            }
        else:
            data = {"error": True, "response": validate_personalform.errors}
        return HttpResponse(json.dumps(data))
    else:
        cities = City.objects.filter(state__country_id=1, status="Enabled").order_by(
            "name"
        )
        countries = Country.objects.all()
        martial_status = MAR_TYPES
        industires = (
            Industry.objects.filter(status="Active").order_by("name").exclude(id=36)
        )
        functional_areas = FunctionalArea.objects.filter(status="Active").order_by(
            "name"
        )
        data = {
            "martial_status": martial_status,
            "cities": cities,
            "countries": countries,
            "industries": industires,
            "functional_areas": functional_areas,
        }
        template = "candidate/edit_personalinfo.html"
        return render(request, template, data)


@login_required
def edit_profile_description(request):
    if request.method == "POST":
        validate_personalform = ProfileDescriptionForm(
            request.POST, instance=request.user
        )
        if validate_personalform.is_valid():
            user = validate_personalform.save()
            user.profile_updated = timezone.now()
            user.save()
            data = {"error": False, "response": "Presonal Info edited successfully"}
        else:
            data = {"error": True, "response": validate_personalform.errors}
        return HttpResponse(json.dumps(data))
    template = "candidate/edit_profile_description.html"
    return render(request, template)


@login_required
def edit_professionalinfo(request):
    if request.method == "POST":
        validate_professionalinfo = ProfessinalInfoForm(
            request.POST, instance=request.user
        )
        if validate_professionalinfo.is_valid():
            user = validate_professionalinfo.save(commit=False)
            industry = Industry.objects.get(id=request.POST.get("prefered_industry"))
            user.prefered_industry = industry
            user.current_salary = request.POST.get("current_salary", "")
            user.expected_salary = request.POST.get("expected_salary")
            user.notice_period = request.POST.get("notice_period")
            user.relocation = str(request.POST.get("relocation")) == "on"
            user.profile_updated = timezone.now()
            user.save()
            data = {
                "error": False,
                "info": "professional info edited successfully",
                "profile_percantage": request.user.profile_completion_percentage,
                "professional_info": True,
                "current_salary": user.current_salary,
                "expected_salary": user.expected_salary,
                "job_role": user.job_role,
                "year": user.year,
                "month": user.month,
                "notice_period": user.notice_period,
                "prefered_industry": industry.name,
            }
        else:
            data = {"error": True, "response": validate_professionalinfo.errors}
        return HttpResponse(json.dumps(data))
    else:
        data = {
            "industires": Industry.objects.filter(status="Active").exclude(id=36),
            "years": YEARS,
            "months": MONTHS,
        }
        template = "candidate/edit_professionalInfo.html"
        return render(request, template, data)


@login_required
def edit_email(request):
    if request.method == "POST":
        user = UserEmail.objects.filter(user=request.user, is_primary=True)
        if user:
            user = user[0]
            user.is_primary = False
            requested_email = UserEmail.objects.get(id=request.POST.get("email"))
            requested_email.is_primary = True
            requested_email.save()
            user.save()
            user = request.user
            user.profile_updated = timezone.now()
            user.save()
            data = {"error": False, "message": "changed successfully"}
        else:
            data = {"error": True, "errinfo": "no email to change"}
        return HttpResponse(json.dumps(data))

    else:
        template = "candidate/edit_email.html"
        return render(request, template)


@login_required
def edit_emailnotifications(request):
    if request.method == "POST":
        user = request.user
        user.email_notifications = False if user.email_notifications else True
        user.save()
        data = {
            "status": user.email_notifications,
            "response": "Updated Successfully",
            "error": False,
        }
    else:
        data = {"error": True}
    return HttpResponse(json.dumps(data))


@login_required
def user_password_change(request):
    if request.method == "POST":
        validate_changepassword = UserPassChangeForm(request.POST)
        if validate_changepassword.is_valid():
            user = request.user
            if request.POST["new_password"] != request.POST["retype_password"]:
                return HttpResponse(
                    json.dumps(
                        {
                            "error": True,
                            "response_message": "Password and ConfirmPasswords did not match",
                        }
                    )
                )
            user.set_password(request.POST["new_password"])
            user.save()
            return HttpResponse(
                json.dumps({"error": False, "message": "Password changed successfully"})
            )
        else:
            return HttpResponse(
                json.dumps({"error": True, "response": validate_changepassword.errors})
            )
    template = "candidate/change_user_password.html"
    return render(request, template)
