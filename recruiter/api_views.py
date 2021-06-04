import json
import math
from django.utils import timezone
from datetime import datetime
from django.http.response import JsonResponse
from django.db.models import Q, Count
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.template import loader, Template, Context

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from peeldb.models import (
    User,
    JobPost,
    Company,
    JOB_TYPE,
    Country,
    City,
    AGENCY_INVOICE_TYPE,
    AGENCY_JOB_TYPE,
    AgencyResume,
    AgencyRecruiterJobposts,
    AppliedJobs,
    MARTIAL_STATUS,
)
from recruiter.permissions import RecruiterRequiredPermission
from recruiter import status
from mpcomp.views import (
    rand_string,
    Memail,
    get_prev_after_pages_count,
    get_next_month,
    get_aws_file_path,
)
from mpcomp.views import get_absolute_url
from recruiter.forms import JobPostForm, YEARS, MONTHS
from recruiter.serializers import *


def get_token(user):
    token, _ = Token.objects.get_or_create(user=user)
    return token


@api_view(["POST"])
def login_view(request):
    form_data = request.query_params if len(request.data) == 0 else request.data

    form = LoginSerializer(data=form_data)
    if form.is_valid():
        email = form_data.get("email")
        user = User.objects.filter(email=email).first()
        token = get_token(user)
        created_on = timezone.now()
        token.created = created_on
        token.save()
        data = {
            "token": token.key,
            "id": user.id,
            "employee_name": user.username,
        }
        return JsonResponse(data, status=status.HTTP_200_OK)
    else:
        data = {"error": True, "errors": form.errors}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
@permission_classes((RecruiterRequiredPermission,))
def jobs_list(request):
    if request.user.agency_admin:
        active_jobs_list = (
            JobPost.objects.filter(user__company=request.user.company)
            .exclude(status__in=["Disabled", "Expired"])
            .prefetch_related("location", "agency_recruiters")
            .annotate(responses=Count("appliedjobs"))
            .order_by("-id")
        )
    elif request.user.is_agency_recruiter:
        active_jobs_list = (
            JobPost.objects.filter(
                Q(agency_recruiters__in=[request.user]) | Q(user=request.user)
            )
            .exclude(status__in=["Disabled", "Expired"])
            .prefetch_related("location", "agency_recruiters")
            .annotate(responses=Count("appliedjobs"))
            .order_by("-id")
            .distinct()
        )
    else:
        active_jobs_list = (
            JobPost.objects.filter(user=request.user)
            .exclude(status__in=["Disabled", "Expired"])
            .prefetch_related("location", "agency_recruiters")
            .annotate(responses=Count("appliedjobs"))
            .order_by("-id")
        )
    items_per_page = 10
    if request.POST.get("search_value"):
        if request.POST.get("search_value") == "all":
            pass
        else:
            active_jobs_list = active_jobs_list.filter(
                job_type__iexact=request.POST.get("search_value")
            )

    if "page" in request.POST and int(request.POST.get("page")) > 0:
        page = int(request.POST.get("page"))
    else:
        page = 1

    no_pages = int(math.ceil(float(active_jobs_list.count()) / items_per_page))
    active_jobs_list = active_jobs_list[
        (page - 1) * items_per_page : page * items_per_page
    ]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    response_data = {
        "jobs_list": JobPostSerializer(active_jobs_list, many=True).data,
        "aft_page": aft_page,
        "after_page": after_page,
        "prev_page": prev_page,
        "previous_page": previous_page,
        "current_page": page,
        "last_page": no_pages,
        "search_value": request.POST["search_value"]
        if "search_value" in request.POST
        else "All",
    }
    return JsonResponse(response_data, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes((RecruiterRequiredPermission,))
def inactive_jobs(request):
    inactive_jobs_list = JobPost.objects.filter(
        Q(user=request.user.id) & Q(status__in=["Disabled", "Expired"])
    ).order_by("-id")
    inactive_jobs_list = inactive_jobs_list.filter(user=request.user)

    items_per_page = 10
    if request.POST.get("search_value"):
        if request.POST.get("search_value") == "all":
            pass
        else:
            inactive_jobs_list = inactive_jobs_list.filter(
                job_type__iexact=request.POST.get("search_value")
            )

    if "page" in request.POST and int(request.POST.get("page")) > 0:
        page = int(request.POST.get("page"))
    else:
        page = 1

    no_pages = int(math.ceil(float(inactive_jobs_list.count()) / items_per_page))
    inactive_jobs_list = inactive_jobs_list[
        (page - 1) * items_per_page : page * items_per_page
    ]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    return JsonResponse(
        {
            "jobs_list": JobPostSerializer(inactive_jobs_list, many=True).data,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "search_value": request.POST["search_value"]
            if "search_value" in request.POST.keys()
            else "All",
        },
    )


def add_other_skills(job_post, data, user):
    temp = loader.get_template("recruiter/email/add_other_fields.html")
    subject = "PeelJobs New JobPost"
    mto = [settings.DEFAULT_FROM_EMAIL]
    mfrom = settings.DEFAULT_FROM_EMAIL
    for skill in data:
        for value in skill.values():
            other_skills = value.replace(" ", "").split(",")
            for value in other_skills:
                if value != "":
                    skills = Skill.objects.filter(name__iexact=value)
                    if skills:
                        job_post.skills.add(skills[0])
                    else:
                        skill = Skill.objects.create(
                            name=value,
                            status="InActive",
                            slug=slugify(value),
                            skill_type="Technical",
                        )
                        c = {
                            "job_post": job_post,
                            "user": user,
                            "item": value,
                            "type": "Skill",
                            "value": skill.name,
                        }
                        rendered = temp.render(c)
                        Memail(mto, mfrom, subject, rendered, True)
                        job_post.skills.add(skill)


def add_other_qualifications(job_post, data, user):
    temp = loader.get_template("recruiter/email/add_other_fields.html")
    subject = "PeelJobs New JobPost"
    mto = [settings.DEFAULT_FROM_EMAIL]
    mfrom = settings.DEFAULT_FROM_EMAIL
    for qualification in data:
        for value in qualification.values():
            other_skills = value.replace(" ", "").split(",")
            for value in other_skills:
                if value != "":
                    qualification = Qualification.objects.filter(name__iexact=value)
                    if qualification:
                        job_post.edu_qualification.add(qualification[0])
                    else:
                        qualification = Qualification.objects.create(
                            name=value, status="InActive", slug=slugify(value)
                        )
                        job_post.edu_qualification.add(qualification)
                        c = {
                            "job_post": job_post,
                            "user": user,
                            "item": value,
                            "type": "Qualification",
                            "value": qualification.name,
                        }
                        rendered = temp.render(c)
                        Memail(mto, mfrom, subject, rendered, True)


def add_other_industry(job_post, data, user):
    temp = loader.get_template("recruiter/email/add_other_fields.html")
    subject = "PeelJobs New JobPost"
    mto = [settings.DEFAULT_FROM_EMAIL]
    mfrom = settings.DEFAULT_FROM_EMAIL

    for industry in data:
        for value in industry.values():
            o_industries = value.replace(" ", "").split(",")
            for value in o_industries:
                if value != "":
                    industry = Industry.objects.filter(name__iexact=value)
                    if industry:
                        job_post.industry.add(industry[0])
                    else:
                        industry = Industry.objects.create(
                            name=value, status="InActive", slug=slugify(value)
                        )
                        job_post.industry.add(industry)
                        c = {
                            "job_post": job_post,
                            "user": user,
                            "item": value,
                            "type": "Industry",
                            "value": industry.name,
                        }
                        rendered = temp.render(c)
                        Memail(mto, mfrom, subject, rendered, True)


def add_other_functional_area(job_post, data, user):
    temp = loader.get_template("recruiter/email/add_other_fields.html")
    subject = "PeelJobs New JobPost"
    mto = [settings.DEFAULT_FROM_EMAIL]
    mfrom = settings.DEFAULT_FROM_EMAIL

    for functional_area in data:
        for value in functional_area.values():
            other_areas = value.replace(" ", "").split(",")
            for value in other_areas:
                if value != "":
                    functional_area = FunctionalArea.objects.filter(name__iexact=value)
                    if functional_area:
                        job_post.functional_area.add(functional_area[0])
                    else:
                        functional_area = FunctionalArea.objects.create(
                            name=value, status="InActive"
                        )
                        job_post.functional_area.add(functional_area)
                        c = {
                            "job_post": job_post,
                            "user": user,
                            "item": value,
                            "type": "Functional Area",
                            "value": functional_area.name,
                        }
                        rendered = temp.render(c)
                        Memail(mto, mfrom, subject, rendered, True)


def add_other_locations(post, data, user):
    temp = loader.get_template("recruiter/email/add_other_fields.html")
    subject = "PeelJobs New JobPost"
    mto = [settings.DEFAULT_FROM_EMAIL]
    mfrom = settings.DEFAULT_FROM_EMAIL
    for location in data.getlist("other_location"):
        locations = [loc.strip() for loc in location.split(",") if loc.strip()]
        for location in locations:
            locations = City.objects.filter(name__iexact=location)
            if locations:
                post.location.add(locations[0])
            else:
                location = City.objects.create(
                    name=location,
                    status="Disabled",
                    slug=slugify(location),
                    state=State.objects.get(id=16),
                )
                post.location.add(location)
                c = {
                    "job_post": post,
                    "user": user,
                    "item": "Location",
                    "type": "Location",
                    "value": location.name,
                }
                rendered = temp.render(c)
                Memail(mto, mfrom, subject, rendered, True)


def add_interview_location(data, job_post, no_of_locations):
    for i in range(1, no_of_locations):
        current_interview_city = "final_location_" + str(i)
        current_venue_details = "venue_details_" + str(i)
        # current_show_location = 'show_location_' + str(i)
        # show_location = False
        interview_venue_details = ""
        latitude = ""
        longitude = ""
        for key in data.keys():
            if str(current_interview_city) == str(key):
                interview_city = list(json.loads(data[key]))
                latitude = interview_city[0]
                longitude = interview_city[1]

            if str(current_venue_details) == str(key):
                interview_venue_details = data[key]

            # if str(current_show_location) == str(key):
            #     show_location = True

        if interview_venue_details or latitude or longitude:
            # interview_location = InterviewLocation.objects.create(
            # venue_details=interview_venue_details, latitude=latitude,
            # longitude=longitude)
            interview_location = InterviewLocation.objects.create(
                venue_details=interview_venue_details
            )
            # interview_location.show_location = show_location
            interview_location.save()
            job_post.job_interview_location.add(interview_location)


def adding_keywords(keywords, post):
    for kw in keywords:
        key = Keyword.objects.filter(name__iexact=kw)
        if not kw == "":
            if not key:
                keyword = Keyword.objects.create(name=kw)
                post.keywords.add(keyword)
            else:
                post.keywords.add(key[0])


def set_other_fields(post, data, user):
    if data.get("last_date"):
        last_date = datetime.strptime(data.get("last_date"), "%m/%d/%Y").strftime(
            "%Y-%m-%d"
        )
        post.last_date = last_date
    else:
        post.last_date = get_next_month()

    post.fresher = data.get("min_year") == 0
    if data.get("visa_required"):
        post.visa_required = True
        visa_country = Country.objects.get(id=data.get("visa_country"))
        post.visa_country = visa_country
        post.visa_type = data.get("visa_type")
    else:
        post.visa_required = False
        post.visa_type = ""
        post.visa_country = None

    if data.get("published_date"):
        start_date = datetime.strptime(
            data.get("published_date"), "%m/%d/%Y %H:%M:%S"
        ).strftime("%Y-%m-%d %H:%M:%S")
        date_format = "%Y-%m-%d %H:%M:%S"
        post.published_date = datetime.strptime(start_date, date_format)
    if data.get("status") == "Pending":

        if data.get("fb_post") == "on":
            post.post_on_fb = True
            post.fb_groups = data.getlist("fb_groups")
        post.post_on_tw = data.get("tw_post") == "on"
        post.post_on_ln = data.get("ln_post") == "on"
    if data.get("job_type") == "walk-in":
        post.vacancies = 0
        post.walkin_contactinfo = data.get("walkin_contactinfo")
        walkin_from_date = datetime.strptime(
            data.get("walkin_from_date"), "%m/%d/%Y"
        ).strftime("%Y-%m-%d")
        post.walkin_show_contact_info = data.get("walkin_show_contact_info") == "on"
        post.walkin_from_date = walkin_from_date
        walkin_to_date = datetime.strptime(
            data.get("walkin_to_date"), "%m/%d/%Y"
        ).strftime("%Y-%m-%d")

        post.walkin_to_date = walkin_to_date
        if data.get("walkin_time"):
            post.walkin_time = data.get("walkin_time")

        post.last_date = walkin_to_date
    post.save()

    if user.agency_admin or user.has_perm("jobposts_edit"):
        post.agency_job_type = data.get("agency_job_type")
        post.agency_invoice_type = data.get("agency_invoice_type")
        if data.get("agency_client"):
            client = AgencyCompany.objects.get(id=data.get("agency_client"))
            post.agency_client = client
        # if data.get('agency_category'):
        #     agency_category = AgencyCompanyCatogery.objects.get(
        #         id=data.get('agency_category'))
        #     post.agency_category = agency_category
        post.save()

        agency_resumes = AgencyResume.objects.filter(uploaded_by__company=user.company)
        agency_resumes = agency_resumes.filter(skill__in=post.skills.all())

        for each_resume in agency_resumes:
            AgencyApplicants.objects.create(applicant=each_resume, job_post=post)
        # post.agency_recruiters.clear()
        # post.agency_recruiters.add(*data.getlist('agency_recruiters'))
        for each_recruiter in data.getlist("agency_recruiters"):
            user = get_object_or_404(User, id=each_recruiter)
            AgencyRecruiterJobposts.objects.create(job_post=post, user=user)


def adding_other_fields_data(data, post, user):
    if "final_skills" in data.keys():
        add_other_skills(post, json.loads(data["final_skills"]), user)
    if "final_edu_qualification" in data.keys():
        add_other_qualifications(
            post, json.loads(data["final_edu_qualification"]), user
        )
    if "final_industry" in data.keys():
        add_other_industry(post, json.loads(data["final_industry"]), user)
    if "final_functional_area" in data.keys():
        add_other_functional_area(post, json.loads(data["final_functional_area"]), user)
    if "other_location" in data.keys():
        add_other_locations(post, data, user)

    no_of_locations = int(json.loads(data["no_of_interview_location"])) + 1
    add_interview_location(data, post, no_of_locations)

    adding_keywords(data.getlist("keywords"), post)
    post.send_email_notifications = data.get("send_email_notifications") == "True"

    post.status = data.get("status")
    post.published_message = data.get("published_message")
    post.job_type = data.get("job_type")
    post.save()
    set_other_fields(post, data, user)


def save_job_post(validate_post, request):
    validate_post.agency_amount = validate_post.agency_amount or ""
    validate_post.user = request.user
    validate_post.published_on = datetime.now()
    validate_post.vacancies = request.POST.get("vacancies") or 0
    validate_post.pincode = request.POST.get("pincode", "")
    if request.POST.get("major_skill"):
        skill = Skill.objects.filter(id=request.POST.get("major_skill"))
        if skill:
            validate_post.major_skill = skill[0]
    company = Company.objects.filter(name__iexact=request.POST["company_name"])
    if company:
        job_post_company = company[0]
        job_post_company.name = request.POST["company_name"]
        job_post_company.slug = slugify(request.POST["company_name"])
        job_post_company.address = request.POST["company_address"]
        job_post_company.profile = request.POST["company_description"]
        job_post_company.website = request.POST["company_website"]
        if "company_logo" in request.FILES:
            file_path = get_aws_file_path(
                request.FILES.get("company_logo"),
                "company/logo/",
                slugify(request.POST["company_name"]),
            )
            job_post_company.profile_pic = file_path
        job_post_company.save()
    else:
        job_post_company = Company.objects.create(
            name=request.POST["company_name"],
            address=request.POST["company_address"],
            profile=request.POST["company_description"],
            slug=slugify(request.POST["company_name"]),
            company_type="Company",
            email=request.user.email,
            created_from="job_post",
            website=request.POST["company_website"],
        )
        if request.FILES.get("company_logo"):
            file_path = get_aws_file_path(
                request.FILES.get("company_logo"),
                "company/logo/",
                slugify(request.POST["company_name"]),
            )
            job_post_company.profile_pic = file_path
        job_post_company.save()
    validate_post.company = job_post_company
    validate_post.slug = get_absolute_url(validate_post)
    validate_post.save()

    if request.user.is_admin and request.user.is_agency_recruiter:
        for recruiter in request.POST.getlist("agency_recruiters"):
            user = User.objects.get(id=recruiter)
            c = {"job_post": validate_post, "user": user}
            t = loader.get_template("email/assign_jobpost.html")
            subject = "PeelJobs New JobPost"
            rendered = t.render(c)
            mfrom = settings.DEFAULT_FROM_EMAIL
            user_active = True if user.is_active else False
            Memail([user.email], mfrom, subject, rendered, user_active)


def checking_error_value(errors, key_item):
    for each in json.loads(key_item):
        for key, value in each.items():
            if not value:
                errors[key] = "This field is required."
    return errors


def retreving_form_errors(request, post):
    errors = post.errors
    if "final_industry" in request.POST.keys():
        errors = checking_error_value(errors, request.POST["final_industry"])

    if "final_functional_area" in request.POST.keys():
        errors = checking_error_value(errors, request.POST["final_functional_area"])

    if "final_edu_qualification" in request.POST.keys():
        errors = checking_error_value(errors, request.POST["final_edu_qualification"])

    if "final_skills" in request.POST.keys():
        errors = checking_error_value(errors, request.POST["final_skills"])

    return errors


@api_view(["GET", "POST"])
@permission_classes((RecruiterRequiredPermission,))
def new_job(request, job_type):
    if request.method == "GET":
        if request.GET.get("q"):
            companies = Company.objects.filter(
                name__icontains=request.GET.get("q"), is_active=True
            ).distinct()[:10]
            companies_names = companies.values_list("name", flat=True)
            if request.GET.get("register_name"):
                company = Company.objects.filter(
                    name=request.GET.get("register_name")
                ).first()
                if company:
                    return JsonResponse({"company": CompanySerializer(company).data})
            data = {"response": companies_names}
            return JsonResponse(data)

        if request.user.is_active:
            if (
                request.user.is_company_recruiter
                and not request.user.is_admin
                and not request.user.has_perm("jobposts_edit")
            ):
                message = "You Don't have permission to create a new job"
                reason = "Please contact your agency admin"
                return JsonResponse(
                    {"message": message, "reason": reason},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            countries = Country.objects.all().order_by("name")
            skills = Skill.objects.all().exclude(status="InActive").order_by("name")
            functional_area = (
                FunctionalArea.objects.all().exclude(status="InActive").order_by("name")
            )
            industries = (
                Industry.objects.all().exclude(status="InActive").order_by("name")
            )
            qualifications = (
                Qualification.objects.all().exclude(status="InActive").order_by("name")
            )
            cities = City.objects.filter().exclude(status="Disabled")
            recruiters = User.objects.filter(company=request.user.company)
            if request.user.agency_admin or request.user.has_perm("jobposts_edit"):
                jobposts = JobPost.objects.filter(
                    job_type=job_type, user__company=request.user.company
                )
            else:
                jobposts = JobPost.objects.filter(job_type=job_type, user=request.user)

            clients = AgencyCompany.objects.filter(company=request.user.company)
            show_clients = True
            show_recruiters = True
            if request.user.is_agency_recruiter:
                show_clients = False if not clients else True
                show_recruiters = False if not recruiters else True
            return JsonResponse(
                {
                    "job_types": JOB_TYPE,
                    "functional_area": FunctionalAreaSerializer(
                        functional_area, many=True
                    ).data,
                    "qualifications": QualificationSerializer(
                        qualifications, many=True
                    ).data,
                    "years": YEARS,
                    "months": MONTHS,
                    "industries": IndustrySerializer(industries, many=True).data,
                    "countries": CountrySerializer(countries, many=True).data,
                    "skills": SkillSerializer(skills, many=True).data,
                    "jobposts": JobPostSerializer(jobposts, many=True).data,
                    "cities": CitySerializer(cities, many=True).data,
                    "status": job_type,
                    "agency_invoice_types": AGENCY_INVOICE_TYPE,
                    "agency_job_types": AGENCY_JOB_TYPE,
                    "recruiters": UserSerializer(recruiters, many=True).data,
                    "clients": AgencyCompanySerializer(clients, many=True).data,
                    "show_clients": show_clients,
                    "show_recruiters": show_recruiters,
                    "user_details": UserSerializer(request.user).data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            message = "Sorry, Your account is not verified"
            reason = "Please verify your email id"
            return JsonResponse(
                {"message": message, "reason": reason},
                status=status.HTTP_404_NOT_FOUND,
            )
    validate_form = JobPostForm(request.POST, request.FILES, user=request.user)
    errors = retreving_form_errors(request, validate_form)
    if not errors:
        validate_post = validate_form.save(commit=False)
        save_job_post(validate_post, request)
        validate_form.save_m2m()
        adding_other_fields_data(request.POST, validate_post, request.user)
        c = {"job_post": validate_post, "user": request.user}
        t = loader.get_template("email/jobpost_notification.html")
        subject = "PeelJobs New JobPost"
        rendered = t.render(c)
        mto = ["anusha@micropyramid.com"]
        mfrom = settings.DEFAULT_FROM_EMAIL
        Memail(mto, mfrom, subject, rendered, True)
        data = {
            "error": False,
            "response": "New Post created",
            "post": validate_post.id,
        }
        return JsonResponse(data, status=status.HTTP_200_OK)
    data = {"error": True, "response": errors}
    return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((RecruiterRequiredPermission,))
def getout(request):
    request.user.auth_token.delete()
    return JsonResponse({"error": False}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((RecruiterRequiredPermission,))
def edit_job(request, job_post_id):
    if request.user.agency_admin or request.user.has_perm("jobposts_edit"):
        job_post = JobPost.objects.filter(
            id=job_post_id, user__company=request.user.company
        ).first()
    else:
        job_post = JobPost.objects.filter(id=job_post_id, user=request.user).first()

    if request.method == "GET":
        if request.user.mobile_verified:
            if job_post:
                countries = Country.objects.all().order_by("name")
                skills = list(Skill.objects.filter(status="Active"))
                skills.extend(job_post.skills.filter(status="InActive"))

                industries = list(
                    Industry.objects.filter(status="Active").order_by("name")
                )
                industries.extend(job_post.industry.filter(status="InActive"))

                cities = list(City.objects.filter(status="Enabled").order_by("name"))
                cities.extend(job_post.location.filter(status="Disabled"))

                qualifications = list(
                    Qualification.objects.filter(status="Active").order_by("name")
                )
                qualifications.extend(
                    job_post.edu_qualification.filter(status="InActive")
                )

                recruiters = User.objects.filter(company=request.user.company)
                clients = AgencyCompany.objects.filter(company=request.user.company)

                functional_area = list(
                    FunctionalArea.objects.filter(status="Active").order_by("name")
                )
                functional_area.extend(
                    job_post.functional_area.filter(status="InActive")
                )
                return JsonResponse(
                    {
                        "job_types": JOB_TYPE,
                        "functional_area": FunctionalAreaSerializer(
                            functional_area, many=True
                        ).data,
                        "qualifications": QualificationSerializer(
                            qualifications, many=True
                        ).data,
                        "years": YEARS,
                        "months": MONTHS,
                        "industries": IndustrySerializer(industries, many=True).data,
                        "countries": CountrySerializer(countries, many=True).data,
                        "skills": SkillSerializer(skills, many=True).data,
                        "jobpost": JobPostSerializer(job_post).data,
                        "cities": CitySerializer(cities, many=True).data,
                        "agency_invoice_types": AGENCY_INVOICE_TYPE,
                        "agency_job_types": AGENCY_JOB_TYPE,
                        "recruiters": UserSerializer(recruiters, many=True).data,
                        "clients": AgencyCompanySerializer(clients, many=True).data,
                    },
                )
            else:
                message = "Sorry, No Job Posts Found"
                reason = "The URL may be misspelled or the job you're looking for is no longer available."
        else:
            message = "Sorry, Your mobile number is not verified"
            reason = "Please verify your mobile number"
        return JsonResponse(
            {"error": True, "message": message}, status=status.HTTP_404_NOT_FOUND
        )

    validate_form = JobPostForm(
        request.POST, request.FILES, instance=job_post, user=request.user
    )
    errors = retreving_form_errors(request, validate_form)
    if not errors:
        validate_post = validate_form.save(commit=False)
        save_job_post(validate_post, request)
        validate_form.save_m2m()
        validate_post.job_interview_location.clear()
        adding_other_fields_data(request.POST, validate_post, request.user)
        data = {
            "error": False,
            "response": "Jobpost Updated Successfully",
            "post": validate_post.id,
        }
        return JsonResponse(data)
    data = {"error": True, "response": errors}
    return JsonResponse(data)


@api_view(["GET"])
@permission_classes((RecruiterRequiredPermission,))
def delete_job(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id, user=request.user)
    job_post.status = "Disabled"
    job_post.closed_date = datetime.now(timezone.utc)
    job_post.save()
    data = {"error": False, "response": "Job Post deleted Successfully"}
    return JsonResponse(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((RecruiterRequiredPermission,))
def change_password(request):
    validate_changepassword = ChangePasswordSerializer(
        data=request.data, user=request.user
    )
    if validate_changepassword.is_valid():
        user = request.user
        user.set_password(request.POST["newpassword"])
        user.save()
        request.user.auth_token.delete()
        token = get_token(user)
        return JsonResponse(
            {
                "error": False,
                "message": "Password changed successfully",
                "token": token.key,
            },
            status=status.HTTP_200_OK,
        )
    return JsonResponse(
        {"error": True, "response": validate_changepassword.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET", "POST"])
@permission_classes((RecruiterRequiredPermission,))
def edit_profile(request):
    if request.method == "GET":
        functional_areas = FunctionalArea.objects.all()
        user = (
            User.objects.filter(id=request.user.id)
            .prefetch_related("technical_skills", "industry", "functional_area")
            .first()
        )
        return JsonResponse(
            {
                "skills": SkillSerializer(Skill.objects.all(), many=True).data,
                "industries": IndustrySerializer(
                    Industry.objects.all(), many=True
                ).data,
                "functional_areas": FunctionalAreaSerializer(
                    functional_areas, many=True
                ).data,
                "martial_status": MARTIAL_STATUS,
                "countries": CountrySerializer(Country.objects.all(), many=True).data,
                "cities": CitySerializer(
                    City.objects.all().select_related("state", "state__country"),
                    many=True,
                ).data,
                "states": StateSerializer(
                    State.objects.all().select_related("country"), many=True
                ).data,
                "user": UserSerializer(user).data,
            },
        )
    validate_user = UserUpdateSerializer(data=request.data, instance=request.user)
    user_mobile = request.user.mobile
    if validate_user.is_valid():
        city = City.objects.get(id=request.data.get("city"))
        state = State.objects.get(id=request.data.get("state"))
        user = validate_user.save(city=city, state=state)
        if request.FILES.get("profile_pic"):
            user.profile_pic = request.FILES.get("profile_pic")
        if request.POST.get("gender"):
            user.gender = request.data.get("gender")
        if request.POST.get("dob"):
            dob = datetime.strptime(request.data.get("dob"), "%m/%d/%Y").strftime(
                "%Y-%m-%d"
            )
            user.dob = dob
        else:
            user.dob = None
        user.show_email = request.data.get("show_email") == "on"
        user.email_notifications = request.data.get("email_notifications") == "on"

        user_login = False
        password_reset_diff = int(
            (datetime.now() - user.last_mobile_code_verified_on).seconds
        )
        # if not user.mobile_verified:
        #     if password_reset_diff > 600:
        #         random_code = rand_string(size=6)
        #         message = (
        #             "Hello "
        #             + request.user.username
        #             + ", An OTP "
        #             + random_code
        #             + " for your Peeljobs recruiter account, Please Confirm and Proceed"
        #         )
        #         data = {
        #             "username": settings.BULK_SMS_USERNAME,
        #             "password": settings.BULK_SMS_PASSWORD,
        #             "from": settings.BULK_SMS_FROM,
        #             "to": request.POST.get("mobile"),
        #             "message": message,
        #         }
        #         # requests.get("http://182.18.160.225/index.php/api/bulk-sms", params=data)
        #         requests.get(
        #             "http://sms.9sm.in/rest/services/sendSMS/sendGroupSms?AUTH_KEY="
        #             + str(settings.SMS_AUTH_KEY)
        #             + "&message="
        #             + str(message)
        #             + "&senderId="
        #             + str(settings.BULK_SMS_FROM)
        #             + "&routeId=1&mobileNos="
        #             + str(request.POST.get("mobile"))
        #             + "&smsContentType=english"
        #         )

        #         user.mobile_verification_code = random_code
        #         user.mobile_verified = False
        #         user_login = True
        #         user.mobile = request.data.get["mobile"]
        #         user.last_mobile_code_verified_on = datetime.now(timezone.utc)
        #         message = "Your Details Updated Successfully"
        #     else:
        #         user.mobile = user_mobile
        #         message = "An otp has been sent to you in the past 1 week, Please Verify Your Mobile Number"
        # else:
        #     if user.mobile == user_mobile:
        #         user.mobile = user_mobile
        #         message = "Your Details Updated Successfully"
        #     else:
        #         message = "Mobile num can't be change within a week"
        user.marital_status = request.data.get("marital_status", "")
        user.first_name = request.data.get("first_name")
        user.last_name = request.data.get("last_name", "")
        user.address = request.data.get("address")
        user.permanent_address = request.data.get("permanent_address", "")
        user.technical_skills.clear()
        user.industry.clear()
        user.functional_area.clear()
        user.technical_skills.add(*request.data.getlist("technical_skills"))
        user.industry.add(*request.data.getlist("industry"))
        user.functional_area.add(*request.data.getlist("functional_area"))
        user.profile_completeness = user.profile_completion_percentage
        user.save()
        data = {"error": False, "response": message, "is_login": user_login}
        return JsonResponse(data, status=status.HTTP_200_OK)
    else:
        data = {"error": True, "response": validate_user.errors}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
@permission_classes((RecruiterRequiredPermission,))
def user_profile(request):
    if request.method == "POST":
        user = request.user
        if "profile_pic" in request.FILES:
            logo = request.FILES.get("profile_pic")
            sup_formates = ["image/jpeg", "image/png"]
            ftype = logo.content_type
            if str(ftype) in sup_formates:
                user.profile_pic = logo
                user.save()
                data = {"error": False, "data": "Profile Pic Uploaded Successfully"}
                return HttpResponse(json.dumps(data))
            data = {
                "error": True,
                "data": "Upload a valid Image format, Ex: PNG, JPEG, JPG",
            }
            return JsonResponse(data)
        data = {"error": True, "data": "Please Upload Profile Pic"}
        return JsonResponse(data)
    user = (
        User.objects.filter(id=request.user.id)
        .prefetch_related("technical_skills", "industry", "functional_area")
        .first()
    )
    return JsonResponse(
        {"error": False, "user": UserSerializer(user).data},
    )


@api_view(["GET"])
@permission_classes((RecruiterRequiredPermission,))
def skill_list(request):
    skills = Skill.objects.exclude(status="InActive").order_by("name")
    return JsonResponse(
        {"error": False, "skills": SkillSerializer(skills, many=True).data},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes((RecruiterRequiredPermission,))
def industry_list(request):
    industries = Industry.objects.exclude(status="InActive").order_by("name")
    return JsonResponse(
        {"error": False, "industries": IndustrySerializer(industries, many=True).data},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes((RecruiterRequiredPermission,))
def city_list(request):
    cities = City.objects.exclude(status="Disabled")
    return JsonResponse(
        {"error": False, "cities": CitySerializer(cities, many=True).data},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes((RecruiterRequiredPermission,))
def state_list(request):
    states = State.objects.exclude(status="Disabled")
    return JsonResponse(
        {"error": False, "states": StateSerializer(states, many=True).data},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes((RecruiterRequiredPermission,))
def functional_area_list(request):
    functional_areas = FunctionalArea.objects.exclude(status="InActive").order_by(
        "name"
    )
    return JsonResponse(
        {
            "error": False,
            "functional_areas": FunctionalAreaSerializer(
                functional_areas, many=True
            ).data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes((RecruiterRequiredPermission,))
def company_list(request):
    companies = Company.objects.all()
    return JsonResponse(
        {"error": False, "companies": CompanySerializer(companies, many=True).data},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes((RecruiterRequiredPermission,))
def view_company(request):
    menu = Menu.objects.filter(company=request.user.company).order_by("lvl")
    return JsonResponse(
        {
            "error": False,
            "company": CompanySerializer(request.user.company).data,
            "menu": MenuSerailizer(menu, many=True).data,
        }
    )
