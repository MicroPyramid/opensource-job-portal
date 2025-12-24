from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import render

from mpcomp.views import permission_required
from peeldb.models import (
    AppliedJobs,
    City,
    Company,
    JobPost,
    Skill,
    Ticket,
    User,
)
from pjob.views import months


# Functions to move here from main views.py:


@permission_required("activity_edit")
def index(request):
    if (
        not request.user.is_jobseeker
        and not request.user.is_recruiter
        and not request.user.is_agency_recruiter
    ):
        current_date = datetime.strptime(
            str(datetime.now().date()), "%Y-%m-%d"
        ).strftime("%Y-%m-%d")
        today_admin_walkin_jobs = JobPost.objects.filter(
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
            today_admin_walkin_jobs = today_admin_walkin_jobs.filter(
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
            "today_admin_walkin_pending_jobs": today_admin_walkin_jobs.filter(
                status="Pending"
            ).count(),
            "today_admin_walkin_published_jobs": today_admin_walkin_jobs.filter(
                status="Published"
            ).count(),
            "today_admin_walkin_live_jobs": today_admin_walkin_jobs.filter(
                status="Live"
            ).count(),
            "today_admin_walkin_disabled_jobs": today_admin_walkin_jobs.filter(
                status="Disabled"
            ).count(),
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

