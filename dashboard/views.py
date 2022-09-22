import csv
import json
import math
import re
import urllib
from calendar import monthrange
from datetime import datetime

import requests
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import ContentType, Permission
from django.urls import reverse
from django.db.models import Count, Q
from django.forms import modelformset_factory
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.template.defaultfilters import slugify
from django.core.cache import cache
from django.utils import timezone
from microurl import google_mini
from twython.api import Twython
from django.shortcuts import redirect

from mpcomp.views import (
    get_absolute_url,
    get_aws_file_path,
    get_prev_after_pages_count,
    permission_required,
)
from mpcomp.aws import AWS
from peeldb.models import (
    GOV_JOB_TYPE,
    JOB_TYPE,
    AppliedJobs,
    City,
    Company,
    Country,
    FacebookGroup,
    FacebookPost,
    FunctionalArea,
    Google,
    Industry,
    JobAlert,
    JobPost,
    Keyword,
    Language,
    MailTemplate,
    Menu,
    MetaData,
    Qualification,
    Question,
    SearchResult,
    SentMail,
    Skill,
    Solution,
    State,
    Subscriber,
    TechnicalSkill,
    Ticket,
    TwitterPost,
    User,
    UserEmail,
    Degree,
    EducationInstitue,
    Project,
    AgencyCompanyBranch,
    AgencyResume,
    SKILL_TYPE,
)
from pjob.views import months
from recruiter.forms import MONTHS, YEARS, JobPostForm, MenuForm
from recruiter.views import (
    add_interview_location,
    add_other_functional_area,
    add_other_industry,
    add_other_qualifications,
    add_other_skills,
)

from .forms import (
    ChangePasswordForm,
    CityForm,
    CompanyForm,
    CountryForm,
    FunctionalAreaForm,
    IndustryForm,
    JobPostTitleForm,
    LanguageForm,
    MailTemplateForm,
    QualificationForm,
    MetaForm,
    QuestionForm,
    SkillForm,
    SolutionForm,
    StateForm,
    UserForm,
)
from .tasks import (
    del_jobpost_fb,
    del_jobpost_peel_fb,
    del_jobpost_tw,
    fbpost,
    poston_allfb_groups,
    postongroup,
    postonpage,
    postonpeel_fb,
    postontwitter,
    sending_mail,
    send_email,
)


def index(request):
    if request.user.is_authenticated:
        if (
            not request.user.is_jobseeker
            and not request.user.is_recruiter
            and not request.user.is_agency_recruiter
        ):
            current_date = datetime.strptime(
                str(datetime.now().date()), "%Y-%m-%d"
            ).strftime("%Y-%m-%d")
            today_admin_walkin_jobs_count = JobPost.objects.filter(
                job_type="walk-in",
                user__is_superuser=True,
            )
            today_tickets_open = Ticket.objects.filter(
                created_on__contains=current_date, status="Open"
            ).count()
            today_tickets_closed = Ticket.objects.filter(
                created_on__contains=current_date, status="Closed"
            ).count()
            if request.POST.get("timestamp", ""):
                date = request.POST.get("timestamp").split(" - ")
                start_date = datetime.strptime(date[0], "%b %d, %Y %H:%M")
                end_date = datetime.strptime(date[1], "%b %d, %Y %H:%M")

                today_jobs_count = JobPost.objects.filter(
                    published_on__range=(start_date, end_date)
                ).exclude(user__is_superuser=True)
                today_full_time_jobs_count = today_jobs_count.filter(
                    job_type="full-time"
                )
                today_govt_jobs_count = today_jobs_count.filter(job_type="government")
                today_internship_jobs_count = today_jobs_count.filter(
                    job_type="internship"
                )
                today_walkin_jobs_count = today_jobs_count.filter(job_type="walk-in")
                today_skills = Skill.objects.filter(
                    id__in=JobPost.objects.filter(
                        published_on__range=(start_date, end_date)
                    ).values_list("skills", flat=True)
                )
                job_loc = JobPost.objects.filter(
                    published_on__range=(start_date, end_date)
                ).values_list("location", flat=True)
                user_loc = User.objects.filter(
                    date_joined__range=(start_date, end_date), user_type="JS"
                ).values_list("current_city", flat=True)
                today_locations = City.objects.filter(id__in=job_loc)
                today_user_locations = City.objects.filter(id__in=user_loc)
                today_companies_active = Company.objects.filter(
                    id__in=JobPost.objects.filter(
                        published_on__range=(start_date, end_date)
                    ).values_list("company", flat=True),
                    is_active=True,
                ).count()
                today_companies_not_active = Company.objects.filter(
                    id__in=JobPost.objects.filter(
                        published_on__range=(start_date, end_date)
                    ).values_list("company", flat=True),
                    is_active=False,
                ).count()

                today_admin_jobs_count = JobPost.objects.filter(
                    published_on__range=(start_date, end_date), user__is_superuser=True
                )
                today_admin_full_time_jobs_count = today_admin_jobs_count.filter(
                    job_type="full-time"
                )
                today_admin_internship_jobs_count = today_admin_jobs_count.filter(
                    job_type="internship"
                )
                today_job_applications = AppliedJobs.objects.filter(
                    applied_on__range=(start_date, end_date)
                )
                today_social_applicants = User.objects.filter(
                    date_joined__range=(start_date, end_date),
                    user_type="JS",
                    registered_from="Social",
                )
                today_register_applicants = User.objects.filter(
                    date_joined__range=(start_date, end_date),
                    user_type="JS",
                    registered_from="Email",
                )
                today_resume_applicants = User.objects.filter(
                    date_joined__range=(start_date, end_date),
                    user_type="JS",
                    registered_from="Resume",
                )
                today_recruiters = User.objects.filter(
                    date_joined__range=(start_date, end_date), user_type="RR"
                )
                today_agency_recruiters = User.objects.filter(
                    date_joined__range=(start_date, end_date), user_type="AA"
                )
            else:
                today_jobs_count = JobPost.objects.filter(
                    published_on__icontains=current_date
                ).exclude(user__is_superuser=True)

                today_full_time_jobs_count = JobPost.objects.filter(
                    job_type="full-time", published_on__icontains=current_date
                ).exclude(user__is_superuser=True)
                today_govt_jobs_count = JobPost.objects.filter(
                    job_type="government", published_on__icontains=current_date
                ).exclude(user__is_superuser=True)
                today_internship_jobs_count = JobPost.objects.filter(
                    job_type="internship", published_on__icontains=current_date
                ).exclude(user__is_superuser=True)
                today_walkin_jobs_count = JobPost.objects.filter(
                    job_type="walk-in", published_on__icontains=current_date
                ).exclude(user__is_superuser=True)
                today_admin_jobs_count = JobPost.objects.filter(
                    published_on__icontains=current_date, user__is_superuser=True
                )
                today_admin_full_time_jobs_count = JobPost.objects.filter(
                    job_type="full-time",
                    published_on__icontains=current_date,
                    user__is_superuser=True,
                )
                today_admin_internship_jobs_count = JobPost.objects.filter(
                    job_type="internship",
                    published_on__icontains=current_date,
                    user__is_superuser=True,
                )
                today_admin_walkin_jobs_count = today_admin_walkin_jobs_count.filter(
                    published_on__icontains=current_date,
                )
                today_job_applications = AppliedJobs.objects.filter(
                    applied_on__contains=current_date
                )
                today_social_applicants = User.objects.filter(
                    date_joined__contains=current_date,
                    user_type="JS",
                    registered_from="Social",
                )
                today_register_applicants = User.objects.filter(
                    date_joined__contains=current_date,
                    user_type="JS",
                    registered_from="Email",
                )
                today_resume_applicants = User.objects.filter(
                    date_joined__contains=current_date,
                    user_type="JS",
                    registered_from="Resume",
                )
                today_recruiters = User.objects.filter(
                    date_joined__contains=current_date, user_type="RR"
                )
                today_agency_recruiters = User.objects.filter(
                    date_joined__contains=current_date, user_type="AA"
                )
                today_skills = Skill.objects.filter(
                    id__in=JobPost.objects.filter(
                        published_on__icontains=current_date
                    ).values_list("skills", flat=True)
                )
                job_loc = JobPost.objects.filter(
                    published_on__icontains=current_date
                ).values_list("location", flat=True)
                user_loc = User.objects.filter(
                    date_joined__contains=current_date, user_type="JS"
                ).values_list("current_city", flat=True)
                today_locations = City.objects.filter(id__in=job_loc)
                today_user_locations = City.objects.filter(id__in=user_loc)

                today_companies_active = Company.objects.filter(
                    id__in=JobPost.objects.filter(
                        published_on__icontains=current_date
                    ).values_list("company", flat=True),
                    is_active=True,
                ).count()
                today_companies_not_active = Company.objects.filter(
                    id__in=JobPost.objects.filter(
                        published_on__icontains=current_date
                    ).values_list("company", flat=True),
                    is_active=False,
                ).count()

            total_jobs_list = JobPost.objects.all()
            total_pending_jobs = total_jobs_list.filter(status="Pending").count()
            total_published_jobs = total_jobs_list.filter(status="Published").count()
            total_live_jobs = total_jobs_list.filter(status="Live").count()
            total_disabled_jobs = total_jobs_list.filter(status="Disabled").count()
            total_full_time_jobs = JobPost.objects.filter(job_type="full-time")
            total_fulltime_pending_jobs = total_full_time_jobs.filter(
                status="Pending"
            ).count()
            total_fulltime_published_jobs = total_full_time_jobs.filter(
                status="Published"
            ).count()
            total_fulltime_live_jobs = total_full_time_jobs.filter(
                status="Live"
            ).count()
            total_fulltime_disabled_jobs = total_full_time_jobs.filter(
                status="Disabled"
            ).count()

            total_internship_jobs = JobPost.objects.filter(job_type="internship")
            total_internship_pending_jobs = total_internship_jobs.filter(
                status="Pending"
            ).count()
            total_internship_published_jobs = total_internship_jobs.filter(
                status="Published"
            ).count()
            total_internship_live_jobs = total_internship_jobs.filter(
                status="Live"
            ).count()
            total_internship_disabled_jobs = total_internship_jobs.filter(
                status="Disabled"
            ).count()

            total_walkin_jobs = JobPost.objects.filter(job_type="walk-in")
            total_walkin_pending_jobs = total_walkin_jobs.filter(
                status="Pending"
            ).count()
            total_walkin_published_jobs = total_walkin_jobs.filter(
                status="Published"
            ).count()
            total_walkin_live_jobs = total_walkin_jobs.filter(status="Live").count()
            total_walkin_disabled_jobs = total_walkin_jobs.filter(
                status="Disabled"
            ).count()

            total_govt_jobs = JobPost.objects.filter(job_type="government")
            total_govt_pending_jobs = total_govt_jobs.filter(status="Pending").count()
            total_govt_published_jobs = total_govt_jobs.filter(
                status="Published"
            ).count()
            total_govt_live_jobs = total_govt_jobs.filter(status="Live").count()
            total_govt_disabled_jobs = total_govt_jobs.filter(status="Disabled").count()
            total_job_applications = AppliedJobs.objects.filter()

            total_social_applicants = User.objects.filter(
                user_type="JS", registered_from="Social"
            )
            social_login_once_applicants = total_social_applicants.filter(
                is_login=False
            ).count()
            social_resume_applicants = total_social_applicants.exclude(
                resume=""
            ).count()
            social_applied_applicants = total_social_applicants.filter(
                id__in=total_job_applications.values_list("user", flat=True)
            ).count()
            social_profile_applicants = total_social_applicants.filter(
                profile_completeness__gte=50
            ).count()

            today_social_login_once_applicants = today_social_applicants.filter(
                is_login=False
            ).count()
            today_social_resume_applicants = today_social_applicants.exclude(
                resume=""
            ).count()
            today_social_profile_applicants = today_social_applicants.filter(
                profile_completeness__gte=50
            ).count()
            today_social_applied_applicants = today_social_applicants.filter(
                id__in=today_job_applications.values_list("user", flat=True)
            ).count()

            total_register_applicants = User.objects.filter(
                user_type="JS", registered_from="Email"
            )
            register_login_once_applicants = total_register_applicants.filter(
                is_login=False
            ).count()
            register_resume_applicants = total_register_applicants.exclude(
                resume=""
            ).count()
            register_applied_applicants = total_register_applicants.filter(
                id__in=total_job_applications.values_list("user", flat=True)
            ).count()
            register_profile_applicants = total_register_applicants.filter(
                profile_completeness__gte=50
            ).count()

            today_register_login_once_applicants = today_register_applicants.filter(
                is_login=False
            ).count()
            today_register_resume_applicants = today_register_applicants.exclude(
                resume=""
            ).count()
            today_register_profile_applicants = today_register_applicants.filter(
                profile_completeness__gte=50
            ).count()
            today_register_applied_applicants = today_register_applicants.filter(
                id__in=today_job_applications.values_list("user", flat=True)
            ).count()

            resume_applicants = User.objects.filter(
                user_type="JS", registered_from="Resume"
            )
            resume_login_once_applicants = resume_applicants.filter(
                is_login=False
            ).count()
            resume_applied_applicants = resume_applicants.filter(
                id__in=total_job_applications.values_list("user", flat=True)
            ).count()
            resume_profile_applicants = resume_applicants.filter(
                profile_completeness__gte=50
            ).count()

            today_resume_applied_applicants = today_resume_applicants.filter(
                id__in=today_job_applications.values_list("user", flat=True)
            ).count()
            today_resume_profile_applicants = today_resume_applicants.filter(
                profile_completeness__gte=50
            ).count()
            today_resume_login_once_applicants = today_resume_applicants.filter(
                is_login=False
            ).count()

            today_internship_pending_jobs = today_internship_jobs_count.filter(
                status="Pending"
            ).count()
            today_internship_published_jobs = today_internship_jobs_count.filter(
                status="Published"
            ).count()
            today_internship_live_jobs = today_internship_jobs_count.filter(
                status="Live"
            ).count()
            today_internship_disabled_jobs = today_internship_jobs_count.filter(
                status="Disabled"
            ).count()

            today_admin_internship_pending_jobs = (
                today_admin_internship_jobs_count.filter(status="Pending").count()
            )
            today_admin_internship_published_jobs = (
                today_admin_internship_jobs_count.filter(status="Published").count()
            )
            today_admin_internship_live_jobs = today_admin_internship_jobs_count.filter(
                status="Live"
            ).count()
            today_admin_internship_disabled_jobs = (
                today_admin_internship_jobs_count.filter(status="Disabled").count()
            )

            today_walkin_pending_jobs = today_walkin_jobs_count.filter(
                status="Pending"
            ).count()
            today_walkin_published_jobs = today_walkin_jobs_count.filter(
                status="Published"
            ).count()
            today_walkin_live_jobs = today_walkin_jobs_count.filter(
                status="Live"
            ).count()
            today_walkin_disabled_jobs = today_walkin_jobs_count.filter(
                status="Disabled"
            ).count()

            today_admin_walkin_pending_jobs = today_admin_walkin_jobs_count.filter(
                status="Pending"
            ).count()
            today_admin_walkin_published_jobs = today_admin_walkin_jobs_count.filter(
                status="Published"
            ).count()
            today_admin_walkin_live_jobs = today_admin_walkin_jobs_count.filter(
                status="Live"
            ).count()
            today_admin_walkin_disabled_jobs = today_admin_walkin_jobs_count.filter(
                status="Disabled"
            ).count()

            today_govt_pending_jobs = today_govt_jobs_count.filter(
                status="Pending"
            ).count()
            today_govt_published_jobs = today_govt_jobs_count.filter(
                status="Published"
            ).count()
            today_govt_live_jobs = today_govt_jobs_count.filter(status="Live").count()
            today_govt_disabled_jobs = today_govt_jobs_count.filter(
                status="Disabled"
            ).count()

            today_pending_jobs = today_jobs_count.filter(status="Pending").count()
            today_published_jobs = today_jobs_count.filter(status="Published").count()
            today_live_jobs = today_jobs_count.filter(status="Live").count()
            today_disabled_jobs = today_jobs_count.filter(status="Disabled").count()

            today_fulltime_pending_jobs = today_full_time_jobs_count.filter(
                status="Pending"
            ).count()
            today_fulltime_published_jobs = today_full_time_jobs_count.filter(
                status="Published"
            ).count()
            today_fulltime_live_jobs = today_full_time_jobs_count.filter(
                status="Live"
            ).count()
            today_fulltime_disabled_jobs = today_full_time_jobs_count.filter(
                status="Disabled"
            ).count()

            today_admin_pending_jobs = today_admin_jobs_count.filter(
                status="Pending"
            ).count()
            today_admin_published_jobs = today_admin_jobs_count.filter(
                status="Published"
            ).count()
            today_admin_live_jobs = today_admin_jobs_count.filter(status="Live").count()
            today_admin_disabled_jobs = today_admin_jobs_count.filter(
                status="Disabled"
            ).count()

            today_admin_full_time_pending_jobs = (
                today_admin_full_time_jobs_count.filter(status="Pending").count()
            )
            today_admin_full_time_published_jobs = (
                today_admin_full_time_jobs_count.filter(status="Published").count()
            )
            today_admin_full_time_live_jobs = today_admin_full_time_jobs_count.filter(
                status="Live"
            ).count()
            today_admin_full_time_disabled_jobs = (
                today_admin_full_time_jobs_count.filter(status="Disabled").count()
            )

            total_skills = Skill.objects.filter()
            total_active_skills = total_skills.filter(status="Active").count()
            total_inactive_skills = total_skills.filter(status="InActive").count()

            total_locations = City.objects.filter()
            user_loc = User.objects.filter(user_type="JS").values_list(
                "current_city", flat=True
            )
            total_user_locations = City.objects.filter(id__in=user_loc)
            total_active_user_locations = total_user_locations.filter(
                status="Enabled"
            ).count()
            total_inactive_user_locations = total_user_locations.filter(
                status="Disabled"
            ).count()
            total_active_locations = total_locations.filter(status="Enabled").count()
            total_inactive_locations = total_locations.filter(status="Disabled").count()

            total_companies = Company.objects.filter(company_type="Company")
            total_active_companies = total_companies.filter(is_active=True).count()
            total_inactive_companies = total_companies.filter(is_active=False).count()
            total_companies = total_companies.count()

            total_recruiters = User.objects.filter(user_type="RR")
            total_agency_recruiters = User.objects.filter(user_type="AA")

            total_tickets_open = Ticket.objects.filter(status="Open").count()
            total_tickets_closed = Ticket.objects.filter(status="Closed").count()

            context = {
                "today_tickets_open": today_tickets_open,
                "today_tickets_closed": today_tickets_closed,
                "today_fulltime_pending_jobs": today_fulltime_pending_jobs,
                "today_fulltime_published_jobs": today_fulltime_published_jobs,
                "today_fulltime_live_jobs": today_fulltime_live_jobs,
                "today_fulltime_disabled_jobs": today_fulltime_disabled_jobs,
                "today_social_login_once_applicants": today_social_login_once_applicants,
                "today_job_applications": today_job_applications.count(),
                "total_job_applications": total_job_applications.count(),
                "today_social_resume_applicants": today_social_resume_applicants,
                "today_social_applied_applicants": today_social_applied_applicants,
                "today_social_profile_applicants": today_social_profile_applicants,
                "total_social_applicants": total_social_applicants.count(),
                "social_login_once_applicants": social_login_once_applicants,
                "social_resume_applicants": social_resume_applicants,
                "social_applied_applicants": social_applied_applicants,
                "social_profile_applicants": social_profile_applicants,
                "today_agency_recruiters_count": today_agency_recruiters.count(),
                "today_agency_active_recruiters_count": today_agency_recruiters.filter(
                    is_active=True
                ).count(),
                "today_agency_inactive_recruiters_count": today_agency_recruiters.filter(
                    is_active=False
                ).count(),
                "today_agency_mobile_verified_recruiters_count": today_agency_recruiters.filter(
                    mobile_verified=True
                ).count(),
                "today_agency_mobile_not_verified_recruiters_count": today_agency_recruiters.filter(
                    mobile_verified=False
                ).count(),
                "total_agency_recruiters_count": total_agency_recruiters.count(),
                "total_agency_active_recruiters_count": total_agency_recruiters.filter(
                    is_active=True
                ).count(),
                "total_agency_inactive_recruiters_count": total_agency_recruiters.filter(
                    is_active=False
                ).count(),
                "total_agency_mobile_verified_recruiters_count": total_agency_recruiters.filter(
                    mobile_verified=True
                ).count(),
                "total_agency_mobile_not_verified_recruiters_count": total_agency_recruiters.filter(
                    mobile_verified=False
                ).count(),
                "today_admin_full_time_pending_jobs": today_admin_full_time_pending_jobs,
                "today_admin_full_time_published_jobs": today_admin_full_time_published_jobs,
                "today_admin_full_time_live_jobs": today_admin_full_time_live_jobs,
                "today_admin_full_time_disabled_jobs": today_admin_full_time_disabled_jobs,
                "total_tickets_open": total_tickets_open,
                "total_tickets_closed": total_tickets_closed,
                "today_pending_jobs": today_pending_jobs,
                "today_published_jobs": today_published_jobs,
                "today_live_jobs": today_live_jobs,
                "today_disabled_jobs": today_disabled_jobs,
                "today_admin_pending_jobs": today_admin_pending_jobs,
                "today_admin_published_jobs": today_admin_published_jobs,
                "today_admin_live_jobs": today_admin_live_jobs,
                "today_admin_disabled_jobs": today_admin_disabled_jobs,
                "today_social_applicants": today_social_applicants.count(),
                "today_recruiters_count": today_recruiters.count(),
                "today_active_recruiters_count": today_recruiters.filter(
                    is_active=True
                ).count(),
                "today_inactive_recruiters_count": today_recruiters.filter(
                    is_active=False
                ).count(),
                "today_recruiters_mobile_verified_count": today_recruiters.filter(
                    mobile_verified=True
                ).count(),
                "today_recruiters_mobile_not_verified_count": today_recruiters.filter(
                    mobile_verified=False
                ).count(),
                "total_pending_jobs": total_pending_jobs,
                "total_published_jobs": total_published_jobs,
                "total_live_jobs": total_live_jobs,
                "total_disabled_jobs": total_disabled_jobs,
                "total_recruiters": total_recruiters.count(),
                "total_active_recruiters_count": total_recruiters.filter(
                    is_active=True
                ).count(),
                "total_inactive_recruiters_count": total_recruiters.filter(
                    is_active=False
                ).count(),
                "total_recruiters_mobile_verified_count": total_recruiters.filter(
                    mobile_verified=True
                ).count(),
                "total_recruiters_mobile_not_verified_count": total_recruiters.filter(
                    mobile_verified=False
                ).count(),
                "total_walkin_pending_jobs": total_walkin_pending_jobs,
                "total_walkin_published_jobs": total_walkin_published_jobs,
                "total_walkin_live_jobs": total_walkin_live_jobs,
                "total_walkin_disabled_jobs": total_walkin_disabled_jobs,
                "total_fulltime_pending_jobs": total_fulltime_pending_jobs,
                "total_fulltime_published_jobs": total_fulltime_published_jobs,
                "total_fulltime_live_jobs": total_fulltime_live_jobs,
                "total_fulltime_disabled_jobs": total_fulltime_disabled_jobs,
                "total_internship_pending_jobs": total_internship_pending_jobs,
                "total_internship_published_jobs": total_internship_published_jobs,
                "total_internship_live_jobs": total_internship_live_jobs,
                "total_internship_disabled_jobs": total_internship_disabled_jobs,
                "today_internship_pending_jobs": today_internship_pending_jobs,
                "today_internship_published_jobs": today_internship_published_jobs,
                "today_internship_live_jobs": today_internship_live_jobs,
                "today_internship_disabled_jobs": today_internship_disabled_jobs,
                "today_walkin_pending_jobs": today_walkin_pending_jobs,
                "today_walkin_published_jobs": today_walkin_published_jobs,
                "today_walkin_live_jobs": today_walkin_live_jobs,
                "today_walkin_disabled_jobs": today_walkin_disabled_jobs,
                "today_govt_pending_jobs": today_govt_pending_jobs,
                "today_govt_published_jobs": today_govt_published_jobs,
                "today_govt_live_jobs": today_govt_live_jobs,
                "today_govt_disabled_jobs": today_govt_disabled_jobs,
                "today_admin_internship_pending_jobs": today_admin_internship_pending_jobs,
                "today_admin_internship_published_jobs": today_admin_internship_published_jobs,
                "today_admin_internship_live_jobs": today_admin_internship_live_jobs,
                "today_admin_internship_disabled_jobs": today_admin_internship_disabled_jobs,
                "today_admin_walkin_pending_jobs": today_admin_walkin_pending_jobs,
                "today_admin_walkin_published_jobs": today_admin_walkin_published_jobs,
                "today_admin_walkin_live_jobs": today_admin_walkin_live_jobs,
                "today_admin_walkin_disabled_jobs": today_admin_walkin_disabled_jobs,
                "total_skills": total_skills.count(),
                "total_active_skills": total_active_skills,
                "total_inactive_skills": total_inactive_skills,
                "total_locations": total_locations.count(),
                "total_active_locations": total_active_locations,
                "total_inactive_locations": total_inactive_locations,
                "total_user_locations": total_user_locations.count(),
                "total_active_user_locations": total_active_user_locations,
                "total_inactive_user_locations": total_inactive_user_locations,
                "today_active_user_locations": today_user_locations.filter(
                    status="Enabled"
                ).count(),
                "today_inactive_user_locations": today_user_locations.filter(
                    status="Disabled"
                ).count(),
                "total_companies": total_companies,
                "total_active_companies": total_active_companies,
                "total_inactive_companies": total_inactive_companies,
                "total_govt_pending_jobs": total_govt_pending_jobs,
                "total_govt_published_jobs": total_govt_published_jobs,
                "total_govt_live_jobs": total_govt_live_jobs,
                "total_govt_disabled_jobs": total_govt_disabled_jobs,
                "today_active_skills": today_skills.filter(status="Active").count(),
                "today_inactive_skills": today_skills.filter(status="InActive").count(),
                "today_active_locations": today_locations.filter(
                    status="Enabled"
                ).count(),
                "today_inactive_locations": today_locations.filter(
                    status="Disabled"
                ).count(),
                "today_companies_active": today_companies_active,
                "today_companies_not_active": today_companies_not_active,
                "today_register_applicants": today_register_applicants.count(),
                "today_register_login_once_applicants": today_register_login_once_applicants,
                "today_register_resume_applicants": today_register_resume_applicants,
                "today_register_profile_applicants": today_register_profile_applicants,
                "today_register_applied_applicants": today_register_applied_applicants,
                "total_register_applicants": total_register_applicants.count(),
                "register_login_once_applicants": register_login_once_applicants,
                "register_resume_applicants": register_resume_applicants,
                "register_applied_applicants": register_applied_applicants,
                "register_profile_applicants": register_profile_applicants,
                "resume_applicants": resume_applicants.count(),
                "resume_login_once_applicants": resume_login_once_applicants,
                "resume_applied_applicants": resume_applied_applicants,
                "resume_profile_applicants": resume_profile_applicants,
                "today_resume_applicants": today_resume_applicants.count(),
                "today_resume_login_once_applicants": today_resume_login_once_applicants,
                "today_resume_applied_applicants": today_resume_applied_applicants,
                "today_resume_profile_applicants": today_resume_profile_applicants,
                "months": months,
            }
            return render(
                request,
                "dashboard/index.html",
                context,
            )
        else:
            return HttpResponseRedirect("/")
    else:
        return render(request, "dashboard/login.html")


@login_required
def change_password(request):
    if request.method == "POST":
        validate_changepassword = ChangePasswordForm(request.POST)
        if validate_changepassword.is_valid():
            user = request.user
            if not check_password(request.POST["oldpassword"], user.password):
                data = {
                    "error": True,
                    "response": {"oldpassword": "Invalid old password"},
                }
                return HttpResponse(json.dumps(data))
            if request.POST["newpassword"] != request.POST["retypepassword"]:
                data = {
                    "error": True,
                    "response": {
                        "newpassword": "New password and ConformPasswords did not match"
                    },
                }
                return HttpResponse(json.dumps(data))
            user.set_password(request.POST["newpassword"])
            user.save()
            data = {"error": False, "message": "Password changed successfully"}
        else:
            data = {"error": True, "response": validate_changepassword.errors}
        return HttpResponse(json.dumps(data))
    return render(request, "dashboard/change_password.html")


@permission_required("activity_view", "activity_edit")
def admin_user_list(request):
    users_list = User.objects.filter(is_staff=True)

    return render(request, "dashboard/users/list.html", {"users_list": users_list})


@permission_required("")
def new_admin_user(request):
    if request.method == "POST":
        if User.objects.filter(email=request.POST["email"]).exists():
            user = User.objects.get(email=request.POST["email"])
            validate_user = UserForm(request.POST, request.FILES, instance=user)
        else:
            validate_user = UserForm(request.POST, request.FILES)
        if validate_user.is_valid():
            user, created = User.objects.get_or_create(
                email=request.POST["email"],
            )
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            if created:
                UserEmail.objects.create(
                    user=user, email=request.POST["email"], is_primary=True
                )
                user.username = request.POST["email"]
                user.first_name = request.POST["first_name"]
                user.last_name = request.POST["last_name"]
                user.address = request.POST["address"]
                user.permanent_address = request.POST["permanent_address"]

            if request.POST["mobile"]:
                user.mobile = request.POST["mobile"]
            if "gender" in request.POST and request.POST["gender"]:
                user.gender = request.POST["gender"]
            if "profile_pic" in request.FILES:
                user.profile_pic = request.FILES["profile_pic"]
            user.save()
            for perm in request.POST.getlist("user_type"):
                permission = Permission.objects.get(id=perm)
                user.user_permissions.add(permission)
                user.save()
            data = {"error": False, "response": "New user created"}
        else:
            data = {"error": True, "response": validate_user.errors}
        return HttpResponse(json.dumps(data))
    contenttype = ContentType.objects.get(model="user")
    permissions = (
        Permission.objects.filter(content_type_id=contenttype)
        .exclude(codename__icontains="jobposts")
        .exclude(codename__icontains="blog")
        .order_by("id")[3:]
    )
    return render(
        request, "dashboard/users/new_user.html", {"permissions": permissions}
    )


@permission_required("")
def view_user(request, user_id):
    user = User.objects.filter(id=user_id)
    return render(request, "dashboard/users/view.html", {"user": user[0]})


@permission_required("")
def edit_user(request, user_id):
    user = User.objects.get(id=user_id)
    if not user:
        return render(request, "dashboard/404.html", status=404)
    if request.method == "POST":
        validate_user = UserForm(request.POST, request.FILES, instance=user)
        if validate_user.is_valid():
            user = validate_user.save(commit=False)
            user.is_active = True
            user.is_superuser = True
            if "profile_pic" in request.FILES:
                user.profile_pic = request.FILES["profile_pic"]
            user.user_type = request.POST.get("user_type")
            user.last_name = request.POST.get("last_name")
            user.save()
            user.user_permissions.clear()
            for perm in request.POST.getlist("user_type"):
                permission = Permission.objects.get(id=perm)
                user.user_permissions.add(permission)
            data = {"error": False, "response": "Blog category created"}
        else:
            data = {"error": True, "response": validate_user.errors}
        return HttpResponse(json.dumps(data))
    contenttype = ContentType.objects.get(model="user")
    permissions = (
        Permission.objects.filter(content_type_id=contenttype)
        .exclude(codename__icontains="jobposts")
        .order_by("id")[3:]
    )
    return render(
        request,
        "dashboard/users/edit_user.html",
        {"permissions": permissions, "user": user},
    )


@permission_required("")
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    if user:
        permissions = Permission.objects.filter(user=user)
        permission_list = [
            "activity_edit",
            "activity_view",
            "add_user",
            "change_user",
            "delete_user",
            "support_edit",
            "support_view",
        ]
        for permission in permissions:
            if permission.codename in permission_list:
                user.user_permissions.remove(permission)
        user.is_staff = False
        user.is_superuser = False
        user.save()
        # user.delete()
        data = {"error": False, "response": "User Deleted"}
    else:
        data = {"error": True, "response": "Unabe to delete user"}
    return HttpResponse(json.dumps(data))


@permission_required("activity_view", "activity_edit")
def country(request):
    if request.method == "GET":
        countries = Country.objects.all().order_by("name")
        states = State.objects.all().order_by("name")
        cities = City.objects.filter(status="Enabled", parent_city=None).order_by(
            "name"
        )
        return render(
            request,
            "dashboard/base_data/country.html",
            {"countries": countries, "states": states, "cities": cities},
        )
    if request.user.is_staff or request.user.has_perm("activity_edit"):
        if request.POST.get("mode") == "add_country":
            new_country = CountryForm(request.POST)
            if new_country.is_valid():
                country = new_country.save()
                country.slug = slugify(country.name)
                country.save()
                data = {"error": False, "message": "Country Added Successfully"}
            else:
                data = {"error": True, "message": new_country.errors["name"]}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "edit_country":
            country = Country.objects.get(id=request.POST.get("id"))
            new_country = CountryForm(request.POST, instance=country)
            if new_country.is_valid():
                new_country.save()
                data = {"error": False, "message": "Country Updated Successfully"}
            else:
                data = {"error": True, "message": new_country.errors}
            return HttpResponse(json.dumps(data))
        if request.POST.get("mode") == "remove_country":
            country = Country.objects.filter(id=request.POST.get("id"))
            if country:
                country[0].delete()
                data = {"error": False, "message": "Country Removed Successfully"}
            else:
                data = {"error": True, "message": "Country Not found"}
            return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "message": "Only Admin Can create/edit country"}
        return HttpResponse(json.dumps(data))

    if request.POST.get("mode") == "get_states":
        country = Country.objects.get(id=request.POST.get("c_id"))
        states = State.objects.filter(country=country).order_by("name")
        slist = ""
        for s in states:
            if s.status == "Enabled":
                slist = (
                    slist
                    + '<div class="ticket"><a class="name_ticket" id="'
                    + s.status
                    + ' " href="'
                    + str(s.id)
                    + '">'
                    + s.name
                    + "</a>("
                    + str(s.get_no_of_jobposts().count())
                    + ')<div class="remove_ticket remove_states"><a class="delete" href="'
                    + str(s.id)
                    + ' " countryId="'
                    + str(s.country.id)
                    + ' " id="'
                    + s.status
                    + ' "><i class="fa fa-trash-o"></i></a></div>'
                    + '<div class="actions_ticket"><a href="'
                    + str(s.id)
                    + '" countryId="'
                    + str(s.country.id)
                    + ' " id="'
                    + s.status
                    + ' "><i class="fa fa-toggle-off"></i></a>'
                )
            else:
                temp = "disabled_ticket"
                slist = (
                    slist
                    + '<div class="ticket '
                    + temp
                    + ' "><a class="name_ticket" id="'
                    + s.status
                    + ' " href="'
                    + str(s.id)
                    + '">'
                    + s.name
                    + "</a>("
                    + str(s.get_no_of_jobposts().count())
                    + ')<div class="remove_ticket remove_states"><a class="delete" href="'
                    + str(s.id)
                    + ' " countryId="'
                    + str(s.country.id)
                    + ' " id="'
                    + s.status
                    + ' "><i class="fa fa-trash-o"></i></a></div>'
                    + '<div class="actions_ticket"><a class="edit" href="'
                    + str(s.id)
                    + ' " countryId="'
                    + str(s.country.id)
                    + ' " id="'
                    + s.status
                    + ' "><i class="fa fa-toggle-on"></i></a>'
                )
            slist = slist + '</div><div class="clearfix"></div></div>'
        data = {"html": slist, "slug": country.slug}
        return HttpResponse(json.dumps(data))

    if request.user.is_staff or request.user.has_perm("activity_edit"):
        if request.POST.get("mode") == "add_state":
            new_state = StateForm(request.POST)
            if new_state.is_valid():
                s = new_state.save()
                s.slug = slugify(s.name)
                s.save()
                data = {
                    "error": False,
                    "message": "State Added Successfully",
                    "id": s.id,
                    "status": s.status,
                    "name": s.name,
                }
            else:
                data = {"error": True, "message": new_state.errors}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "edit_state":
            state = State.objects.get(id=request.POST.get("id"))
            new_state = StateForm(request.POST, instance=state)
            if new_state.is_valid():
                new_state.save()
                data = {"error": False, "message": "State Updated Successfully"}
            else:
                data = {"error": True, "message": new_state.errors}
            return HttpResponse(json.dumps(data))
        if request.POST.get("mode") == "remove_state":
            state = State.objects.filter(id=request.POST.get("id"))
            if state:
                state[0].delete()
                data = {"error": False, "message": "State Removed Successfully"}
            else:
                data = {"error": True, "message": "State Not found"}
            return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "message": "Only Admin Can create/edit country"}
        return HttpResponse(json.dumps(data))

    if request.POST.get("mode") == "get_cities":
        state = State.objects.filter(id=request.POST.get("s_id")).first()
        country = state.country.id
        cities = City.objects.filter(state=state).order_by("name")
        clist = ""
        for c in cities:
            if c.status == "Enabled":
                clist = (
                    clist
                    + '<div class="ticket"><a class="name_ticket" id="'
                    + c.status
                    + ' " href="'
                    + str(c.id)
                    + '">'
                    + c.name
                    + "</a>("
                    + str(c.get_no_of_jobposts().count())
                    + ')<div class="remove_ticket remove_city"><a class="delete" href="'
                    + str(c.id)
                    + ' " id="'
                    + c.status
                    + '"><i class="fa fa-trash-o"></i></a></div>'
                    + '<div class="actions_ticket"><a href="'
                    + str(c.id)
                    + ' " stateId="'
                    + str(c.state.id)
                    + ' " id="'
                    + c.status
                    + ' "><i class="fa fa-toggle-off"></i></a></div><a href="'
                    + reverse("job_locations", kwargs={"location": c.slug})
                    + '" target="_blank"><i class="fa fa-eye"></i></a><a class="add_other_city" title="Add Other City" id="'
                    + str(c.id)
                    + '" data-state="'
                    + str(c.state.id)
                    + '"><i class="fa fa-plus"></i></a>'
                )
            else:
                temp = "disabled_ticket"
                clist = (
                    clist
                    + '<div class="ticket '
                    + temp
                    + ' "><a class="name_ticket" id="'
                    + c.status
                    + ' " href="'
                    + str(c.id)
                    + '">'
                    + c.name
                    + "</a>("
                    + str(c.get_no_of_jobposts().count())
                    + ')<div class="remove_ticket remove_city"><a class="delete" href="'
                    + str(c.id)
                    + ' " id="'
                    + c.status
                    + '"><i class="fa fa-trash-o"></i></a></div>'
                    + '<div class="actions_ticket"><a class="edit" href="'
                    + str(c.id)
                    + ' " stateId="'
                    + str(c.state.id)
                    + ' " id="'
                    + c.status
                    + ' "><i class="fa fa-toggle-on"></i></a></div>'
                )
            clist = (
                clist
                + '<span class="meta_title meta_data">'
                + str(c.meta_title)
                + "</span>"
                + '<span class="meta_description meta_data">'
                + str(c.meta_description)
                + "</span>"
                + '<span class="internship_meta_title meta_data">'
                + str(c.internship_meta_title)
                + "</span>"
                + '<span class="internship_meta_description meta_data">'
                + str(c.internship_meta_description)
                + "</span>"
            )
            clist = clist + '</div><div class="clearfix"></div></div>'
        data = {"html": clist, "country": country, "state_slug": state.slug}
        return HttpResponse(json.dumps(data))
    if request.POST.get("mode") == "get_city_info":
        city = City.objects.filter(id=request.POST.get("city")).first()
        if city:
            data = {
                "city": city.id,
                "country": city.state.country.id,
                "state": city.state.id,
                "slug": city.slug,
                "parent": city.parent_city.id if city.parent_city else "",
            }
            return HttpResponse(json.dumps(data))

    if request.user.is_staff or request.user.has_perm("activity_edit"):
        if request.POST.get("mode") == "add_city":
            new_city = CityForm(request.POST)
            if new_city.is_valid():
                c = new_city.save()
                c.slug = slugify(c.name)
                c.save()
                data = {
                    "error": False,
                    "message": "City Added Successfully",
                    "id": c.id,
                    "status": c.status,
                    "name": c.name,
                }
            else:
                data = {"error": True, "message": new_city.errors["name"]}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "add_other_city":
            new_city = CityForm(request.POST)
            if new_city.is_valid():
                c = new_city.save()
                c.slug = slugify(c.name)
                if request.POST.get("parent_city"):
                    c.parent_city_id = request.POST.get("parent_city")
                c.save()
                data = {
                    "error": False,
                    "message": "City Added Successfully",
                    "id": c.id,
                    "status": c.status,
                    "name": c.name,
                }
            else:
                data = {"error": True, "message": new_city.errors["name"]}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "edit_city":
            city = City.objects.get(id=request.POST.get("id"))
            new_city = CityForm(request.POST, instance=city)
            if new_city.is_valid():
                new_city.save()
                if State.objects.filter(id=request.POST.get("state")):
                    city.state = State.objects.filter(id=request.POST.get("state"))[0]
                if request.POST.get("meta_title"):
                    city.meta_title = request.POST.get("meta_title")
                if request.POST.get("meta_description"):
                    city.meta_description = request.POST.get("meta_description")
                if request.POST.get("internship_meta_title"):
                    city.internship_meta_title = request.POST.get(
                        "internship_meta_title"
                    )
                if request.POST.get("internship_meta_description"):
                    city.internship_meta_description = request.POST.get(
                        "internship_meta_description"
                    )
                if request.POST.get("page_content"):
                    city.page_content = request.POST.get("page_content")
                if request.POST.get("parent_city"):
                    city.parent_city_id = request.POST.get("parent_city")
                city.save()
                data = {"error": False, "message": "City Updated Successfully"}
            else:
                data = {"error": True, "message": new_city.errors}
            return HttpResponse(json.dumps(data))
        if request.POST.get("mode") == "remove_city":
            city = City.objects.filter(id=request.POST.get("id"))
            if city:
                city[0].delete()
                data = {"error": False, "message": "City Removed Successfully"}
            else:
                data = {"error": True, "message": "City Not found"}
            return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "message": "Only Admin Can create/edit country"}
        return HttpResponse(json.dumps(data))

    if request.POST.get("mode") == "country_status":
        country = Country.objects.get(id=request.POST.get("id"))
        if request.user.is_staff == "Admin" or request.user.has_perm("activity_edit"):
            if country.status == "Enabled":
                country.status = "Disabled"
                country.save()
                states = State.objects.filter(country_id=country.id)
                if states:
                    State.objects.filter(country_id=country.id).update(
                        status="Disabled"
                    )
                    City.objects.filter(state_id__in=states).update(status="Disabled")

                data = {"error": False, "message": "Country Disabled Successfully"}
                return HttpResponse(json.dumps(data))
            else:
                country.status = "Enabled"
                country.save()
                states = State.objects.filter(country_id=country.id)
                if states:
                    State.objects.filter(country_id=country.id).update(status="Enabled")
                    City.objects.filter(state_id__in=states).update(status="Enabled")

                data = {"error": False, "message": "Country Enabled Successfully"}
                return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "message": "Only Admin Can edit country status"}
            return HttpResponse(json.dumps(data))

    if request.POST.get("mode") == "state_status":
        country_status = False
        state = State.objects.filter(id=request.POST.get("id")).prefetch_related(
            "country", "state"
        )
        state = state[0]
        if request.user.is_staff == "Admin" or request.user.has_perm("activity_edit"):
            if state.status == "Enabled":
                state.status = "Disabled"
                state.save()
                cities = state.state.all()
                if cities:
                    cities.update(status="Disabled")

                if not State.objects.filter(country=state.country, status="Enabled"):
                    if state.country.status != "Disabled":
                        state.country.status = "Disabled"
                        country_status = True
                        state.country.save()

                data = {
                    "error": False,
                    "message": "State Disabled Successfully",
                    "country_status": country_status,
                    "country_id": state.country.id,
                }
            else:
                state.status = "Enabled"
                state.save()
                state.country.status = "Enabled"
                state.country.save()
                cities = state.state.all()
                if cities:
                    cities.update(status="Enabled")

                data = {
                    "error": False,
                    "message": "State Enabled Successfully",
                    "country_status": country_status,
                    "country_id": state.country.id,
                }
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "message": "Only Admin Can create/edit country"}
            return HttpResponse(json.dumps(data))

    if request.POST.get("mode") == "city_status":
        state_status = False
        country_status = False
        city = (
            City.objects.filter(id=request.POST.get("id"))
            .prefetch_related("state")
            .first()
        )
        if not city:
            data = {"error": True, "message": "City Not Found"}
            return HttpResponse(json.dumps(data))
        if request.user.is_staff or request.user.has_perm("activity_edit"):
            if city.status == "Enabled":
                city.status = "Disabled"
                city.save()

                if not City.objects.filter(state=city.state, status="Enabled"):
                    if city.state.status != "Disabled":
                        city.state.status = "Disabled"
                        state_status = True
                        city.state.save()

                    if not State.objects.filter(
                        country=city.state.country, status="Enabled"
                    ):
                        if city.state.country.status != "Disabled":
                            city.state.country.status = "Disabled"
                            country_status = True
                            city.state.country.save()

                data = {
                    "error": False,
                    "message": "City Disabled Successfully",
                    "state_status": state_status,
                    "country_status": country_status,
                    "state_id": city.state.id,
                    "country_id": city.state.country.id,
                }
                return HttpResponse(json.dumps(data))
            else:
                city.status = "Enabled"
                city.save()
                city.state.status = "Enabled"
                city.state.save()
                if city.state.country.status == "Disabled":
                    city.state.country.status = "Enabled"
                    city.state.country.save()
                data = {
                    "error": False,
                    "message": "City Enabled Successfully",
                    "state_status": state_status,
                    "country_status": country_status,
                    "state_id": city.state.id,
                    "country_id": city.state.country.id,
                }
                return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "message": "Only Admin Can create/edit country"}
            return HttpResponse(json.dumps(data))


def edit_tech_skills(skill, request):
    if request.FILES.get("icon"):
        if skill.icon:
            url = str(skill.icon).split("cdn.peeljobs.com")[-1:]
            AWS().cloudfront_invalidate(paths=url)
        file_path = get_aws_file_path(
            request.FILES.get("icon"),
            "technology/icons/",
            slugify(request.POST.get("name")),
        )
        skill.icon = file_path
    skill.name = request.POST.get("name")
    if request.POST.get("slug"):
        skill.slug = request.POST.get("slug")
    if request.POST.get("skill_type"):
        skill.skill_type = request.POST.get("skill_type")
    if request.POST.get("page_content"):
        skill.page_content = request.POST.get("page_content")
    if request.POST.get("meta"):
        skill.meta = json.loads(request.POST.get("meta"))
    skill.save()


@permission_required("activity_view", "activity_edit")
def tech_skills(request):
    if request.method == "GET":
        skills = Skill.objects.all().order_by("name")

        if request.GET.get("search"):
            skills = Skill.objects.filter(name__icontains=request.GET.get("search"))
        status = request.GET.get("status")
        if status:
            if status == "active":
                skills = skills.filter(status="Active")
            elif status == "inactive":
                skills = skills.filter(status="InActive")
            else:
                skills = skills.filter(skill_type=status)

        items_per_page = 20
        no_pages = int(math.ceil(float(skills.count()) / items_per_page))

        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                return HttpResponseRedirect(reverse("dashboard:tech_skills"))
            else:
                page = int(request.GET.get("page"))
        else:
            page = 1

        skills = skills[(page - 1) * items_per_page : page * items_per_page]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        return render(
            request,
            "dashboard/base_data/technical_skills.html",
            {
                "search": request.GET.get("search"),
                "status": status,
                "skills": skills,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
                "skill_types": SKILL_TYPE,
            },
        )
    else:
        if request.user.is_staff == "Admin" or request.user.has_perm("activity_edit"):
            if request.POST.get("mode") == "add_skill":
                new_skill = SkillForm(request.POST, request.FILES)
                if new_skill.is_valid():
                    new_skill = new_skill.save(commit=False)
                    if request.FILES and request.FILES.get("icon"):
                        file_path = get_aws_file_path(
                            request.FILES.get("icon"),
                            "technology/icons/",
                            slugify(request.POST.get("name")),
                        )
                        new_skill.icon = file_path
                    new_skill.status = "InActive"
                    new_skill.skill_type = request.POST.get("skill_type")
                    new_skill.save()
                    data = {"error": False, "message": "Skill Added Successfully"}
                else:
                    data = {"error": True, "message": new_skill.errors}
                return HttpResponse(json.dumps(data))
            if request.POST.get("mode") == "edit_skill":
                skill = Skill.objects.filter(id=request.POST.get("id")).first()
                if skill:
                    new_skill = SkillForm(request.POST, request.FILES, instance=skill)
                    try:
                        if request.POST.get("meta"):
                            json.loads(request.POST.get("meta"))
                        valid = True
                    except BaseException as e:
                        new_skill.errors["meta"] = "Enter Valid Json Format - " + str(e)
                        valid = False
                    if new_skill.is_valid() and valid:
                        edit_tech_skills(skill, request)
                        data = {"error": False, "message": "Skill Updated Successfully"}
                        return HttpResponse(json.dumps(data))
                    else:
                        data = {"error": True, "response": new_skill.errors}
                    return HttpResponse(json.dumps(data))
                else:
                    data = {
                        "error": True,
                        "message": "Skill Not Found",
                        "page": request.POST.get("page")
                        if request.POST.get("page")
                        else 1,
                    }
                    return HttpResponse(json.dumps(data))
        else:
            data = {
                "error": True,
                "message": "Only Admin can add/edit Technical Skill",
                "page": request.POST.get("page") if request.POST.get("page") else 1,
            }
            return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def delete_skill(request, skill_id):
    skill = Skill.objects.filter(id=skill_id)
    if skill:
        skill.delete()
        data = {
            "error": False,
            "message": "Skill Removed Successfully",
            "path": request.path,
        }
    else:
        data = {"error": True, "message": "Skill Not Found", "path": request.path}
    return HttpResponse(json.dumps(data))


@permission_required("activity_view", "activity_edit")
def languages(request):
    if request.method == "GET":
        languages = Language.objects.all().order_by("name")
        if request.GET.get("search"):
            languages = languages.filter(name__icontains=request.GET.get("search"))
        items_per_page = 10
        no_pages = int(math.ceil(float(languages.count()) / items_per_page))

        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                return HttpResponseRedirect(reverse("dashboard:languages"))
            else:
                page = int(request.GET.get("page"))
        else:
            page = 1

        languages = languages[(page - 1) * items_per_page : page * items_per_page]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        search_value = request.GET.get("search") if request.GET.get("search") else None
        return render(
            request,
            "dashboard/base_data/languages.html",
            {
                "search_value": search_value,
                "languages": languages,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
            },
        )

    if request.user.user_type == "Admin" or request.user.has_perm("activity_edit"):

        if request.POST.get("mode") == "add_language":
            new_language = LanguageForm(request.POST)
            if new_language.is_valid():
                new_language.save()
                data = {"error": False, "message": "Language Added Successfully"}
            else:
                data = {"error": True, "message": new_language.errors["name"]}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "edit_language":
            language = Language.objects.get(id=request.POST.get("id"))
            new_language = LanguageForm(request.POST, instance=language)
            if new_language.is_valid():
                new_language.save()
                data = {
                    "error": False,
                    "message": "Language Updated Successfully",
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            else:
                data = {
                    "error": True,
                    "message": new_language.errors["name"],
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            return HttpResponse(json.dumps(data))
    else:
        data = {
            "error": True,
            "message": "Only Admin can add/edit Qualification",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
        return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def delete_language(request, language_id):
    Language.objects.get(id=language_id).delete()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@permission_required("activity_view", "activity_edit")
def qualifications(request):
    if request.method == "GET":
        qualifications = Qualification.objects.all().order_by("name")
        if request.GET.get("search"):
            qualifications = qualifications.filter(
                name__icontains=request.GET.get("search")
            )
        if request.GET.get("status") == "Active":
            qualifications = qualifications.filter(status="Active")
        elif request.GET.get("status") == "InActive":
            qualifications = qualifications.filter(status="InActive")

        items_per_page = 10
        no_pages = int(math.ceil(float(qualifications.count()) / items_per_page))

        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                return HttpResponseRedirect(reverse("dashboard:qualifications"))
            page = int(request.GET.get("page"))
        else:
            page = 1

        qualifications = qualifications[
            (page - 1) * items_per_page : page * items_per_page
        ]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        status = request.GET.get("status") if request.GET.get("status") else None
        search = request.GET.get("search") if request.GET.get("search") else None
        return render(
            request,
            "dashboard/base_data/qualifications.html",
            {
                "status": status,
                "qualifications": qualifications,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
                "search": search,
            },
        )
    if request.user.is_staff or request.user.has_perm("activity_edit"):
        if request.POST.get("mode") == "add_qualification":
            new_qualification = QualificationForm(request.POST)
            if new_qualification.is_valid():
                new_qualification.save()
                data = {"error": False, "message": "Qualification Added Successfully"}
            else:
                data = {"error": True, "message": new_qualification.errors["name"]}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "edit_qualification":
            qualification = Qualification.objects.get(id=request.POST.get("id"))
            new_qualification = QualificationForm(request.POST, instance=qualification)
            if new_qualification.is_valid():
                new_qualification.save()
                data = {
                    "error": False,
                    "message": "Qualification Updated Successfully",
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            else:
                data = {
                    "error": True,
                    "message": new_qualification.errors["name"],
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            return HttpResponse(json.dumps(data))
    else:
        data = {
            "error": True,
            "message": "Only Admin can add/edit Qualification",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
        return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def delete_qualification(request, qualification_id):
    Qualification.objects.get(id=qualification_id).delete()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@permission_required("activity_view", "activity_edit")
def industries(request):
    if request.method == "GET":
        industries = Industry.objects.all().order_by("name")
        if request.GET.get("search"):
            industries = industries.filter(name__icontains=request.GET.get("search"))
        if request.GET.get("status") == "active":
            industries = industries.filter(status="Active")
        elif request.GET.get("status") == "inctive":
            industries = industries.filter(status="InActive")

        items_per_page = 10
        no_pages = int(math.ceil(float(industries.count()) / items_per_page))

        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                return HttpResponseRedirect(reverse("dashboard:industries"))
            page = int(request.GET.get("page"))
        else:
            page = 1

        industries = industries[(page - 1) * items_per_page : page * items_per_page]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        status = request.GET.get("status") if request.GET.get("status") else None
        search = request.GET.get("search") if request.GET.get("search") else None
        return render(
            request,
            "dashboard/base_data/industry.html",
            {
                "status": status,
                "search": search,
                "industries": industries,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
            },
        )

    if request.user.is_staff or request.user.has_perm("activity_edit"):
        if request.POST.get("mode") == "add_industry":
            new_industry = IndustryForm(request.POST)
            if new_industry.is_valid():
                new_industry.save()
                data = {"error": False, "message": "Industry Added Successfully"}
            else:
                data = {"error": True, "message": new_industry.errors["name"]}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "edit_industry":
            industry = Industry.objects.get(id=request.POST.get("id"))
            new_industry = IndustryForm(request.POST, instance=industry)
            if new_industry.is_valid():
                new_industry.save()
                if request.POST.get("meta_title"):
                    industry.meta_title = request.POST.get("meta_title")
                if request.POST.get("meta_description"):
                    industry.meta_description = request.POST.get("meta_description")
                if request.POST.get("page_content"):
                    industry.page_content = request.POST.get("page_content")
                industry.save()
                data = {
                    "error": False,
                    "message": "Industry Updated Successfully",
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            else:
                data = {
                    "error": True,
                    "message": new_industry.errors,
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            return HttpResponse(json.dumps(data))
    else:
        data = {
            "error": True,
            "message": "Only Admin can add/edit Industry",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
        return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def delete_industry(request, industry_id):
    Industry.objects.get(id=industry_id).delete()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@permission_required("activity_view", "activity_edit")
def functional_area(request):
    if request.method == "GET":
        functional_areas = FunctionalArea.objects.all().order_by("name")
        if request.GET.get("search"):
            functional_areas = functional_areas.filter(
                name__icontains=request.GET.get("search")
            )
        if request.GET.get("status") == "active":
            functional_areas = functional_areas.filter(status="Active")
        elif request.GET.get("status") == "inactive":
            functional_areas = functional_areas.filter(status="InActive")

        items_per_page = 10
        no_pages = int(math.ceil(float(functional_areas.count()) / items_per_page))

        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                return HttpResponseRedirect(reverse("dashboard:functional_areas"))
            page = int(request.GET.get("page"))
        else:
            page = 1

        functional_areas = functional_areas[
            (page - 1) * items_per_page : page * items_per_page
        ]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        status = request.GET.get("status") if request.GET.get("status") else None
        search = request.GET.get("search") if request.GET.get("search") else None
        return render(
            request,
            "dashboard/base_data/functional_area.html",
            {
                "status": status,
                "search": search,
                "functional_areas": functional_areas,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
            },
        )

    if request.user.is_staff or request.user.has_perm("activity_edit"):
        if request.POST.get("mode") == "add_functional_area":
            new_functional_area = FunctionalAreaForm(request.POST)
            if new_functional_area.is_valid():
                new_functional_area.save()
                data = {"error": False, "message": "Functional Area Added Successfully"}
            else:
                data = {"error": True, "message": new_functional_area.errors["name"]}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "edit_functional_area":
            functional_area = FunctionalArea.objects.get(id=request.POST.get("id"))
            new_functional_area = FunctionalAreaForm(
                request.POST, instance=functional_area
            )
            if new_functional_area.is_valid():
                new_functional_area.save()
                data = {
                    "error": False,
                    "message": "Industry Updated Successfully",
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            else:
                data = {
                    "error": True,
                    "message": new_functional_area.errors["name"],
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            return HttpResponse(json.dumps(data))
    data = {
        "error": True,
        "message": "Only Admin can add/edit FunctionalArea",
        "page": request.POST.get("page") if request.POST.get("page") else 1,
    }
    return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def delete_functional_area(request, functional_area_id):
    FunctionalArea.objects.get(id=functional_area_id).delete()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


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
def deactivate_job(request, job_post_id):

    job_post = get_object_or_404(JobPost, id=job_post_id)
    # need to delete job post on fb, twitter and linkedin
    posts = FacebookPost.objects.filter(job_post=job_post).exclude(
        post_status="Deleted"
    )
    for each in posts:
        del_jobpost_peel_fb(request.user, each)
        del_jobpost_fb(job_post.user, each)
    posts = TwitterPost.objects.filter(job_post=job_post)

    job_post.previous_status = job_post.status
    job_post.status = "Disabled"
    job_post.save()

    data = {
        "error": False,
        "response": "Job Post deactivated",
        "job_type": job_post.job_type,
    }
    # return HttpResponse(json.dumps(data))
    return HttpResponseRedirect(
        reverse("dashboard:job_posts", args=(job_post.job_type,))
    )


@permission_required("activity_edit")
def delete_job(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    job_type = job_post.job_type
    posts = FacebookPost.objects.filter(job_post=job_post).exclude(
        post_status="Deleted"
    )
    for each in posts:
        del_jobpost_fb(job_post.user, each)
    posts = TwitterPost.objects.filter(job_post=job_post)
    for each in posts:
        del_jobpost_tw(job_post.user, each)

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
        # postonpeel_fb.delay(job_post.user, job_post)
        # if job_post.post_on_fb:
        #     fbpost.delay(job_post.user, job_post)
        #     postonpage.delay(job_post.user, job_post)
        #     # need to check this condition
        #     # if emp['peelfbpost']:
        # posts = FacebookPost.objects.filter(job_post=job_post, page_or_group='group', is_active=True, post_status='Deleted')
        # for group in job_post.fb_groups:
        #     fb_group = FacebookGroup.objects.get(user=job_post.user, group_id=group)
        #     is_active = True
        #     postongroup.delay(job_post.user, job_post, fb_group, is_active)
        #     # need to get accetoken for peeljobs twitter page
        # if job_post.post_on_tw:
        #     postontwitter.delay(job_post.user, job_post, 'Profile'))
    # else:
    #     job_post.status = "Published"

    else:
        job_post.status = "Pending"
        job_post.save()
        # postonpeel_fb.delay(job_post.user, job_post)
        # if job_post.post_on_fb:
        #     fbpost.delay(job_post.user, job_post)
        #     postonpage.delay(job_post.user, job_post)
        #     # need to check this condition
        #     # if emp['peelfbpost']:
        # posts = FacebookPost.objects.filter(job_post=job_post, page_or_group='group', is_active=True, post_status='Deleted')
        # for group in job_post.fb_groups:
        #     fb_group = FacebookGroup.objects.get(user=job_post.user, group_id=group)
        #     is_active = True
        #     postongroup.delay(job_post.user, job_post, fb_group, is_active)
        #     # need to get accetoken for peeljobs twitter page
        # if job_post.post_on_tw:
        #     postontwitter.delay(job_post.user, job_post, 'Profile'))
    # else:
    #     job_post.status = "Published"
    posts = FacebookPost.objects.filter(job_post=job_post)
    for each in posts:
        del_jobpost_fb(job_post.user, each)
    posts = TwitterPost.objects.filter(job_post=job_post)
    for each in posts:
        del_jobpost_tw(job_post.user, each)

    job_post.save()
    job_type = job_post.job_type
    data = {
        "error": False,
        "response": "Job Post Published Successfully",
        "job_type": job_type,
        "status": job_post.status,
    }
    # return HttpResponse(json.dumps(data))
    return HttpResponseRedirect(
        reverse("dashboard:job_posts", args=(job_post.job_type,))
    )


@permission_required("activity_edit")
def enable_job(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)
    job_post.status = job_post.previous_status
    job_post.save()
    if job_post.post_on_fb:
        fbpost.delay(job_post.user.id, job_post_id)
        postonpage.delay(job_post.user.id, job_post_id)
        postonpeel_fb(job_post)
    posts = FacebookPost.objects.filter(
        job_post=job_post, page_or_group="group", is_active=True, post_status="Deleted"
    )
    for group in posts:
        fb_group = FacebookGroup.objects.get(
            user=job_post.user, group_id=group.page_or_group_id
        )
        postongroup.delay(job_post.id, fb_group.id)
    if job_post.post_on_tw:
        postontwitter.delay(job_post.user.id, job_post_id, "Profile")

    data = {"error": False, "response": "Job Post enabled Successfully"}
    # return HttpResponse(json.dumps(data))
    return HttpResponseRedirect(
        reverse("dashboard:job_posts", args=(job_post.job_type,))
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


@permission_required("activity_edit")
def skill_status(request, skill_id):
    skill = Skill.objects.filter(id=skill_id).first()
    if skill:
        skill.status = "InActive" if skill.status == "Active" else "Active"
        skill.save()
        data = {"error": False, "response": "Skill Status Changed Successfully"}
    else:
        data = {"error": True, "response": "skill not exists"}
    return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def functional_area_status(request, functional_area_id):
    functional_area = FunctionalArea.objects.filter(id=functional_area_id)
    if functional_area:
        functional_area.status = (
            "InActive" if functional_area.status == "Active" else "Active"
        )
        functional_area.save()
        data = {
            "error": False,
            "response": "Functional Area Status Changed Successfully",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
    else:
        data = {
            "error": True,
            "response": "Functional Area not exists",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
    return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def industry_status(request, industry_id):
    industry = Industry.objects.filter(id=industry_id).first()
    if industry:
        industry.status = "InActive" if industry.status == "Active" else "Active"
        industry.save()
        data = {
            "error": False,
            "response": "Industry Status Changed Successfully",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
    else:
        data = {
            "error": True,
            "response": "Industry not exists",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
    return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def qualification_status(request, qualification_id):
    qualification = Qualification.objects.filter(id=qualification_id).first()
    if qualification:
        qualification.status = (
            "InActive" if qualification.status == "Active" else "Active"
        )
        qualification.save()
        data = {
            "error": False,
            "response": "Qualification Status Changed Successfully",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
    else:
        data = {
            "error": True,
            "response": "Qualification not exists",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
    return HttpResponse(json.dumps(data))


POST = (
    ("Shortlisted", "Shortlisted"),
    ("Selected", "Selected"),
    ("Rejected", "Rejected"),
    ("Process", "Process"),
)


@permission_required("activity_edit")
def new_template(request):
    if request.method == "POST":
        validate_mailtemplate = MailTemplateForm(request.POST)
        if validate_mailtemplate.is_valid():
            mail_template = MailTemplate.objects.create(
                title=request.POST.get("title"),
                subject=request.POST.get("subject"),
                message=request.POST.get("message"),
                created_on=datetime.utcnow(),
                modified_on=datetime.utcnow(),
                created_by=request.user,
            )
            if str(request.POST.get("show_recruiter")) == "True":
                mail_template.show_recruiter = True
                mail_template.applicant_status = request.POST.get("applicant_status")
                mail_template.save()
            data = {
                "error": False,
                "message": "Successfully saved new template, now you can see it, edit it, send to your contacts.!",
            }
        else:
            data = {"error": True, "message": validate_mailtemplate.errors}
        return HttpResponse(json.dumps(data))
    else:
        return render(
            request, "dashboard/mail/new_mailtemplate.html", {"applicant_status": POST}
        )


@permission_required("activity_edit")
def edit_template(request, template_id):
    mailtemplates = MailTemplate.objects.filter(id=template_id)
    if mailtemplates:
        mailtemplate = mailtemplates[0]
        if request.method == "POST":
            validate_mailtemplate = MailTemplateForm(
                request.POST, instance=mailtemplate
            )
            if validate_mailtemplate.is_valid():
                mailtemplate = validate_mailtemplate.save(commit=False)
                mailtemplate.modified_on = datetime.utcnow()
                if (
                    "show_recruiter" in request.POST.keys()
                    and str(request.POST.get("show_recruiter")) == "True"
                ):
                    mailtemplate.show_recruiter = True
                    mailtemplate.applicant_status = request.POST.get("applicant_status")
                else:
                    mailtemplate.show_recruiter = False
                mailtemplate.save()

                mailtemplate.save()
                data = {
                    "error": False,
                    "message": "Successfully saved template, now you can see it, edit it, send to recruiters!",
                }
            else:
                data = {"error": True, "message": validate_mailtemplate.errors}
            return HttpResponse(json.dumps(data))
        return render(
            request,
            "dashboard/mail/edit_mailtemplate.html",
            {"email_template": mailtemplate, "applicant_status": POST},
        )
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "dashboard/404.html",
        {
            "message_type": "404",
            "message": "Sorry, the page you requested can not be found",
            "reason": reason,
        },
        status=404,
    )


@permission_required("activity_view", "activity_edit")
def emailtemplates(request):
    mailtemplates = MailTemplate.objects.filter()
    return render(request, "dashboard/mail/list.html", {"mailtemplates": mailtemplates})


@permission_required("activity_view", "activity_edit")
def view_template(request, template_id):
    mailtemplate = MailTemplate.objects.filter(id=template_id).first()
    if mailtemplate:
        return render(
            request, "dashboard/mail/view.html", {"mail_template": mailtemplate}
        )
    return render(request, "dashboard/404.html", status=404)


@permission_required("activity_edit")
def delete_template(request, template_id):
    mailtemplates = MailTemplate.objects.filter(id=template_id)
    if mailtemplates:
        mailtemplates.delete()
        data = {"error": False, "response": "Job Post deleted Successfully"}
        return HttpResponse(json.dumps(data))
    return render(request, "dashboard/404.html", status=404)


@permission_required("activity_edit")
def send_mail(request, template_id):
    mailtemplate = MailTemplate.objects.filter(id=template_id).first()
    if mailtemplate:
        if request.method == "POST":
            validate_mailtemplate = MailTemplateForm(
                request.POST, instance=mailtemplate
            )
            if validate_mailtemplate.is_valid():
                emailtemplate = mailtemplate
                t = loader.get_template("email/email_template.html")
                c = {"text": emailtemplate.message}
                subject = emailtemplate.subject
                rendered = t.render(c)
                mto = []
                for recruiter in request.POST.getlist("recruiters"):
                    recruiter = User.objects.get(id=recruiter)
                    mto.append(recruiter.email)
                sent_mail = SentMail.objects.create(template=emailtemplate)

                for recruiter in request.POST.getlist("recruiters"):
                    recruiter = User.objects.get(id=recruiter)
                    sent_mail.recruiter.add(recruiter)
                send_email.delay(mto, subject, rendered)
                sending_mail.delay(mailtemplate, request.POST.getlist("recruiters"))
                return HttpResponse(
                    json.dumps({"error": False, "response": "Email Sent Successfully"})
                )
            return HttpResponse(
                json.dumps({"error": True, "response": validate_mailtemplate.errors})
            )
        recruiters = User.objects.filter(user_type="RR")
        return render(
            request,
            "dashboard/mail/send_mail.html",
            {"recruiters": recruiters, "mailtemplate": mailtemplate},
        )
    return render(request, "dashboard/404.html", status=404)


@permission_required("activity_view", "activity_edit")
def sent_mails(request):
    sent_mails = SentMail.objects.filter()
    return render(
        request, "dashboard/mail/sent_mail_list.html", {"sent_mails": sent_mails}
    )


@permission_required("activity_view", "activity_edit")
def view_sent_mail(request, sent_mail_id):
    sent_mails = SentMail.objects.filter(id=sent_mail_id)
    if sent_mails:
        sent_mail = sent_mails[0]
        return render(
            request, "dashboard/mail/view_sent_mail.html", {"sent_mail": sent_mail}
        )
    return render(request, "dashboard/404.html", status=404)


@permission_required("activity_edit")
def delete_sent_mail(request, sent_mail_id):
    sent_mails = SentMail.objects.filter(id=sent_mail_id)
    if sent_mails:
        sent_mail = sent_mails[0]
        sent_mail.delete()
        data = {"error": False, "response": "Sent Mail Deleted Successfully"}
        return HttpResponse(json.dumps(data))
    return render(request, "dashboard/404.html", status=404)


@permission_required("activity_view", "activity_edit")
def search_log(request):
    search_logs = SearchResult.objects.all().order_by("-search_on")
    items_per_page = 500
    no_pages = int(math.ceil(float(len(search_logs)) / items_per_page))

    if (
        "page" in request.GET
        and bool(re.search(r"[0-9]", request.GET.get("page")))
        and int(request.GET.get("page")) > 0
    ):
        if int(request.GET.get("page")) > (no_pages + 2):
            return HttpResponseRedirect(reverse("dashboard:search_log"))
        page = int(request.GET.get("page"))
    else:
        page = 1

    search_logs = search_logs[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    return render(
        request,
        "dashboard/search/list.html",
        {
            "search_logs": search_logs,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
        },
    )


@permission_required("activity_view", "activity_edit")
def view_search_log(request, search_log_id):
    search_logs = SearchResult.objects.filter(id=search_log_id)
    if search_logs:
        search_log = search_logs[0]
        return render(request, "dashboard/search/view.html", {"search_log": search_log})
    return render(request, "dashboard/404.html", status=404)


@permission_required("activity_view", "activity_edit")
def subscribers(request):
    subscribers = Subscriber.objects.values_list("skill_id", flat=True).distinct()
    skills = []
    for each in subscribers:
        skill = Skill.objects.get(id=each)
        skills.append(skill)
    return render(request, "dashboard/subscribers/list.html", {"skills": skills})


@permission_required("activity_view", "activity_edit")
def view_subscribers(request, skill_id):
    subscribers = Subscriber.objects.filter(skill_id=skill_id)
    return render(
        request, "dashboard/subscribers/view.html", {"subscribers": subscribers}
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
        if "final_industry" in request.POST.keys():
            add_other_industry(
                validate_post, json.loads(request.POST["final_industry"]), request.user
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
            fb_groups = FacebookPost.objects.filter(
                job_post=job_post, page_or_group="group", post_status="Posted"
            ).order_by("-id")
            companies = Company.objects.filter(
                company_type="Company", is_active=True
            ).order_by("name")
            return render(
                request,
                "dashboard/jobpost/edit.html",
                {
                    "fb_groups": fb_groups,
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
        if "final_industry" in request.POST.keys():
            add_other_industry(
                post, json.loads(request.POST["final_industry"]), request.user
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


@permission_required("activity_edit", "activity_view")
def companies(request, company_type):
    status = ""
    if company_type == "company":
        companies = Company.objects.filter(company_type__iexact=company_type).distinct()
        if request.GET.get("active") == "false":
            status = "fasle"
            companies = companies.filter(is_active=False)
        else:
            status = "true"
            companies = companies.filter(is_active=True)
    else:
        companies = Company.objects.filter(company_type__iexact=company_type).distinct()
        if "admin" in request.GET:
            if request.GET.get("admin") == "false":
                status = "admin_inactive"
                companies = companies.filter(
                    id__in=User.objects.filter(
                        is_admin=True, is_active=False
                    ).values_list("company", flat=True)
                )
            elif request.GET.get("admin") == "true":
                status = "admin_active"
                companies = companies.filter(
                    id__in=User.objects.filter(
                        is_admin=True, is_active=True
                    ).values_list("company", flat=True)
                )
        if "active" in request.GET:
            if request.GET.get("active") == "false":
                status = "inactive"
                companies = companies.filter(is_active=False)
            elif request.GET.get("active") == "true":
                status = "active"
                companies = companies.filter(is_active=True)

    if request.GET.get("search", ""):
        user_ids = User.objects.filter(
            email__icontains=request.GET.get("search")
        ).values_list("company", flat=True)
        companies = companies.filter(
            Q(id__in=user_ids)
            | Q(name__icontains=request.GET.get("search"))
            | Q(website=request.GET.get("search"))
        )

    items_per_page = 50
    no_pages = int(math.ceil(float(companies.count()) / items_per_page))
    companies = companies.order_by("-registered_date")
    page = request.POST.get("page") or request.GET.get("page")
    if page and bool(re.search(r"[0-9]", page)) and int(page) > 0:
        if int(page) > (no_pages + 2):
            return HttpResponseRedirect(reverse("dashboard:applicants"))
        page = int(page)
    else:
        page = 1
    companies = companies[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    return render(
        request,
        "dashboard/company/list.html",
        {
            "companies": companies,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "page": page,
            "last_page": no_pages,
            "company_type": company_type,
            "status": status,
            "search_value": request.GET.get("search")
            if request.GET.get("search")
            else "",
            "active": request.GET.get("active") if request.GET.get("active") else "",
            "admin": request.GET.get("admin") if request.GET.get("admin") else "",
        },
    )


@permission_required("activity_edit")
def enable_company(request, company_id):
    page_value = request.POST.get("page")
    search_value = request.POST.get("search")
    admin = request.POST.get("admin")
    company = get_object_or_404(Company, id=company_id)
    url = reverse("dashboard:companies", kwargs={"company_type": company.company_type})
    if company.is_active:
        company.is_active = False
        is_active = "true"
        if str(admin) == "true":
            is_active = ""
        url = url + "?active=true&page=" + str(page_value) + "&search=" + search_value
        data = {
            "error": False,
            "response": "Company Deactivated Successfully",
            "is_active": is_active,
            "url": url,
        }
    else:
        url = url + "?active=false&page=" + str(page_value) + "&search=" + search_value
        company.is_active = True
        is_active = "false"
        if str(admin) == "true":
            is_active = ""

        data = {
            "error": False,
            "response": "Company Activated Successfully",
            "is_active": is_active,
            "url": url,
        }
    company.save()
    if company.is_active:
        data["active"] = "false"
    else:
        data["active"] = "true"
    return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def delete_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company_users = User.objects.filter(company=company)
    company_users.delete()

    page_value = request.POST.get("page")
    search_value = request.POST.get("search")
    admin = request.POST.get("admin")
    url = reverse("dashboard:companies", kwargs={"company_type": company.company_type})
    if company.is_active:
        company.is_active = False
        is_active = "true"
        if str(admin) == "true":
            is_active = ""
        url = url + "?active=true&page=" + str(page_value) + "&search=" + search_value
        data = {
            "error": False,
            "response": "Company Deactivated Successfully",
            "is_active": is_active,
            "url": url,
        }
    else:
        url = url + "?active=false&page=" + str(page_value) + "&search=" + search_value
        company.is_active = True
        is_active = "false"
        if str(admin) == "true":
            is_active = ""

    company.delete()
    data = {
        "error": False,
        "response": "Company Deleted Successfully",
        "url": url,
        "is_active": is_active,
    }
    return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def enable_paid_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company_admin = get_object_or_404(User, company=company, is_admin=True)
    if company_admin.is_paid:
        company_admin.is_paid = False
    else:
        company_admin.is_paid = True
    company_admin.save()
    return HttpResponseRedirect(
        reverse("dashboard:companies", kwargs={"company_type": company.company_type})
    )


@permission_required("activity_edit", "activity_view")
def view_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    return render(request, "dashboard/company/view.html", {"company": company})


@permission_required("activity_edit", "activity_view")
def company_recruiters(request, company_id, status):
    company = get_object_or_404(Company, id=company_id)
    recruiters = company.get_company_recruiters()
    if str(status) == "active":
        recruiters = recruiters.filter(is_active=True)
    else:
        recruiters = recruiters.filter(is_active=False)
    items_per_page = 100
    no_pages = int(math.ceil(float(recruiters.count()) / items_per_page))
    page = request.GET.get("page")
    if page and bool(re.search(r"[0-9]", page)) and int(page) > 0:
        if int(page) > (no_pages + 2):
            return HttpResponseRedirect(reverse("dashboard:applicants"))
        page = int(page)
    else:
        page = 1

    recruiters = recruiters[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    return render(
        request,
        "dashboard/company/recruiters.html",
        {
            "recruiters": recruiters,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "company": company,
        },
    )


@permission_required("activity_edit", "activity_view")
def company_jobposts(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    job_posts = company.get_jobposts()
    items_per_page = 100
    no_pages = int(math.ceil(float(job_posts.count()) / items_per_page))
    page = request.GET.get("page")
    if page and bool(re.search(r"[0-9]", page)) and int(page) > 0:
        if int(page) > (no_pages + 2):
            return HttpResponseRedirect(reverse("dashboard:applicants"))
        page = int(page)
    else:
        page = 1

    job_posts = job_posts[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    return render(
        request,
        "dashboard/company/job_posts.html",
        {
            "company": company,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "job_posts": job_posts,
        },
    )


@permission_required("activity_edit", "activity_view")
def company_tickets(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    items_per_page = 100
    tickets = company.get_company_tickets()
    no_pages = int(math.ceil(float(tickets.count()) / items_per_page))
    page = request.GET.get("page")
    if page and bool(re.search(r"[0-9]", page)) and int(page) > 0:
        if int(page) > (no_pages + 2):
            return HttpResponseRedirect(reverse("dashboard:applicants"))
        page = int(page)
    else:
        page = 1

    tickets = tickets[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    return render(
        request,
        "dashboard/company/tickets.html",
        {
            "tickets": tickets,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "company": company,
        },
    )


@permission_required("activity_edit")
def menu_status(request, menu_id, company_id):
    company = get_object_or_404(Company, id=company_id)
    menu = Menu.objects.filter(id=menu_id, company=company)
    if menu:
        menu = menu[0]
        if menu.status:
            menu.status = False
        else:
            menu.status = True
        menu.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@permission_required("activity_edit")
def delete_menu(request, menu_id, company_id):
    company = get_object_or_404(Company, id=company_id)
    menu = Menu.objects.filter(id=menu_id, company=company)
    if menu:
        menu = menu[0]
        menu.delete()
        data = {"error": False, "response": "Menu Deleted Successfully"}
    else:
        data = {"error": True, "response": "Some Problem Occurs"}
    return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def edit_menu(request, menu_id, company_id):
    company = get_object_or_404(Company, id=company_id)
    menu = get_object_or_404(Menu, id=menu_id, company=company)
    if request.method == "POST":
        validate_menu = MenuForm(request.POST, instance=menu)
        if validate_menu.is_valid():
            new_menu = validate_menu.save(commit=False)
            if request.POST.get("status") == "True":
                new_menu.status = True
            new_menu.save()
            data = {"error": False, "response": "Menu created successfully"}
        else:
            data = {"error": True, "response": validate_menu.errors}
        return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def menu_order(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    menu = get_object_or_404(Menu, id=request.GET.get("menu_id"), company=company)
    prev = request.GET.get("prev")
    current = request.GET.get("current")
    if int(prev) < int(current):
        selected_menus = Menu.objects.filter(
            lvl__gt=prev, lvl__lte=current, company=request.user.company
        )
        for each in selected_menus:
            each.lvl = each.lvl - 1
            each.save()
    else:
        selected_menus = Menu.objects.filter(
            lvl__lt=prev, lvl__gte=current, company=request.user.company
        )
        for each in selected_menus:
            each.lvl = each.lvl + 1
            each.save()
    menu.lvl = current
    menu.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@permission_required("activity_edit", "activity_view")
def search_summary(request, search_type):
    values = []
    count = []
    if request.POST.get("timestamp"):
        date = request.POST.get("timestamp").split(" - ")
        start_date = datetime.strptime(date[0], "%b %d, %Y %H:%M")
        end_date = datetime.strptime(date[1], "%b %d, %Y %H:%M")
    if search_type == "other-skills":
        summary = (
            SearchResult.objects.exclude(other_skill="")
            .values("other_skill")
            .annotate(num=Count("other_skill"))
            .order_by("-num")
        )
        if request.POST.get("search"):
            search = request.POST.get("search")
            summary = summary.filter(other_skill=search)
        if request.POST.get("timestamp"):
            summary = summary.filter(search_on__range=(start_date, end_date))
        for each in summary[:20]:
            values.append(each["other_skill"])
            count.append(each["num"])
    elif search_type == "other-locations":
        summary = (
            SearchResult.objects.exclude(other_location="")
            .values("other_location")
            .annotate(num=Count("other_location"))
            .order_by("-num")
        )
        if request.POST.get("search"):
            search = request.POST.get("search")
            summary = summary.filter(other_location=search)
        if request.POST.get("timestamp"):
            summary = summary.filter(search_on__range=(start_date, end_date))
        for each in summary[:20]:
            values.append(each["other_location"])
            count.append(each["num"])
    elif search_type == "skills":
        summary = (
            SearchResult.objects.values("skills__name")
            .annotate(num=Count("skills"))
            .order_by("-num")
        )
        if request.POST.get("search"):
            search = request.POST.get("search").split(",")
            summary = summary.filter(
                Q(skills__name__in=search) | Q(skills__slug__in=search)
            )
        if request.POST.get("timestamp"):
            summary = summary.filter(search_on__range=(start_date, end_date))
        for each in summary[:20]:
            values.append(each["skills__name"])
            count.append(each["num"])
    else:
        summary = (
            SearchResult.objects.values("locations__name")
            .annotate(num=Count("locations"))
            .order_by("-num")
        )
        if request.POST.get("search"):
            search = request.POST.get("search").split(",")
            summary = summary.filter(
                Q(locations__name__in=search) | Q(locations__slug__in=search)
            )
        if request.POST.get("timestamp"):
            summary = summary.filter(search_on__range=(start_date, end_date))
        for each in summary[:20]:
            values.append(each["locations__name"])
            count.append(each["num"])
    return render(
        request,
        "dashboard/search_summary.html",
        {
            "values": json.dumps(values),
            "count": json.dumps(count),
            "search_type": search_type,
        },
    )


@permission_required("activity_edit", "activity_view")
def new_company(request):
    if request.method == "POST":
        validate_company = CompanyForm(request.POST, request.FILES)
        if validate_company.is_valid():
            company = validate_company.save()
            company.created_from = "dashboard"
            company.email = request.user.email
            company.slug = slugify(request.POST.get("name"))
            company.company_type = "Company"
            company.website = request.POST.get("website")
            company.is_active = request.POST.get("is_active") == "on"
            if request.POST.get("meta_title"):
                company.meta_title = request.POST.get("meta_title")
            if request.POST.get("meta_description"):
                company.meta_description = request.POST.get("meta_description")
            if request.FILES.get("profile_pic"):
                file_path = get_aws_file_path(
                    request.FILES.get("profile_pic"),
                    "company/logo/",
                    slugify(request.POST.get("name")),
                )
                company.profile_pic = file_path
            if request.FILES.get("campaign_icon"):
                file_path = get_aws_file_path(
                    request.FILES.get("campaign_icon"),
                    "company/logo/",
                    slugify(request.POST.get("name")),
                )
                company.campaign_icon = file_path
            company.save()
            data = {"error": False, "response": "Company created successfully"}
        else:
            data = {"error": True, "response": validate_company.errors}
        return HttpResponse(json.dumps(data))

    return render(request, "dashboard/company/new_company.html")


@permission_required("activity_edit", "activity_view")
def edit_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == "POST":
        validate_company = CompanyForm(request.POST, request.FILES, instance=company)
        if validate_company.is_valid():
            company_active = company.is_active
            company = validate_company.save()
            company.website = request.POST.get("website")
            company.slug = request.POST.get("slug")
            company.is_active = request.POST.get("is_active") == "on"
            if request.POST.get("meta_title"):
                company.meta_title = request.POST.get("meta_title")
            if request.POST.get("meta_description"):
                company.meta_description = request.POST.get("meta_description")
            if request.FILES.get("profile_pic"):
                if company.profile_pic:
                    url = str(company.profile_pic).split("cdn.peeljobs.com")[-1:]
                    AWS().cloudfront_invalidate(paths=url)
                file_path = get_aws_file_path(
                    request.FILES.get("profile_pic"), "company/logo/", company.slug
                )
                company.profile_pic = file_path
            if request.FILES.get("campaign_icon"):
                if company.campaign_icon:
                    url = str(company.campaign_icon).split("cdn.peeljobs.com")[-1:]
                    AWS().cloudfront_invalidate(paths=url)
                file_path = get_aws_file_path(
                    request.FILES.get("campaign_icon"),
                    "company/logo/",
                    slugify(request.POST.get("name")),
                )
                company.campaign_icon = file_path

            company.save()
            data = {
                "error": False,
                "response": "Company edited successfully",
                "company_active": company_active,
                "edit": True,
            }
        else:
            data = {"error": True, "response": validate_company.errors}
        return HttpResponse(json.dumps(data))
    return render(request, "dashboard/company/new_company.html", {"company": company})


@permission_required("activity_edit", "activity_view")
def applicants_mail(request):
    current_date = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").strftime(
        "%Y-%m-%d"
    )

    all_mail_applicants = list(db.users.find({"date": current_date}))

    items_per_page = 100

    no_pages = int(math.ceil(float(len(all_mail_applicants)) / items_per_page))
    page = request.POST.get("page")
    if page and bool(re.search(r"[0-9]", page)) and int(page) > 0:
        if int(page) > (no_pages + 2):
            return HttpResponseRedirect(reverse("dashboard:applicants"))
        page = int(page)
    else:
        page = 1

    all_mail_applicants = all_mail_applicants[
        (page - 1) * items_per_page : page * items_per_page
    ]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    return render(
        request,
        "dashboard/all_mail_applicants.html",
        {
            "all_mail_applicants": all_mail_applicants,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
        },
    )


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
            # job_post.minified_url = google_mini('https://peeljobs.com' + job_url, settings.MINIFIED_URL)
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


@permission_required("activity_edit", "activity_view")
def locations(request, status):
    if status == "active":
        locations = (
            City.objects.filter(status="Enabled")
            .annotate(num_posts=Count("locations"))
            .prefetch_related("state")
            .order_by("name")
        )
    else:
        locations = (
            City.objects.filter(status="Disabled")
            .annotate(num_posts=Count("locations"))
            .prefetch_related("state")
            .order_by("name")
        )
    items_per_page = 100
    if request.POST.get("search"):
        locations = locations.filter(name__icontains=request.POST.get("search"))
    no_pages = int(math.ceil(float(locations.count()) / items_per_page))
    page = request.GET.get("page")
    if page and bool(re.search(r"[0-9]", page)) and int(page) > 0:
        if int(page) > (no_pages + 2):
            return HttpResponseRedirect(reverse("dashboard:locations"))
        page = int(page)
    else:
        page = 1
    if request.POST.get("mode") == "remove_city":
        city = City.objects.filter(id=request.POST.get("id"))
        if city:
            city.delete()
            data = {"error": False, "message": "City Removed Successfully"}
        else:
            data = {"error": True, "message": "City Not Found"}
        return HttpResponse(json.dumps(data))
    if request.POST.get("mode") == "edit":
        city = City.objects.filter(id=int(request.POST.get("id"))).first()
        if city:
            new_city = CityForm(request.POST, instance=city)
            try:
                if request.POST.get("meta"):
                    json.loads(request.POST.get("meta"))
                valid = True
            except BaseException as e:
                new_city.errors["meta"] = "Enter Valid Json Format - " + str(e)
                valid = False
            if new_city.is_valid() and valid:
                new_city.save()
                if request.POST.get("page_content"):
                    city.page_content = request.POST.get("page_content")
                if request.POST.get("internship_page_content"):
                    city.page_content = request.POST.get("page_content")
                if request.POST.get("meta"):
                    city.meta = json.loads(request.POST.get("meta"))
                city.save()
                data = {"error": False, "message": "City Updated Successfully"}
            else:
                data = {
                    "error": True,
                    "message": new_city.errors,
                    "id": request.POST.get("id"),
                }
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "message": "City Not Found"}
            return HttpResponse(json.dumps(data))
    locations = locations[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    cities = City.objects.filter(status="Enabled", parent_city=None)
    return render(
        request,
        "dashboard/locations.html",
        {
            "locations": locations,
            "cities": cities,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "status": status,
        },
    )


@permission_required("activity_edit", "activity_view")
def reports(request):
    cities = City.objects.filter()
    skills = [
        "java",
        "html",
        "php",
        "android",
        ".net",
        "bpo",
        "testing",
        "javascript",
        "c#",
        "adobe photoshop",
        "fresher",
        "css",
        "mysql",
        "j2ee",
        "sql server",
        "sales",
        "marketing",
        "accounting",
        "technical support",
        "python",
    ]
    all_skills = Skill.objects.filter()
    location = []
    jobs_location = []

    job_posts = []
    active_recruiters = []
    inactive_recruiters = []
    skills_names = []
    skill_wise_jobs_count = []
    for city in cities:
        users = User.objects.filter(city=city).exclude(user_type="JS")
        if request.method == "POST" and request.POST.get("timestamp"):
            date = request.POST.get("timestamp").split(" - ")
            start_date = datetime.strptime(date[0], "%b %d, %Y %H:%M")
            end_date = datetime.strptime(date[1], "%b %d, %Y %H:%M")
            users = users.filter(date_joined__range=(start_date, end_date))
        if users:
            location.append(str(city.name))
            active_recruiters.append(int(users.filter(is_active=True).count()))
            inactive_recruiters.append(int(users.filter(is_active=False).count()))
        jobs = JobPost.objects.filter(location__in=[city], status="Live")
        if request.method == "POST" and request.POST.get("timestamp"):

            date = request.POST.get("timestamp").split(" - ")
            start_date = datetime.strptime(date[0], "%b %d, %Y %H:%M")
            end_date = datetime.strptime(date[1], "%b %d, %Y %H:%M")

            jobs = jobs.filter(published_on__range=(start_date, end_date))

        if jobs:
            jobs_location.append(str(city.name))
            job_posts.append(jobs.count())
    if request.POST.getlist("skills"):
        skills = Skill.objects.filter(
            id__in=request.POST.getlist("skills")
        ).values_list("name", flat=True)
    for skill in skills:
        skill = Skill.objects.filter(name__iexact=skill)
        jobs_skills = JobPost.objects.filter(skills__in=skill, status="Live")
        if request.method == "POST" and request.POST.get("timestamp"):

            date = request.POST.get("timestamp").split(" - ")
            start_date = datetime.strptime(date[0], "%b %d, %Y %H:%M")
            end_date = datetime.strptime(date[1], "%b %d, %Y %H:%M")

            jobs_skills = jobs_skills.filter(published_on__range=(start_date, end_date))
        if jobs_skills:
            skills_names.append(skill[0].name)
            skill_wise_jobs_count.append(jobs_skills.count())

    return render(
        request,
        "dashboard/reports.html",
        {
            "location": json.dumps(location),
            "job_posts": json.dumps(job_posts),
            "cities": cities,
            "skills": skills,
            "active_recruiters": json.dumps(active_recruiters),
            "inactive_recruiters": json.dumps(inactive_recruiters),
            "skill_wise_jobs_count": json.dumps(skill_wise_jobs_count),
            "skills_names": json.dumps(skills_names),
            "all_skills": all_skills,
            "selected_skills": request.POST.getlist("skills"),
            "jobs_location": json.dumps(jobs_location),
        },
    )


def get_csv_reader(file_path):
    file_data = file_path.read().decode("utf-8-sig").encode("utf-8")
    csv_reader = csv.DictReader(file_data, delimiter=",", quotechar='"')
    csv_reader.fieldnames = [header.strip() for header in csv_reader.fieldnames]
    csv_reader = list(csv_reader)
    return csv_reader


def post_on_all_fb_groups(request, post_id):
    job_post = JobPost.objects.filter(id=post_id)
    if job_post.exists():
        poston_allfb_groups.delay(post_id)
    return HttpResponse(
        json.dumps(
            {"errors": False, "response": "Sucessfully Published Job Post In Fb Groups"}
        )
    )


def adding_existing_candidates_to_jobposts(request, post_id):
    job_post = get_object_or_404(JobPost, id=post_id)
    user_technical_skills = TechnicalSkill.objects.filter(
        skill__in=job_post.skills.all().values_list("id", flat=True)
    )
    users = User.objects.filter(user_type="JS", skills__in=user_technical_skills)
    for user in users:
        if not AppliedJobs.objects.filter(user=user, job_post=job_post):
            AppliedJobs.objects.create(
                user=user,
                job_post=job_post,
                status="Pending",
                ip_address=request.META["REMOTE_ADDR"],
                user_agent=request.META["HTTP_USER_AGENT"],
            )
    return HttpResponse(
        json.dumps({"errors": False, "response": "Sucessfully Added Users to Jobposts"})
    )


@login_required
def aws_push_to_s3(request):
    if request.method == "POST":
        if request.FILES.get("upload_file"):
            blog_post = Post.objects.filter(id=request.POST.get("post_id"))
            if blog_post:
                attachment = BlogAttachment.objects.create(
                    post=blog_post[0],
                    uploaded_by=request.user,
                    attached_file=request.FILES.get("upload_file"),
                )
                return HttpResponse(
                    json.dumps(
                        {
                            "error": False,
                            "response": "Please Upload An Image",
                            "url": str(settings.STATIC_URL)
                            + str(attachment.attached_file.name),
                            "name": attachment.attached_file.name,
                            "id": attachment.id,
                        }
                    )
                )
            return HttpResponse(
                json.dumps(
                    {
                        "error": True,
                        "response": "Blog post is not exist, please try again",
                    }
                )
            )
        return HttpResponse(
            json.dumps({"error": True, "response": "Please Upload An Image"})
        )


@login_required
def aws_del_from_s3(request):
    if request.method == "POST":
        if request.POST.get("attachment_id"):
            blog_attachment = BlogAttachment.objects.filter(
                id=request.POST.get("attachment_id")
            )
            if blog_attachment:
                blog_attachment.delete()
                return HttpResponse(
                    json.dumps(
                        {"error": False, "response": "Attachment Deleted Successfully"}
                    )
                )
            return HttpResponse(
                json.dumps(
                    {
                        "error": True,
                        "response": "Blog post is not exist, please try again",
                    }
                )
            )
    return HttpResponse(
        json.dumps({"error": True, "response": "Please Upload An Image"})
    )


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


@permission_required("activity_edit")
def enable_agency(request, agency_id):
    agency = get_object_or_404(User, id=agency_id)
    if agency.is_active:
        agency.is_active = False
    else:
        agency.is_active = True
    agency.save()
    page = request.GET.get("page")
    url = reverse("dashboard:companies", kwargs={"company_type": "consultant"})
    if request.GET.get("status") == "active":
        url = (
            reverse("dashboard:companies", kwargs={"company_type": "consultant"})
            + "?page="
            + page
            + "&active=true"
        )
    if request.GET.get("status") == "inactive":
        url = (
            reverse("dashboard:companies", kwargs={"company_type": "consultant"})
            + "?page="
            + page
            + "&active=false"
        )
    if request.GET.get("status") == "admin_active":
        url = (
            reverse("dashboard:companies", kwargs={"company_type": "consultant"})
            + "?page="
            + page
            + "&admin=true"
        )
    if request.GET.get("status") == "admin_inactive":
        url = (
            reverse("dashboard:companies", kwargs={"company_type": "consultant"})
            + "?page="
            + page
            + "&admin=false"
        )
    return HttpResponseRedirect(url)


@permission_required("activity_edit")
def removing_duplicate_companies(request):
    all_duplicate_companies = Company.objects.filter()
    if request.method == "POST":
        if request.POST.getlist("duplicate_companies"):
            duplicate_companies = request.POST.getlist("duplicate_companies")
            company_id = request.POST.get("company")
            all_company = Company.objects.filter(id__in=duplicate_companies)
            all_duplicate_companies = all_company.values_list("id", flat=True)
            each_company = Company.objects.filter(id=company_id)
            jobposts = JobPost.objects.filter(company_id__in=all_duplicate_companies)
            users = User.objects.filter(company_id__in=all_duplicate_companies)
            if each_company:
                company = each_company[0]
                jobposts.update(company=company)
                users.update(company=company)
            data = {"error": False, "response": "Company Jobposts updated successfully"}
        else:
            data = {"error": True, "response": "Please Select the duplicate companies"}
        return HttpResponse(json.dumps(data))

    return render(
        request,
        "dashboard/company/update_jobposts.html",
        {"all_duplicate_companies": all_duplicate_companies},
    )


def google_login(request):
    if "code" in request.GET:
        params = {
            "grant_type": "authorization_code",
            "code": request.GET.get("code"),
            "redirect_uri": settings.GOOGLE_LOGIN_HOST + reverse("social:google_login"),
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
        }

        info = requests.post("https://accounts.google.com/o/oauth2/token", data=params)
        info = info.json()
        url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {"access_token": info["access_token"]}
        kw = dict(params=params, headers={}, timeout=60)
        response = requests.request("GET", url, **kw)
        user_document = response.json()
        email_matches = UserEmail.objects.filter(email=user_document["email"])
        link = "https://plus.google.com/" + user_document["id"]
        picture = user_document.get("picture", "")
        dob = user_document.get("birthday", "")
        gender = user_document.get("gender", "")
        link = user_document.get("link", link)
        if email_matches:
            user = email_matches[0].user
            if not user.is_gp_connected:
                Google.objects.create(
                    user=user,
                    google_url=link,
                    verified_email=user_document["verified_email"],
                    google_id=user_document["id"],
                    family_name=user_document["family_name"],
                    name=user_document["name"],
                    given_name=user_document["given_name"],
                    dob=dob,
                    email=user_document["email"],
                    gender=gender,
                    picture=picture,
                )
            if user.is_superuser:
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                return HttpResponseRedirect("/dashboard/")
        else:
            user = User.objects.filter(
                email__iexact=user_document.get("email", "")
            ).first()
            if user:
                user.first_name = user_document.get("given_name", "")
                user.last_name = user_document.get("family_name", "")
                user.photo = picture
                user.profile_pic = picture
                user.profile_updated = datetime.now(timezone.utc)
                user.is_active = True
                user.save()
            else:
                user = User.objects.create(
                    username=user_document.get("email", ""),
                    email=user_document.get("email", ""),
                    first_name=user_document.get("given_name", ""),
                    last_name=user_document.get("family_name", ""),
                    photo=picture,
                    user_type="",
                    profile_updated=datetime.now(timezone.utc),
                    is_active=True,
                    registered_from="Social",
                )
            if user_document.get("gender"):
                user.gender = "M" if user_document.get("gender") == "male" else "F"
                user.save()

            Google.objects.create(
                user=user,
                google_url=link,
                verified_email=user_document.get("verified_email", ""),
                google_id=user_document.get("id", ""),
                family_name=user_document.get("family_name", ""),
                name=user_document.get("name", ""),
                given_name=user_document.get("given_name", ""),
                dob=dob,
                email=user_document.get("email", ""),
                gender=gender,
                picture=picture,
            )

            UserEmail.objects.create(
                user=user, email=user_document.get("email", ""), is_primary=True
            )

            if user.is_superuser:
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                return HttpResponseRedirect("/dashboard/")
        return HttpResponseRedirect("/")
    else:
        rty = (
            "https://accounts.google.com/o/oauth2/auth?client_id="
            + settings.GOOGLE_CLIENT_ID
            + "&response_type=code"
        )
        rty += (
            "&scope=https://www.googleapis.com/auth/userinfo.profile"
            + " https://www.googleapis.com/auth/userinfo.email"
            + " &redirect_uri="
            + settings.GOOGLE_LOGIN_HOST
            + reverse("social:google_login")
            + "&state=1235dfghjkf123"
        )
        return HttpResponseRedirect(rty)


@permission_required("activity_view", "activity_edit")
def assessment_skills(request):
    skills = Skill.objects.filter(status="Active").order_by("name")
    if request.GET.get("search"):
        skills = skills.filter(name__icontains=request.GET.get("search"))
    return render(
        request, "dashboard/assessments/skills_lists.html", {"skills": skills}
    )


@permission_required("activity_view", "activity_edit")
def new_question(request):
    questionFormSet = modelformset_factory(Question, form=QuestionForm, can_delete=True)
    data = {
        "form-TOTAL_FORMS": "1",
        "form-INITIAL_FORMS": "0",
        "form-MAX_NUM_FORMS": "10",
    }
    question_form_set = questionFormSet(data)
    skills = Skill.objects.filter(status="Active")
    if request.POST:
        question_form_set = questionFormSet(request.POST)
        form_count = int(request.POST.get("form-TOTAL_FORMS"))
        for i in range(0, form_count):
            answers = request.POST.getlist("form-" + str(i) + "-answer")
            duplicates = [
                x[0] for x in enumerate(answers) if x[1] and answers.count(x[1]) > 1
            ]
            if duplicates:
                question_form_set.errors[i].update({"duplicates": duplicates})
        if question_form_set.is_valid():
            question = question_form_set.save()
            for i in range(0, form_count):
                answers = request.POST.getlist("form-" + str(i) + "-answer")
                sol = Solution.objects.bulk_create(
                    [
                        Solution(description=j, given_by=request.user, status="Pending")
                        for j in answers
                    ]
                )
                que = question[i]
                que.solutions.add(*sol)
                que.status = "Pending"
                que.save()
            data = {"error": False, "response": "Questions Created Successfully"}
        else:
            data = {"error": True, "response": question_form_set.errors}
        return HttpResponse(json.dumps(data))
    return render(
        request,
        "dashboard/assessments/new_question.html",
        {"skills": skills, "question_form_set": question_form_set},
    )


@permission_required("activity_view", "activity_edit")
def skill_questions(request, skill_id):
    skill = Skill.objects.filter(id=skill_id).first()
    skill_questions = (
        skill.skill_questions.all().prefetch_related("created_by") if skill else ""
    )
    if request.method == "POST":
        if request.POST.get("mode") == "search":
            if request.POST.get("timestamp", ""):
                date = request.POST.get("timestamp").split(" - ")
                start_date = datetime.strptime(date[0], "%b %d, %Y %H:%M")
                end_date = datetime.strptime(date[1], "%b %d, %Y %H:%M")
                skill_questions = skill_questions.filter(
                    created_on__range=(start_date, end_date)
                )

            if request.POST.get("search", ""):
                skill_questions = skill_questions.filter(
                    Q(title__icontains=request.POST.get("search"))
                    | Q(status__icontains=request.POST.get("search"))
                    | Q(created_by__username__icontains=request.POST.get("search"))
                )
        else:
            question = Question.objects.filter(id=request.POST.get("id")).first()
            if question:
                if request.POST.get("mode") == "disable_question":
                    question.status = "Closed"
                    question.save()
                    data = {"error": False, "message": "Question Disabled Successfully"}
                    return HttpResponse(json.dumps(data))
                if request.POST.get("mode") == "enable_question":
                    question.status = "Pending"
                    question.save()
                    data = {"error": False, "message": "Question Enabled Successfully"}
                    return HttpResponse(json.dumps(data))
                if request.POST.get("mode") == "set_live":
                    question.status = "Live"
                    question.save()
                    question.solutions.all().update(status="Live")
                    data = {"error": False, "message": "Question Enabled Successfully"}
                    return HttpResponse(json.dumps(data))
                if request.POST.get("mode") == "remove_question":
                    question.delete()
                    data = {"error": False, "message": "Question Removed Successfully"}
                    question.solutions.all().delete()
                    return HttpResponse(json.dumps(data))
            else:
                data = {"error": True, "message": "Question Not Found"}
                return HttpResponse(json.dumps(data))
    items_per_page = 10
    no_pages = int(math.ceil(float(skill_questions.count()) / items_per_page))

    if (
        "page" in request.POST
        and bool(re.search(r"[0-9]", request.POST.get("page")))
        and int(request.POST.get("page")) > 0
    ):
        if int(request.POST.get("page")) > (no_pages + 2):
            page = 1
        else:
            page = int(request.POST.get("page"))
    else:
        page = 1
    skill_questions = skill_questions[
        (page - 1) * items_per_page : page * items_per_page
    ]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    return render(
        request,
        "dashboard/assessments/skill_questions.html",
        {
            "skill": skill,
            "skill_questions": skill_questions,
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
def view_question(request, question_id):
    question = Question.objects.filter(id=question_id).first()
    if request.method == "POST":
        if question:
            if request.POST.get("mode") == "edit_question":
                qform = QuestionForm(request.POST, instance=question)
                if qform.is_valid():
                    qform.save()
                    data = {"error": False, "response": "Question updated Successfully"}
                else:
                    data = {"error": True, "response": qform.errors}
                return HttpResponse(json.dumps(data))
            if request.POST.get("mode") == "edit_solution":
                sol = Solution.objects.filter(
                    id=request.POST.get("solution", 0)
                ).first()
                if sol:
                    sform = SolutionForm(request.POST, instance=sol)
                    ans = question.solutions.filter(
                        description__iexact=request.POST.get("answer")
                    ).exclude(id=sol.id)
                    if ans.exists():
                        sform.errors["answer"] = "Solution Already Exists"
                    if sform.is_valid():
                        sol.status = request.POST.get("status")
                        sol.description = request.POST.get("answer")
                        sol.save()
                        data = {
                            "error": False,
                            "response": "Solution updated Successfully",
                        }
                    else:
                        data = {"error": True, "response": sform.errors}
                else:
                    data = {"error": True, "message": "Solution Not Found"}
                return HttpResponse(json.dumps(data))
            if request.POST.get("mode") == "add_solution":
                answers = request.POST.getlist("answer")
                duplicates = [
                    x[0] for x in enumerate(answers) if answers.count(x[1]) > 1
                ]
                for i in answers:
                    sol = question.solutions.filter(description__iexact=i)
                    if sol.exists():
                        duplicates.append(answers.index(i))
                if duplicates:
                    data = {"error": True, "duplicate": duplicates}
                elif "" in answers or "" in request.POST.getlist("status"):
                    data = {"error": True}
                else:
                    for i in range(0, int(request.POST.get("count"))):
                        sol = Solution.objects.create(
                            description=request.POST.getlist("answer")[i],
                            given_by=request.user,
                            status=request.POST.getlist("status")[i],
                        )
                        question.solutions.add(sol)
                        data = {
                            "error": False,
                            "message": "Solutions Added Successfully",
                        }
                return HttpResponse(json.dumps(data))
            if request.POST.get("mode") == "remove_solution":
                sol = Solution.objects.filter(id=request.POST.get("id"))
                sol.delete()
                data = {"error": False, "message": "Solution Removed Successfully"}
                return HttpResponse(json.dumps(data))
            if request.POST.get("mode") == "remove_question":
                url = reverse(
                    "dashboard:skill_questions", kwargs={"skill_id": question.skills.id}
                )
                question.delete()
                data = {"error": False, "redirect_url": url}
                return HttpResponse(json.dumps(data))
        data = {"error": True, "message": "Question Not Found"}
        return HttpResponse(json.dumps(data))
    else:
        skills = Skill.objects.filter(status="Active")
        if question:
            return render(
                request,
                "dashboard/assessments/view_question.html",
                {"question": question, "skills": skills},
            )
        return render(request, "dashboard/404.html", status=404)


def updating_meta_data():
    skills = Skill.objects.filter(status="Active", slug="java")
    for skill in skills:

        meta_title = (
            skill.meta["meta_title"] if "meta_title" in skill.meta.keys() else ""
        )
        meta_description = (
            skill.meta["meta_description"]
            if "meta_description" in skill.meta.keys()
            else ""
        )
        walkin_meta_title = meta_title.replace(" Jobs", " Walkins").replace(
            "Openings", "Vacancies"
        )
        walkin_meta_description = (
            meta_description.replace("jobs", "Walkins")
            .replace("openings", "Vacancies")
            .replace("Jobs", "Walkins")
            .replace("Openings", "Vacancies")
        )
        meta = skill.meta
        meta["walkin_meta_title"] = walkin_meta_title
        meta["walkin_meta_description"] = walkin_meta_description
        skill.meta = meta
        skill.save()


@permission_required("activity_edit")
def save_meta_data(request):
    if request.POST:
        if request.POST.get("mode") == "add_data":
            mform = MetaForm(request.POST)
            if mform.is_valid():
                mform.save()
                return HttpResponse(
                    json.dumps({"error": False, "response": "Data Added Successfuly"})
                )
            return HttpResponse(json.dumps({"error": True, "response": mform.errors}))
        if request.POST.get("mode") == "edit_data":
            instance = get_object_or_404(MetaData, id=request.POST.get("meta_id"))
            form = MetaForm(request.POST or None, instance=instance)
            if form.is_valid():
                form.save()

                return HttpResponse(
                    json.dumps({"error": False, "response": "Updated Successfully"})
                )
            return HttpResponse(json.dumps({"error": True, "response": form.errors}))
        if request.POST.get("mode") == "delete_data":
            if MetaData.objects.get(pk=request.POST.get("meta_id")):
                MetaData.objects.get(pk=request.POST.get("meta_id")).delete()
            return HttpResponse(
                json.dumps({"error": False, "response": "Removed Successfully!"})
            )
    meta_data = MetaData.objects.all()
    return render(
        request, "dashboard/base_data/save_meta_data.html", {"meta_data": meta_data}
    )


@permission_required("activity_edit")
def moving_duplicates(request, value):
    if value == "skills":
        values = Skill.objects.annotate(num_posts=Count("jobpost"))
        if request.method == "POST":
            if request.POST.getlist("duplicates"):
                duplicates = Skill.objects.filter(
                    id__in=request.POST.getlist("duplicates")
                )
                original = Skill.objects.filter(id=request.POST.get("original")).first()
                search_results = SearchResult.objects.filter(skills__in=duplicates)
                for search in search_results:
                    for skill in duplicates:
                        search.skills.remove(skill)
                    search.skills.add(original)
                alerts = JobAlert.objects.filter(skill__in=duplicates)
                for alert in alerts:
                    for skill in duplicates:
                        alert.skill.remove(skill)
                    alert.skill.add(original)
                major_skill_jobs = JobPost.objects.filter(major_skill__in=duplicates)
                major_skill_jobs.update(major_skill=original)
                tech_skills = TechnicalSkill.objects.filter(skill__in=duplicates)
                tech_skills.update(skill=original)
                jobposts = JobPost.objects.filter(skills__in=duplicates)
                for job in jobposts:
                    for skill in duplicates:
                        job.skills.remove(skill)
                    job.skills.add(original)
                users = User.objects.filter(technical_skills__in=duplicates)
                for user in users:
                    for skill in duplicates:
                        user.technical_skills.remove(skill)
                    user.technical_skills.add(original)
                projects = Project.objects.filter(skills__in=duplicates)
                for project in projects:
                    for skill in duplicates:
                        project.skills.remove(skill)
                    project.skills.add(original)
                agency_resumes = AgencyResume.objects.filter(skill__in=duplicates)
                for resume in agency_resumes:
                    for skill in duplicates:
                        resume.skill.remove(skill)
                    resume.skill.add(original)
                subscribers = Subscriber.objects.filter(skill__in=duplicates)
                subscribers.update(skill=original)
                questions = Question.objects.filter(skills__in=duplicates)
                questions.update(skills=original)
                return HttpResponse(
                    json.dumps(
                        {"error": False, "response": "Skills updated successfully"}
                    )
                )
            return HttpResponse(
                json.dumps(
                    {"error": True, "response": "Please Select the duplicate Skills"}
                )
            )
    elif value == "degrees":
        values = Qualification.objects.annotate(num_posts=Count("jobpost"))
        if request.method == "POST":
            if request.POST.getlist("duplicates"):
                original = Qualification.objects.filter(
                    id=request.POST.get("original")
                ).first()
                duplicates = Qualification.objects.filter(
                    id__in=request.POST.getlist("duplicates")
                )
                jobs = JobPost.objects.filter(edu_qualification__in=duplicates)
                for job in jobs:
                    for deg in duplicates:
                        job.edu_qualification.remove(deg)
                    job.edu_qualification.add(original)
                degrees = Degree.objects.filter(degree_name__in=duplicates)
                degrees.update(degree_name=original)
                return HttpResponse(
                    json.dumps(
                        {"error": False, "response": "Degrees updated successfully"}
                    )
                )
            return HttpResponse(
                json.dumps(
                    {"error": True, "response": "Please Select the duplicate Degrees"}
                )
            )
    elif value == "locations":
        values = City.objects.annotate(num_posts=Count("locations")).annotate(
            user_count=Count("current_city")
        )
        if request.method == "POST":
            if request.POST.getlist("duplicates"):
                duplicates = City.objects.filter(
                    id__in=request.POST.getlist("duplicates")
                )
                original = City.objects.filter(id=request.POST.get("original")).first()
                duplicates.update(parent_city=original)
                users = User.objects.filter(city__in=duplicates)
                users.update(city=original)
                current_users = User.objects.filter(current_city__in=duplicates)
                current_users.update(current_city=original)
                preferred_users = User.objects.filter(preferred_city__in=duplicates)
                for user in preferred_users:
                    for city in duplicates:
                        user.preferred_city.remove(city)
                    user.preferred_city.add(original)
                jobs = JobPost.objects.filter(location__in=duplicates)
                for job in jobs:
                    for city in duplicates:
                        job.location.remove(city)
                    job.location.add(original)
                alerts = JobAlert.objects.filter(location__in=duplicates)
                for alert in alerts:
                    for city in duplicates:
                        alert.location.remove(city)
                    alert.location.add(original)
                searches = SearchResult.objects.filter(locations__in=duplicates)
                for search in searches:
                    for city in duplicates:
                        search.locations.remove(city)
                    search.locations.add(original)
                institutes = EducationInstitue.objects.filter(city__in=duplicates)
                institutes.update(city=original)
                Projects = Project.objects.filter(location__in=duplicates)
                Projects.update(location=original)
                agency_branches = AgencyCompanyBranch.objects.filter(
                    location__in=duplicates
                )
                agency_branches.update(location=original)
                return HttpResponse(
                    json.dumps(
                        {"error": False, "response": "Locations updated successfully"}
                    )
                )
            return HttpResponse(
                json.dumps(
                    {"error": True, "response": "Please Select the duplicate Locations"}
                )
            )
    return render(
        request, "dashboard/duplicates.html", {"values": values, "status": value}
    )


@permission_required("activity_edit")
def clear_cache(request):
    cache._cache.flush_all()
    return HttpResponseRedirect("/dashboard/")
