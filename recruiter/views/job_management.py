import json
import math

from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.template import loader, Template, Context
from django.template.loader import render_to_string
from datetime import datetime
from django.utils import timezone
from django.db.models import Q, Count


from dashboard.tasks import send_email
from peeldb.models import (
    Country,
    JobPost,
    MetaData,
    City,
    Skill,
    Industry,
    Qualification,
    AppliedJobs,
    User,
    JOB_TYPE,
    FunctionalArea,
    Company,
    AGENCY_INVOICE_TYPE,
    AGENCY_JOB_TYPE,
    AgencyCompany,
    AGENCY_RECRUITER_JOB_TYPE,
    AgencyResume,
    POST,
    UserMessage,
)
from recruiter.forms import (
    JobPostForm,
    YEARS,
    MONTHS,
    ApplicantResumeForm,
)

from mpcomp.views import (
    recruiter_login_required,
    get_prev_after_pages_count,
)
from recruiter.views.job_helpers import adding_other_fields_data, retreving_form_errors, save_job_post




@recruiter_login_required
def jobs_list(request):
    if request.user.agency_admin:
        active_jobs_list = (
            JobPost.objects.filter(user__company=request.user.company)
            .exclude(status="Disabled")
            .exclude(status="Expired")
            .prefetch_related("location", "agency_recruiters")
            .annotate(responses=Count("appliedjobs"))
            .order_by("-id")
        )
    elif request.user.is_agency_recruiter:
        active_jobs_list = (
            JobPost.objects.filter(
                Q(agency_recruiters__in=[request.user]) | Q(user=request.user)
            )
            .exclude(status="Disabled")
            .exclude(status="Expired")
            .prefetch_related("location", "agency_recruiters")
            .annotate(responses=Count("appliedjobs"))
            .order_by("-id")
            .distinct()
        )
    else:
        active_jobs_list = (
            JobPost.objects.filter(user=request.user)
            .exclude(status="Disabled")
            .exclude(status="Expired")
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

    return render(
        request,
        # "recruiter/job/list.html",
        'recruiter_v2/jobs/list.html',
        {
            "jobs_list": active_jobs_list,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "search_value": (
                request.POST["search_value"]
                if "search_value" in request.POST
                else "All"
            ),
        },
    )




@recruiter_login_required
def inactive_jobs(request):
    inactive_jobs_list = JobPost.objects.filter(
        Q(user=request.user.id) & Q(status="Disabled") | Q(status="Expired")
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

    return render(
        request,
        "recruiter/job/list.html",
        {
            "jobs_list": inactive_jobs_list,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "search_value": (
                request.POST["search_value"]
                if "search_value" in request.POST.keys()
                else "All"
            ),
        },
    )




@recruiter_login_required
def new_job(request, status):
    if request.method == "GET":
        if request.GET.get("q"):
            companies = Company.objects.filter(
                name__icontains=request.GET.get("q"), is_active=True
            ).distinct()[:10]
            companies_names = []
            for each in companies:
                companies_names.append(each.name)
            if request.GET.get("register_name"):
                company = Company.objects.filter(
                    name=request.GET.get("register_name")
                ).first()
                if company:
                    each_obj = {}
                    each_obj["website"] = company.website
                    each_obj["company_type"] = company.company_type
                    each_obj["company_id"] = company.id
                    each_obj["company_address"] = company.address
                    each_obj["company_profile"] = company.profile
                    each_obj["company_profile_pic"] = company.profile_pic
                    data = {"company": each_obj}
                    return HttpResponse(json.dumps(data))
            data = {"response": companies_names}
            return HttpResponse(json.dumps(data))

        if request.user.is_active:
            if (
                request.user.is_company_recruiter
                and not request.user.is_admin
                and not request.user.has_perm("jobposts_edit")
            ):
                message = "You Don't have permission to create a new job"
                reason = "Please contact your agency admin"
                return render(
                    request,
                    "recruiter/recruiter_404.html",
                    {"message": message, "reason": reason},
                    status=404,
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
                    job_type=status, user__company=request.user.company
                )
            else:
                jobposts = JobPost.objects.filter(job_type=status, user=request.user)

            clients = AgencyCompany.objects.filter(company=request.user.company)
            show_clients = True
            show_recruiters = True
            if request.user.is_agency_recruiter:
                show_clients = False if not clients else True
                show_recruiters = False if not recruiters else True
            return render(
                request,
                "recruiter_v2/jobs/new.html",
                {
                    "job_types": JOB_TYPE,
                    "functional_area": functional_area,
                    "qualifications": qualifications,
                    "years": YEARS,
                    "months": MONTHS,
                    "industries": industries,
                    "countries": countries,
                    "skills": skills,
                    "jobposts": jobposts,
                    "cities": cities,
                    "status": status,
                    "agency_invoice_types": AGENCY_INVOICE_TYPE,
                    "agency_job_types": AGENCY_JOB_TYPE,
                    "recruiters": recruiters,
                    "clients": clients,
                    "show_clients": show_clients,
                    "show_recruiters": show_recruiters,
                },
            )
        else:
            message = "Sorry, Your account is not verified"
            reason = "Please verify your email id"
            return render(
                request,
                "recruiter/recruiter_404.html",
                {"message": message, "reason": reason},
                status=404,
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
        mto = settings.SUPPORT_EMAILS
        send_email.delay(mto, subject, rendered)
        data = {
            "error": False,
            "response": "New Post created",
            "post": validate_post.id,
        }
        return HttpResponse(json.dumps(data))
    data = {"error": True, "response": errors}
    return HttpResponse(json.dumps(data))




@recruiter_login_required
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
                
                return render(
                    request,
                    "recruiter/job/edit.html",
                    {
                        "fb_groups": '',
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
                        "recruiters": recruiters,
                        "agency_invoice_types": AGENCY_INVOICE_TYPE,
                        "agency_job_types": AGENCY_JOB_TYPE,
                        "clients": clients,
                    },
                )
            else:
                message = "Sorry, No Job Posts Found"
                reason = "The URL may be misspelled or the job you're looking for is no longer available."
        else:
            message = "Sorry, Your mobile number is not verified"
            reason = "Please verify your mobile number"
        return render(
            request,
            "recruiter/recruiter_404.html",
            {"message": message, "reason": reason},
            status=404,
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
        return HttpResponse(json.dumps(data))
    data = {"error": True, "response": errors}
    return HttpResponse(json.dumps(data))




@recruiter_login_required
def copy_job(request, status):
    if request.user.agency_admin or request.user.has_perm("jobposts_edit"):
        jobposts = JobPost.objects.filter(
            job_type=status, user__company=request.user.company
        )
        job_post = JobPost.objects.filter(
            id=request.GET.get("jobpost_id"), user__company=request.user.company
        ).first()
    else:
        jobposts = JobPost.objects.filter(job_type=status, user=request.user)
        job_post = JobPost.objects.filter(
            id=request.GET.get("jobpost_id"), user=request.user
        ).first()

    if request.method == "GET":
        if request.user.mobile_verified:
            if job_post:
                countries = Country.objects.all().order_by("name")
                skills = list(Skill.objects.filter(status="Active").order_by("name"))
                skills.extend(job_post.skills.filter(status="InActive"))

                cities = list(City.objects.filter(status="Enabled").order_by("name"))
                cities.extend(job_post.location.filter(status="Disabled"))

                industries = list(
                    Industry.objects.filter(status="Active").order_by("name")
                )
                industries.extend(job_post.industry.filter(status="InActive"))

                qualifications = list(
                    Qualification.objects.filter(status="Active").order_by("name")
                )
                qualifications.extend(
                    job_post.edu_qualification.filter(status="InActive")
                )

                recruiters = User.objects.filter(company=request.user.company)
                clients = AgencyCompany.objects.filter(company=request.user.company)

                functional_area = list(
                    FunctionalArea.objects.all()
                    .exclude(status="InActive")
                    .order_by("name")
                )
                functional_area.extend(
                    job_post.functional_area.filter(status="InActive")
                )

                return render(
                    request,
                    "recruiter/job/copy.html",
                    {
                        "job_types": JOB_TYPE,
                        "qualifications": qualifications,
                        "functional_area": functional_area,
                        "years": YEARS,
                        "months": MONTHS,
                        "job_post": job_post,
                        "industries": industries,
                        "countries": countries,
                        "skills": skills,
                        "jobposts": jobposts,
                        "cities": cities,
                        "status": status,
                        "recruiters": recruiters,
                        "agency_job_types": AGENCY_JOB_TYPE,
                        "agency_invoice_types": AGENCY_INVOICE_TYPE,
                        "clients": clients,
                    },
                )
            message = "Sorry, No Job Posts Found"
            reason = "The URL may be misspelled or the job you're looking for is no longer available."
            return render(
                request,
                "recruiter/recruiter_404.html",
                {"message_type": "404", "message": message, "reason": reason},
                status=404,
            )
        message = "Sorry, Your mobile number is not verified"
        reason = "Please verify your mobile number"
        return render(
            request,
            "recruiter/recruiter_404.html",
            {"message_type": "404", "message": message, "reason": reason},
            status=404,
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
        mto = settings.SUPPORT_EMAILS
        send_email.delay(mto, subject, rendered)
        data = {
            "error": False,
            "response": "Job Post Created Successfully",
            "post": validate_post.id,
        }
        return HttpResponse(json.dumps(data))
    return HttpResponse(json.dumps({"error": True, "response": errors}))





@recruiter_login_required
def view_job(request, job_post_id):
    if request.POST.get("post_message"):
        msg = UserMessage.objects.create(
            message=request.POST.get("message"),
            message_from=request.user,
            message_to=User.objects.get(id=int(request.POST.get("message_to"))),
            job=int(request.POST.get("job_id")),
        )

        time = datetime.now().strftime("%b. %d, %Y, %l:%M %p")
        return HttpResponse(
            json.dumps(
                {
                    "error": False,
                    "message": request.POST.get("message"),
                    "msg_id": msg.id,
                    "time": time,
                }
            )
        )
    if request.POST.get("get_applicant"):
        if request.POST.get("user_type") == "resume_pool":
            user = AgencyResume.objects.filter(id=request.POST.get("user_id")).first()
            applicant = render_to_string(
                "recruiter/job/resume_applicant.html", {"user": user}
            )
        else:
            user = User.objects.filter(id=request.POST.get("user_id")).first()
            UserMessage.objects.filter(
                message_to=request.user.id,
                message_from=user.id,
                job=int(job_post_id),
            ).update(is_read=True)

            m1 = UserMessage.objects.filter(
                message_from=user.id,
                message_to=request.user.id,
                job=int(job_post_id),
            )

            m2 = UserMessage.objects.filter(
                message_to=user.id,
                message_from=request.user.id,
                job=int(job_post_id),
            )

            messages = list(m1) + list(m2)
            try:
                user_pic = user.profile_pic.url
            except:
                user_pic = user.photo
            try:
                profile_pic = request.user.profile_pic.url
            except:
                profile_pic = request.user.photo
            if not user_pic:
                user_pic = "https://cdn.peeljobs.com/dummy.jpg"
            if not profile_pic:
                profile_pic = "https://cdn.peeljobs.com/dummy.jpg"
            applicant = render_to_string(
                "recruiter/job/applicant_profile.html",
                {
                    "user": user,
                    "messages": list(messages),
                    "job_id": job_post_id,
                    "user_pic": user_pic,
                    "profile_pic": profile_pic,
                },
                request,
            )
        if user:
            return HttpResponse(json.dumps({"error": False, "profile": applicant}))
        return HttpResponse(
            json.dumps({"error": True, "response": "Profile Not Found!"})
        )
    if request.user.agency_admin:
        jobposts = JobPost.objects.filter(
            id=job_post_id, user__company=request.user.company
        )
    elif request.user.is_agency_recruiter:
        jobposts = JobPost.objects.filter(
            Q(user=request.user) | Q(agency_recruiters__in=[request.user])
        )
    else:
        jobposts = JobPost.objects.filter(id=job_post_id, user=request.user)
    if jobposts:
        jobpost = jobposts[0]
        all_applicants = (
            AppliedJobs.objects.filter(job_post=jobpost)
            .prefetch_related("user", "resume_applicant")
            .distinct()
        )
        shortlisted_applicants = all_applicants.filter(status="Shortlisted")
        rejected_applicants = all_applicants.filter(status="Rejected")
        selected_applicants = all_applicants.filter(status="Selected")
        process_applicants = all_applicants.filter(status="Process")
        pending_applicants = all_applicants.filter(status="Pending")
        if request.POST.get("search_value"):
            if request.POST.get("search_value") == "users":
                all_applicants = all_applicants.exclude(user=None)
                shortlisted_applicants = shortlisted_applicants.exclude(user=None)
                rejected_applicants = rejected_applicants.exclude(user=None)
                selected_applicants = selected_applicants.exclude(user=None)
                process_applicants = process_applicants.exclude(user=None)
                pending_applicants = pending_applicants.exclude(user=None)
            if request.POST.get("search_value") == "resume_pool":
                all_applicants = all_applicants.exclude(resume_applicant=None)
                shortlisted_applicants = shortlisted_applicants.exclude(
                    resume_applicant=None
                )
                rejected_applicants = rejected_applicants.exclude(resume_applicant=None)
                selected_applicants = selected_applicants.exclude(resume_applicant=None)
                process_applicants = process_applicants.exclude(resume_applicant=None)
                pending_applicants = pending_applicants.exclude(resume_applicant=None)
        search_location = request.POST.getlist("location")
        search_skills = request.POST.getlist("skills")
        if search_location or search_skills:
            all_applicants = all_applicants.filter(
                Q(user__current_city__id__in=search_location)
                | Q(user__skills__skill__id__in=search_skills)
            )
            shortlisted_applicants = shortlisted_applicants.filter(
                Q(user__current_city__id__in=search_location)
                | Q(user__skills__skill__id__in=search_skills)
            )
            rejected_applicants = rejected_applicants.filter(
                Q(user__current_city__id__in=search_location)
                | Q(user__skills__skill__id__in=search_skills)
            )
            selected_applicants = selected_applicants.filter(
                Q(user__current_city__id__in=search_location)
                | Q(user__skills__skill__id__in=search_skills)
            )
            process_applicants = process_applicants.filter(
                Q(user__current_city__id__in=search_location)
                | Q(user__skills__skill__id__in=search_skills)
            )
            pending_applicants = pending_applicants.filter(
                Q(user__current_city__id__in=search_location)
                | Q(user__skills__skill__id__in=search_skills)
            )
        # if request.user.agency_admin:
        #     work_logs = AgencyWorkLog.objects.filter(job_post=jobpost)
        # else:
        #     work_logs = AgencyWorkLog.objects.filter(user=request.user, job_post=jobpost)
        exclude_applicants = all_applicants.values_list("resume_applicant", flat=True)
        ids = filter(None, exclude_applicants)
        agency_resumes = AgencyResume.objects.filter(uploaded_by=request.user).exclude(
            id__in=ids
        )
        if request.POST.get("search_value") == "users":
            agency_resumes = []
        if request.POST.getlist("applicants"):
            validate_resume_applicant = ApplicantResumeForm(request.POST)
            if validate_resume_applicant.is_valid():
                for resume in request.POST.getlist("applicants"):
                    applied_jobs = AppliedJobs.objects.filter(
                        resume_applicant__id=resume,
                        job_post__id=request.POST.get("job_post"),
                    )
                    if not applied_jobs:
                        AppliedJobs.objects.create(
                            status=request.POST.get("status"),
                            resume_applicant_id=resume,
                            job_post_id=request.POST.get("job_post"),
                            ip_address=request.META["REMOTE_ADDR"],
                            user_agent=request.META["HTTP_USER_AGENT"],
                        )
                    else:
                        applied_jobs = applied_jobs[0]
                        applied_jobs.status = request.POST.get("status")
                        applied_jobs.save()
                data = {"error": False, "response": "JobPosts Added Successfully"}
                return HttpResponse(json.dumps(data))
            data = {"error": True, "response": validate_resume_applicant.errors}
            return HttpResponse(json.dumps(data))
        meta_title = meta_description = ""
        meta = MetaData.objects.filter(name="job_detail_page")
        if meta:
            meta_title = Template(meta[0].meta_title).render(Context({"job": jobpost}))
            meta_description = Template(meta[0].meta_description).render(
                Context({"job": jobpost})
            )
        return render(
            request,
            "recruiter/job/view.html",
            {
                "jobpost": jobpost,
                "jobpost_assigned_status": AGENCY_RECRUITER_JOB_TYPE,
                "selected_applicants": selected_applicants,
                "shortlisted_applicants": shortlisted_applicants,
                "process_applicants": process_applicants,
                "pending_applicants": pending_applicants,
                "rejected_applicants": rejected_applicants,
                "agency_resumes": agency_resumes,
                "search_skills": search_skills if search_skills else "",
                "search_location": search_location if search_location else "",
                "meta_title": meta_title,
                "meta_description": meta_description,
            },
        )
    else:
        reason = "The URL may be misspelled or the job you're looking for is no longer available."
        return render(
            request,
            "recruiter/recruiter_404.html",
            {"message": "Sorry, No Job Posts Found", "reason": reason},
            status=404,
        )



@recruiter_login_required
def preview_job(request, job_post_id):
    if request.user.is_agency_recruiter:
        job_post = JobPost.objects.filter(
            id=job_post_id, user__company=request.user.company
        )
        if not request.user.agency_admin:
            job_post = job_post.filter(
                Q(user=request.user) | Q(agency_recruiters__in=[request.user])
            )
    else:
        job_post = JobPost.objects.filter(id=job_post_id, user=request.user)
    if job_post:
        if job_post[0].status == "Pending":
            return render(request, "recruiter/job/view.html", {"jobpost": job_post[0]})
    message_type = "404"
    message = "No Job Preview Available"
    reason = "The URL may be misspelled or the job you're looking for is no longer available."
    return render(
        request,
        "recruiter/recruiter_404.html",
        {"message_type": message_type, "message": message, "reason": reason},
        status=404,
    )




@recruiter_login_required
def deactivate_job(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    if request.user.is_agency_admin or request.user == job_post.user:
               
        job_post.previous_status = job_post.status
        job_post.closed_date = timezone.now()
        job_post.status = "Disabled"
        job_post.save()
        data = {"error": False, "response": "Job Post Deactivated"}
        return HttpResponse(json.dumps(data))
    data = {"error": True, "response": "You don't permissions to deactivate this Job"}
    return HttpResponse(json.dumps(data))



@recruiter_login_required
def delete_job(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id, user=request.user)
    
    job_post.status = "Disabled"
    job_post.closed_date = timezone.now()
    job_post.save()

    data = {"error": False, "response": "Job Post deleted Successfully"}
    return HttpResponse(json.dumps(data))



@recruiter_login_required
def enable_job(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    job_post.status = "Pending"
    job_post.closed_date = None
    job_post.save()
    data = {"error": False, "response": "Job Post enabled Successfully"}
    return HttpResponse(json.dumps(data))

