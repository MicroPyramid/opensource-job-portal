import json
import math
import re
from datetime import datetime

from django.conf import settings
from django.urls import reverse
from django.db.models import Q
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import loader

from mpcomp.views import (
    get_absolute_url,
    get_prev_after_pages_count,
    permission_required,
)
from peeldb.models import (
    GOV_JOB_TYPE,
    JOB_TYPE,
    AppliedJobs,
    City,
    Company,
    Country,
    FunctionalArea,
    Industry,
    JobPost,
    Keyword,
    Qualification,
    Skill,
    TechnicalSkill,
    User,
)
from recruiter.forms import MONTHS, YEARS, JobPostForm
from recruiter.views import (
    add_interview_location,
    add_other_functional_area,
    add_other_qualifications,
    add_other_skills,
)

from ..forms import (
    JobPostTitleForm,
)
from ..tasks import (
    send_email,
)


# Functions to move here from main views.py:


@permission_required("activity_view", "activity_edit")
def post_list(request, job_type):
    posts = JobPost.objects.filter(job_type=job_type)

    if request.POST.get("timestamp", ""):
        date = request.POST.get("timestamp").split(" - ")
        start_date = datetime.strptime(date[0], "%b %d, %Y %H:%M")
        end_date = datetime.strptime(date[1], "%b %d, %Y %H:%M")
        posts = posts.filter(published_on__range=(start_date, end_date))

    if request.POST.get("search", ""):
        posts = posts.filter(
            Q(title__icontains=request.POST.get("search"))
            | Q(company_name__icontains=request.POST.get("search"))
            | Q(status__icontains=request.POST.get("search"))
            | Q(user__username__icontains=request.POST.get("search"))
        )

    items_per_page = 100
    no_pages = int(math.ceil(float(posts.count()) / items_per_page))

    if (
        "page" in request.POST
        and bool(re.search(r"[0-9]", request.POST.get("page")))
        and int(request.POST.get("page")) > 0
    ):
        if int(request.POST.get("page")) > (no_pages + 2):
            return HttpResponseRedirect("/dashboard/")
        page = int(request.POST.get("page"))
    else:
        page = 1

    posts = posts[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    return render(
        request,
        "dashboard/jobpost/post_list.html",
        {
            "posts": posts,
            "job_type": job_type,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "page": page,
        },
    )



@permission_required("activity_view", "activity_edit")
def post_detail(request, post_id):
    post = get_object_or_404(JobPost, id=post_id)
    applicants = AppliedJobs.objects.filter(job_post__id=post_id).select_related(
        "user", "resume_applicant"
    )
    manual_users = applicants.filter(ip_address="", user_agent="")
    applicants = applicants.exclude(ip_address="", user_agent="")
    users = applicants.exclude(user=None)
    resumes = applicants.exclude(resume_applicant=None)

    return render(
        request,
        "dashboard/jobpost/post_view.html",
        {
            "post": post,
            "applicants": users,
            "resumes": resumes,
            "manual_users": manual_users,
        },
    )



def status_change(request, post_id):
    post = JobPost.objects.get(id=post_id)
    if post.status == "Live":
        post.status = "Expired"
        post.save()
    else:
        post.status = "Live"
        post.save()
    c = {"job_post": post, "user": post.user}
    t = loader.get_template("email/jobpost.html")
    subject = "PeelJobs JobPost Status"
    rendered = t.render(c)
    mto = post.user.email
    user_active = True if post.user.is_active else False
    send_email.delay(mto, subject, rendered)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))



@permission_required("activity_edit")
def deactivate_job(request, job_post_id):

    job_post = get_object_or_404(JobPost, id=job_post_id)
   
    job_post.previous_status = job_post.status
    job_post.status = "Disabled"
    job_post.save()

    return HttpResponseRedirect(
        reverse("dashboard:job_posts", args=(job_post.job_type,))
    )


@permission_required("activity_edit")
def delete_job(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    job_type = job_post.job_type
        
    job_post.delete()

    data = {
        "error": False,
        "response": "Job Post deleted Successfully",
        "job_type": job_type,
    }
    return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def publish_job(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    if job_post.status == "Pending":
        job_post.status = "Published"
        job_post.save()
        
    else:
        job_post.status = "Pending"
        job_post.save()
     
    job_post.save()
    
    return HttpResponseRedirect(
        reverse("dashboard:job_posts", args=(job_post.job_type,))
    )


@permission_required("activity_edit")
def enable_job(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    job_post.status = job_post.previous_status
    job_post.save()
        
    return HttpResponseRedirect(
        reverse("dashboard:job_posts", args=(job_post.job_type,))
    )



@permission_required("activity_edit")
def new_govt_job(request, job_type):
    if request.method == "GET":
        countries = Country.objects.all().order_by("name")
        skills = Skill.objects.all().exclude(status="InActive").order_by("name")
        functional_area = (
            FunctionalArea.objects.all().exclude(status="InActive").order_by("name")
        )
        industries = Industry.objects.all().exclude(status="InActive").order_by("name")
        qualifications = (
            Qualification.objects.all().exclude(status="InActive").order_by("name")
        )
        cities = City.objects.filter(status="Enabled").order_by("name")
        companies = Company.objects.filter(is_active=True).order_by("name")
        return render(
            request,
            "dashboard/jobpost/new.html",
            {
                "job_types": JOB_TYPE,
                "functional_area": functional_area,
                "qualifications": qualifications,
                "years": YEARS,
                "months": MONTHS,
                "industries": industries,
                "countries": countries,
                "skills": skills,
                "cities": cities,
                "gov_job_type": GOV_JOB_TYPE,
                "job_type": job_type,
                "companies": companies,
            },
        )
    validate_post = JobPostForm(request.POST, user=request.user)
    errors = validate_post.errors
    no_of_locations = int(json.loads(request.POST["no_of_interview_location"])) + 1

    for key, value in request.POST.items():

        if "final_industry" in request.POST.keys():
            for industry in json.loads(request.POST["final_industry"]):
                for key, value in industry.items():
                    if not value:
                        errors[key] = "This field is required"
        if "final_functional_area" in request.POST.keys():
            for functional_area in json.loads(request.POST["final_functional_area"]):
                for key, value in functional_area.items():
                    if not value:
                        errors[key] = "This field is required"

        if "final_edu_qualification" in request.POST.keys():
            for qualification in json.loads(request.POST["final_edu_qualification"]):
                for key, value in qualification.items():
                    if not value:
                        errors[key] = "This field is required"

        if "final_skills" in request.POST.keys():
            for skill in json.loads(request.POST["final_skills"]):
                for key, value in skill.items():
                    if not value:
                        errors[key] = "This field is required"

    if not errors:
        validate_post = validate_post.save(commit=False)
        validate_post.user = request.user

        if request.POST.get("min_year") == 0:
            validate_post.fresher = True

        validate_post.country = None

        company = Company.objects.get(id=request.POST.get("company"))
        validate_post.company = company
        validate_post.company_links = request.POST.get("company_links")
        validate_post.company_emails = request.POST.get("company_emails")

        if request.POST.get("visa_required"):
            validate_post.visa_required = True
            visa_country = Country.objects.get(id=request.POST.get("visa_country"))
            validate_post.visa_country = visa_country
            validate_post.visa_type = request.POST.get("visa_type")

        validate_post.status = request.POST.get("status")
        validate_post.published_message = request.POST.get("published_message", "")
        validate_post.job_type = request.POST.get("job_type")
        validate_post.pincode = request.POST.get("pincode", "")
        date_format = "%Y-%m-%d %H:%M:%S"
        if request.POST.get("published_date"):
            start_date = datetime.strptime(
                request.POST.get("published_date"), "%m/%d/%Y %H:%M:%S"
            ).strftime("%Y-%m-%d %H:%M:%S")
            published_date = datetime.strptime(start_date, date_format)

        validate_post.job_type = job_type

        validate_post.vacancies = (
            request.POST.get("vacancies") if request.POST.get("vacancies") else 0
        )
        if request.POST.get("major_skill"):
            skill = Skill.objects.filter(id=request.POST.get("major_skill"))
            if skill:
                validate_post.major_skill = skill[0]
        if request.POST.get("job_type") == "government":
            validate_post.vacancies = request.POST.get("vacancies")
            if request.POST.get("application_fee"):
                validate_post.application_fee = request.POST.get("application_fee")

            validate_post.govt_job_type = request.POST.get("govt_job_type")
            validate_post.age_relaxation = request.POST.get("age_relaxation")
            validate_post.important_dates = request.POST.get("important_dates")
            validate_post.how_to_apply = request.POST.get("how_to_apply")
            validate_post.selection_process = request.POST.get("selection_process")

            govt_from_date = datetime.strptime(
                request.POST.get("govt_from_date"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")

            validate_post.govt_from_date = govt_from_date
            govt_to_date = datetime.strptime(
                request.POST.get("govt_to_date"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")

            validate_post.govt_to_date = govt_to_date

            if request.POST.get("govt_exam_date"):
                govt_exam_date = datetime.strptime(
                    request.POST.get("govt_exam_date"), "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
                validate_post.govt_exam_date = govt_exam_date
                validate_post.last_date = govt_exam_date
            else:
                validate_post.last_date = govt_to_date
        if request.POST.get("published_date"):
            validate_post.published_date = published_date
        validate_post.published_on = datetime.now()
        validate_post.slug = get_absolute_url(validate_post)
        validate_post.save()

        no_of_locations = int(json.loads(request.POST["no_of_interview_location"])) + 1
        add_interview_location(request.POST, validate_post, no_of_locations)
        if validate_post.job_type == "walk-in":
            validate_post.vacancies = 0
            validate_post.walkin_contactinfo = request.POST.get("walkin_contactinfo")
            walkin_from_date = datetime.strptime(
                request.POST.get("walkin_from_date"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")

            validate_post.walkin_from_date = walkin_from_date
            walkin_to_date = datetime.strptime(
                request.POST.get("walkin_to_date"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")

            validate_post.walkin_to_date = walkin_to_date
            if request.POST.get("walkin_time"):
                validate_post.walkin_time = request.POST.get("walkin_time")

            validate_post.last_date = walkin_to_date
        if "final_skills" in request.POST.keys():
            add_other_skills(
                validate_post, json.loads(request.POST["final_skills"]), request.user
            )
        if "final_edu_qualification" in request.POST.keys():
            add_other_qualifications(
                validate_post,
                json.loads(request.POST["final_edu_qualification"]),
                request.user,
            )
        if "final_functional_area" in request.POST.keys():
            add_other_functional_area(
                validate_post,
                json.loads(request.POST["final_functional_area"]),
                request.user,
            )

        if request.POST.get("status") == "Pending":

            if request.POST.get("fb_post") == "on":
                validate_post.post_on_fb = True
                validate_post.fb_groups = request.POST.getlist("fb_groups")
            validate_post.post_on_tw = request.POST.get("tw_post") == "on"
            validate_post.post_on_ln = request.POST.get("ln_post") == "on"
        validate_post.save()

        for kw in request.POST.getlist("keywords"):
            if not kw == "":
                key = Keyword.objects.filter(name=kw)
                if not key:
                    keyword = Keyword.objects.create(name=kw)
                    validate_post.keywords.add(keyword)
                else:
                    validate_post.keywords.add(key[0])

        validate_post.location.add(*request.POST.getlist("location"))

        for each in request.POST.getlist("edu_qualification"):
            qualification = Qualification.objects.get(id=each)
            validate_post.edu_qualification.add(qualification)

        for each in request.POST.getlist("skills"):
            skill = Skill.objects.filter(id=each)
            if skill:
                validate_post.skills.add(skill[0])

        for each in request.POST.getlist("industry"):
            industry = Industry.objects.get(id=each)
            validate_post.industry.add(industry)

        for each in request.POST.getlist("functional_area"):
            fa = FunctionalArea.objects.get(id=each)
            validate_post.functional_area.add(fa)
        if (
            validate_post.major_skill
            and validate_post.major_skill not in validate_post.skills.all()
        ):
            validate_post.skills.add(validate_post.major_skill)

        data = {
            "error": False,
            "response": "New Post created",
            "post": validate_post.id,
            "job_type": validate_post.job_type,
        }
        return HttpResponse(json.dumps(data))

    else:
        data = {"error": True, "response": errors}
        return HttpResponse(json.dumps(data))



@permission_required("activity_edit")
def edit_govt_job(request, post_id):
    job_posts = JobPost.objects.filter(id=post_id, user=request.user)
    if request.method == "GET":
        if job_posts:
            job_post = job_posts[0]
            countries = Country.objects.all().order_by("name")
            skills = list(Skill.objects.filter(status="Active"))
            skills.extend(job_post.skills.filter(status="InActive"))
            industries = list(Industry.objects.filter(status="Active").order_by("name"))
            industries.extend(job_post.industry.filter(status="InActive"))
            cities = City.objects.filter(status="Enabled").order_by("name")
            qualifications = list(
                Qualification.objects.filter(status="Active").order_by("name")
            )
            qualifications.extend(job_post.edu_qualification.filter(status="InActive"))

            functional_area = list(
                FunctionalArea.objects.filter(status="Active").order_by("name")
            )
            functional_area.extend(job_post.functional_area.filter(status="InActive"))
            
            companies = Company.objects.filter(
                company_type="Company", is_active=True
            ).order_by("name")
            return render(
                request,
                "dashboard/jobpost/edit.html",
                {
                    "fb_groups": "",
                    "job_types": JOB_TYPE,
                    "qualifications": qualifications,
                    "functional_area": functional_area,
                    "years": YEARS,
                    "months": MONTHS,
                    "job_post": job_post,
                    "industries": industries,
                    "countries": countries,
                    "skills": skills,
                    "cities": cities,
                    "gov_job_type": GOV_JOB_TYPE,
                    "companies": companies,
                },
            )
        else:
            message = "Sorry, No Job Posts Found"
        return render(request, "dashboard/404.html", {"message": message}, status=404)

    job_post = job_posts[0]
    validate_post = JobPostForm(request.POST, user=request.user, instance=job_posts[0])

    errors = validate_post.errors

    for key, value in request.POST.items():

        if "final_industry" in request.POST.keys():
            for industry in json.loads(request.POST["final_industry"]):
                for key, value in industry.items():
                    if not value:
                        errors[key] = "This field is required"
        if "final_functional_area" in request.POST.keys():
            for functional_area in json.loads(request.POST["final_functional_area"]):
                for key, value in functional_area.items():
                    if not value:
                        errors[key] = "This field is required"

        if "final_edu_qualification" in request.POST.keys():
            for qualification in json.loads(request.POST["final_edu_qualification"]):
                for key, value in qualification.items():
                    if not value:
                        errors[key] = "This field is required"

        if "final_skills" in request.POST.keys():
            for skill in json.loads(request.POST["final_skills"]):
                for key, value in skill.items():
                    if not value:
                        errors[key] = "This field is required"

    if not errors:
        post = validate_post.save(commit=False)
        post.fresher = request.POST.get("min_year") == 0
        post.min_salary = (
            request.POST.get("min_salary", 0)
            if request.POST.get("min_salary", 0)
            else 0
        )
        post.max_salary = (
            request.POST.get("max_salary", 0)
            if request.POST.get("max_salary", 0)
            else 0
        )
        post.pincode = request.POST.get("pincode", "")
        if request.POST.get("visa_required"):
            post.visa_required = True
            visa_country = Country.objects.get(id=request.POST.get("visa_country"))
            post.visa_country = visa_country
            post.visa_type = request.POST.get("visa_type")
        else:
            post.visa_required = False
            post.visa_type = ""
            post.visa_country = None
        if request.POST.get("published_date"):
            start_date = datetime.strptime(
                request.POST.get("published_date"), "%m/%d/%Y %H:%M:%S"
            ).strftime("%Y-%m-%d %H:%M:%S")
            date_format = "%Y-%m-%d %H:%M:%S"
            published_date = datetime.strptime(start_date, date_format)
            post.published_date = published_date
        if request.POST.get("major_skill"):
            skill = Skill.objects.filter(id=request.POST.get("major_skill"))
            if skill:
                post.major_skill = skill[0]

        post.status = request.POST.get("status")
        post.published_message = request.POST.get("published_message")

        company = Company.objects.get(id=request.POST.get("company"))
        post.company = company
        post.company_links = request.POST.get("company_links")
        post.company_emails = request.POST.get("company_emails")

        post.job_type = request.POST.get("job_type")
        post.min_year = request.POST.get("min_year", 0)
        post.min_month = request.POST.get("min_month", 0)
        post.max_year = request.POST.get("max_year", 0)
        post.max_month = request.POST.get("max_month", 0)

        if request.POST.get("job_type") == "government":
            post.vacancies = request.POST.get("vacancies")
            if request.POST.get("application_fee"):
                post.application_fee = request.POST.get("application_fee")
            post.govt_job_type = request.POST.get("govt_job_type")
            post.age_relaxation = request.POST.get("age_relaxation")
            post.important_dates = request.POST.get("important_dates")
            post.how_to_apply = request.POST.get("how_to_apply")
            post.selection_process = request.POST.get("selection_process")

            govt_from_date = datetime.strptime(
                request.POST.get("govt_from_date"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")

            post.govt_from_date = govt_from_date
            govt_to_date = datetime.strptime(
                request.POST.get("govt_to_date"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")

            post.govt_to_date = govt_to_date

            if request.POST.get("govt_exam_date"):
                govt_exam_date = datetime.strptime(
                    request.POST.get("govt_exam_date"), "%m/%d/%Y"
                ).strftime("%Y-%m-%d")

                post.govt_exam_date = govt_exam_date

                post.last_date = govt_exam_date
            else:
                post.last_date = govt_to_date

        if request.POST.get("status") == "Pending":
            if request.POST.get("fb_post") == "on":
                post.post_on_fb = True
                post.fb_groups = request.POST.getlist("fb_groups")

            if request.POST.get("tw_post") == "on":
                post.post_on_tw = True

            if request.POST.get("ln_post") == "on":
                post.post_on_ln = True

            t = loader.get_template("email/jobpost.html")
            c = {"job_post": post, "user": post.user}
            subject = "PeelJobs New JobPost"
            rendered = t.render(c)
            mto = [settings.DEFAULT_FROM_EMAIL]
            send_email.delay(mto, subject, rendered)
            post.save()

        post.location.clear()
        post.skills.clear()
        post.industry.clear()
        post.functional_area.clear()
        post.edu_qualification.clear()
        post.keywords.clear()

        if "final_skills" in request.POST.keys():

            add_other_skills(
                post, json.loads(request.POST["final_skills"]), request.user
            )
        if "final_edu_qualification" in request.POST.keys():
            add_other_qualifications(
                post, json.loads(request.POST["final_edu_qualification"]), request.user
            )
        if "final_functional_area" in request.POST.keys():
            add_other_functional_area(
                post, json.loads(request.POST["final_functional_area"]), request.user
            )

        if "other_location" in request.POST.keys():
            temp = loader.get_template("recruiter/email/add_other_fields.html")
            subject = "PeelJobs New JobPost"
            mto = [settings.DEFAULT_FROM_EMAIL]

            c = {
                "job_post": post,
                "user": request.user,
                "value": request.POST["other_location"],
                "type": "Location",
            }
            rendered = temp.render(c)
            send_email.delay(mto, subject, rendered)

        post.job_interview_location.clear()

        no_of_locations = int(json.loads(request.POST["no_of_interview_location"])) + 1
        add_interview_location(request.POST, post, no_of_locations)

        post.edu_qualification.add(*request.POST.getlist("edu_qualification"))
        post.location.add(*request.POST.getlist("location"))
        post.skills.add(*request.POST.getlist("skills"))
        post.industry.add(*request.POST.getlist("industry"))
        post.functional_area.add(*request.POST.getlist("functional_area"))

        for kw in request.POST.getlist("keywords"):
            key = Keyword.objects.filter(name=kw)
            if not kw == "":
                if not key:
                    keyword = Keyword.objects.create(name=kw)
                    post.keywords.add(keyword)
                else:
                    post.keywords.add(key[0])

        if post.job_type == "walk-in":
            post.vacancies = 0
            post.walkin_contactinfo = request.POST.get("walkin_contactinfo")
            walkin_from_date = datetime.strptime(
                request.POST.get("walkin_from_date"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")

            post.walkin_from_date = walkin_from_date
            walkin_to_date = datetime.strptime(
                request.POST.get("walkin_to_date"), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")

            post.walkin_to_date = walkin_to_date
            if request.POST.get("walkin_time"):
                post.walkin_time = request.POST.get("walkin_time")

            post.last_date = walkin_to_date
        post.save()
        if post.major_skill and post.major_skill not in post.skills.all():
            post.skills.add(post.major_skill)
        data = {
            "error": False,
            "response": "Job Post Updated",
            "post": job_post.id,
            "job_type": post.job_type,
        }
        return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "response": errors}

        return HttpResponse(json.dumps(data))




@permission_required("activity_edit")
def preview_job(request, post_id):
    job_post = JobPost.objects.filter(id=post_id, user=request.user)
    if job_post:
        if job_post[0].status == "Draft":
            return render(
                request, "dashboard/jobpost/preview.html", {"job": job_post[0]}
            )
    message = "No Job Preview Available"
    return render(request, "dashboard/404.html", {"message": message}, status=404)




def edit_job_title(request, post_id):
    job_post = get_object_or_404(JobPost, id=post_id)
    companies = Company.objects.filter()
    skills = Skill.objects.all().order_by("name")
    countries = Country.objects.all().order_by("name")
    cities = City.objects.all().order_by("name")
    qualifications = Qualification.objects.all().order_by("name")
    industries = Industry.objects.all().order_by("name")
    functional_areas = FunctionalArea.objects.all().order_by("name")
    if request.POST:
        validate_jobpost = JobPostTitleForm(request.POST, instance=job_post)
        send_mail = job_post.status != "Live"
        if validate_jobpost.is_valid():
            job_post.title = request.POST.get("title", "")
            job_post.description = request.POST.get("description")
            job_post.status = request.POST.get("post_status")
            job_post.pincode = request.POST.get("pincode", "")
            job_post.company_emails = request.POST.get("company_emails", "")
            # job_post.published_on = datetime.now()
            job_post.published_message = request.POST.get("published_message", "")
            if request.POST.get("meta_description"):
                job_post.meta_description = request.POST.get("meta_description")
            if request.POST.get("meta_title"):
                job_post.meta_title = request.POST.get("meta_title")
            if request.POST.get("company"):
                job_post.company_id = request.POST.get("company")
            if request.POST.getlist("skills"):
                job_post.skills.clear()
                job_post.skills.add(*request.POST.getlist("skills"))
            if request.POST.getlist("location"):
                job_post.location.clear()
                job_post.location.add(*request.POST.getlist("location"))
            if request.POST.getlist("edu_qualification"):
                job_post.edu_qualification.clear()
                job_post.edu_qualification.add(
                    *request.POST.getlist("edu_qualification")
                )
            if request.POST.getlist("industry"):
                job_post.industry.clear()
                job_post.industry.add(*request.POST.getlist("industry"))
            if request.POST.getlist("functional_area"):
                job_post.functional_area.clear()
                job_post.functional_area.add(*request.POST.getlist("functional_area"))
            if request.POST.get("salary_type"):
                job_post.salary_type = request.POST.get("salary_type")
            job_post.min_salary = request.POST.get("min_salary") or 0
            job_post.max_salary = request.POST.get("max_salary") or 0
            if request.POST.get("major_skill"):
                skill = Skill.objects.filter(id=request.POST.get("major_skill"))
                if skill:
                    job_post.major_skill = skill[0]
            job_url = get_absolute_url(job_post)
            job_post.slug = job_url
            job_post.save()
            if (
                job_post.major_skill
                and job_post.major_skill not in job_post.skills.all()
            ):
                job_post.skills.add(job_post.major_skill)
            job_post.job_interview_location.clear()

            no_of_locations = (
                int(json.loads(request.POST["no_of_interview_location"])) + 1
            )
            add_interview_location(request.POST, job_post, no_of_locations)
            if job_post.status == "Live" and send_mail:
                t = loader.get_template("email/jobpost.html")
                c = {"job_post": job_post, "user": job_post.user}
                subject = "PeelJobs JobPost Status"
                rendered = t.render(c)
                mto = [job_post.user.email]
                user_active = True if job_post.user.is_active else False
                send_email.delay(mto, subject, rendered)
            data = {"error": False, "response": "Company Updated successfully"}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "response": validate_jobpost.errors}
            return HttpResponse(json.dumps(data))
    return render(
        request,
        "dashboard/jobpost/edit_job_title.html",
        {
            "job_post": job_post,
            "companies": companies,
            "skills": skills,
            "countries": countries,
            "qualifications": qualifications,
            "status": JobPost.POST_STATUS,
            "cities": cities,
            "industries": industries,
            "functional_areas": functional_areas,
        },
    )




@permission_required("activity_edit")
def mail_to_recruiter(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    user = User.objects.get(id=job_post.user.id)
    recruiter_email = user.email
    c = {"job_post": job_post, "user": user, "comments": request.POST.get("comments")}
    t = loader.get_template("email/mail_to_recruiter.html")
    subject = "PeelJobs JobPost"
    rendered = t.render(c)
    mto = recruiter_email
    send_email.delay(mto, subject, rendered)
    return HttpResponseRedirect(
        reverse("dashboard:job_posts", args=(job_post.job_type,))
    )


