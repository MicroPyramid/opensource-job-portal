import datetime
import json
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from zoneinfo import ZoneInfo

from candidate.forms import (
    EducationForm,
    DegreeForm,
    EducationInstitueForm,
    DEGREE_TYPES,
)
from peeldb.models import (
    City,
    EducationDetails,
    Degree,
    EducationInstitue,
    Qualification,
)


@login_required
def add_education(request):
    if request.method == "GET":
        template = "candidate/add_education.html"
        return render(
            request,
            template,
            {
                "degree_types": DEGREE_TYPES,
                "qualifications": Qualification.objects.filter(
                    status="Active"
                ).order_by("name"),
                "cities": City.objects.filter(status="Enabled").order_by("name"),
            },
        )
    education_valid = EducationForm(request.POST)
    degree_valid = DegreeForm(request.POST)
    education_institute_valid = EducationInstitueForm(request.POST)
    if (
        education_valid.is_valid()
        and degree_valid.is_valid()
        and education_institute_valid.is_valid()
    ):
        if request.user.education.filter(
            degree__degree_name=request.POST.get("degree_name")
        ):
            return HttpResponse(
                json.dumps(
                    {"error": True, "response_message": "education already exists"}
                )
            )
        city = City.objects.get(id=request.POST.get("city"))
        institute = EducationInstitue.objects.create(
            name=request.POST.get("name"), city=city
        )
        if request.POST.get("address"):
            institute.address = request.POST.get("address")
            institute.save()
        degree_name = Qualification.objects.get(id=request.POST.get("degree_name"))
        degree = Degree.objects.create(
            degree_name=degree_name,
            degree_type=request.POST.get("degree_type"),
            specialization=request.POST.get("specialization"),
        )
        to = (
            None
            if (request.POST.get("current_education") == "on")
            else datetime.datetime.strptime(
                request.POST.get("to_date"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
        )
        from_date = datetime.datetime.strptime(
            request.POST.get("from_date"), "%m/%d/%Y"
        ).strftime("%Y-%m-%d")
        education = EducationDetails.objects.create(
            institute=institute,
            degree=degree,
            score=request.POST.get("score"),
            from_date=from_date,
            to_date=to,
            current_education=request.POST.get("current_education") == "on",
        )
        request.user.profile_updated = timezone.now()
        request.user.save()
        request.user.education.add(education)
        return HttpResponse(
            json.dumps({"error": False, "response": "education details added"})
        )
    else:
        errors = {}
        for k in education_valid.errors:
            errors[k] = education_valid.errors[k][0]
        for k in degree_valid.errors:
            errors[k] = degree_valid.errors[k][0]
        for k in education_institute_valid.errors:
            errors[k] = education_institute_valid.errors[k][0]
        return HttpResponse(json.dumps({"error": True, "response": errors}))


@login_required
def edit_education(request, education_id):
    education = EducationDetails.objects.filter(id=education_id).first()
    if education:
        if request.method == "GET":
            template = "candidate/edit_education.html"
            return render(
                request,
                template,
                {
                    "degree_types": DEGREE_TYPES,
                    "qualifications": Qualification.objects.filter(
                        status="Active"
                    ).order_by("name"),
                    "education": education,
                    "cities": City.objects.filter(status="Enabled").order_by("name"),
                },
            )
        student_degree = Degree.objects.get(id=education.degree.id)
        degree_valid = DegreeForm(request.POST, student_degree)
        institute = EducationInstitue.objects.get(id=education.institute.id)
        education_institute_valid = EducationInstitueForm(request.POST, institute)
        education_valid = EducationForm(request.POST, education, student_degree)
        if (
            education_valid.is_valid()
            and degree_valid.is_valid()
            and education_institute_valid.is_valid()
        ):
            degree_name = Qualification.objects.get(id=request.POST.get("degree_name"))

            if request.user.education.filter(
                degree__degree_name=request.POST.get("degree_name")
            ).exclude(id=education_id):
                return HttpResponse(
                    json.dumps(
                        {"error": True, "response_message": "Education already exists"}
                    )
                )

            student_degree.degree_name = degree_name
            student_degree.degree_type = request.POST.get("degree_type")
            student_degree.specialization = request.POST.get("specialization")
            student_degree.save()

            institute.name = request.POST.get("name")
            if request.POST.get("address"):
                institute.address = request.POST.get("address")
            city = City.objects.get(id=request.POST.get("city"))
            institute.city = city
            institute.save()

            education.degree = student_degree
            education.institute = institute
            education.from_date = datetime.datetime.strptime(
                request.POST.get("from_date"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
            education.to_date = (
                None
                if (request.POST.get("current_education") == "on")
                else datetime.datetime.strptime(
                    request.POST.get("to_date"), "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
            )
            education.score = request.POST.get("score")
            education.current_education = request.POST.get("current_education") == "on"
            education.save()
            user = request.user
            user.profile_updated = timezone.now()
            user.save()

            return HttpResponse(
                json.dumps(
                    {"error": False, "response": "education updated successfully"}
                )
            )
        else:
            errors = {}
            for k in education_valid.errors:
                errors[k] = education_valid.errors[k][0]
            for k in degree_valid.errors:
                errors[k] = degree_valid.errors[k][0]
            for k in education_institute_valid.errors:
                errors[k] = education_institute_valid.errors[k][0]
            return HttpResponse(json.dumps({"error": True, "response": errors}))
    else:
        template = "404.html"
        reason = "The URL may be misspelled or the education you're looking for is no longer available."
        return render(
            request,
            template,
            {"message": "Sorry, User with this Education not exists", "reason": reason},
            status=404,
        )


@login_required
def delete_education(request, education_id):
    educations = EducationDetails.objects.filter(id=education_id)
    if educations:
        educations[0].delete()
        user = request.user
        user.profile_updated = timezone.now()
        user.save()
        data = {"error": False, "response": "education deleted successfully"}
    else:
        data = {"error": True, "repsonse": "education not exist"}
    return HttpResponse(json.dumps(data))
