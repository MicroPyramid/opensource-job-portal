from django.conf import settings
from django.conf.urls import include, url
from django.urls import path
from pjob.views import (
    skill_location_wise_fresher_jobs,
    skill_fresher_jobs,
    skill_location_walkin_jobs,
    register_using_email,
    login_user_email,
    forgot_password,
    user_activation,
    user_reg_success,
    recruiter_profile,
    jobs_by_location,
    jobs_by_skill,
    jobs_by_degree,
    jobs_by_industry,
    full_time_jobs,
    walkin_jobs,
    city_internship_jobs,
    internship_jobs,
    government_jobs,
    each_company_jobs,
    job_industries,
    companies,
    jobposts_by_date,
    # week_calendar,
    job_locations,
    set_password,
    job_skills,
    job_detail,
    # year_calendar,
    # calendar_add_event,
    # calendar_event_list,
    # month_calendar,
    recruiters,
    user_subscribe,
    unsubscribe,
    fresher_jobs_by_skills,
    process_email,
    location_fresher_jobs,
)
from search.views import (
    skill_auto_search,
    city_auto_search,
    custome_search,
    custom_walkins,
    search_slugs,
)
from candidate.views import (
    bounces,
    assessment_changes,
    applicant_unsubscribing,
    applicant_email_unsubscribing,
    question_view,
    assessments_questions,
    alert_subscribe_verification,
)
from recruiter.views import index
from psite.views import (
    contact,
    sitemap,
    get_out,
    pages,
    custom_500,
    sitemap_xml,
    # users_login,
    custom_404,
    auth_return,
)
from pjob.views import index as job_list

from django.contrib import admin


urlpatterns = [
    url(
        r"^(?P<job_title_slug>[a-z0-9-.,*?]+)-(?P<job_id>([0-9])+)/$",
        job_detail,
        name="job_detail",
    ),
    url(
        r"^(?P<skill_name>[-\w]+)-fresher-jobs-in-(?P<city_name>[-\w]+)/$",
        skill_location_wise_fresher_jobs,
        name="skill_location_wise_fresher_jobs",
    ),
    url(
        r"^(?P<skill_name>[-\w]+)-fresher-jobs-in-(?P<city_name>[-\w]+)/(?P<page_num>[0-9]+)/$",
        skill_location_wise_fresher_jobs,
    ),
    url(
        r"^internship-jobs-in-(?P<location>[-\w]+)/$",
        city_internship_jobs,
        name="city_internship_jobs",
    ),
    url(
        r"^internship-jobs-in-(?P<location>[-\w]+)/(?P<page_num>[0-9]+)/$",
        city_internship_jobs,
    ),
    url(
        r"^fresher-jobs-in-(?P<city_name>[-\w]+)/$",
        location_fresher_jobs,
        name="location_fresher_jobs",
    ),
    url(
        r"^fresher-jobs-in-(?P<city_name>[-\w]+)/(?P<page_num>[0-9]+)/$",
        location_fresher_jobs,
        name="location_fresher_jobs",
    ),
    url(
        r"^(?P<skill_name>[-\w]+)-jobs-in-(?P<city_name>[-\w]+)/$",
        custome_search,
        name="custome_search",
    ),
    url(
        r"^(?P<skill_name>[-\w]+)-jobs-in-(?P<city_name>[-\w]+)/(?P<page_num>[0-9]+)/$",
        custome_search,
    ),
    url(
        r"^(?P<skill_name>[-\w]+)-walkins-in-(?P<city_name>[-\w]+)/$",
        custom_walkins,
        name="custom_walkins",
    ),
    url(
        r"^(?P<skill_name>[-\w]+)-walkins-in-(?P<city_name>[-\w]+)/(?P<page_num>[0-9]+)/$",
        custom_walkins,
    ),
    url(
        r"^(?P<skill_name>[-\w]+)-fresher-jobs/$",
        skill_fresher_jobs,
        name="skill_fresher_jobs",
    ),
    url(
        r"^(?P<skill_name>[-\w]+)-fresher-jobs/(?P<page_num>[0-9]+)/$",
        skill_fresher_jobs,
    ),
    url(
        r"^(?P<skill_name>[-\w]+)-walkins/(?P<page_num>[0-9]+)/$",
        skill_location_walkin_jobs,
    ),
    url(
        r"^(?P<skill_name>[-\w]+)-walkins/$",
        skill_location_walkin_jobs,
        name="skill_walkin_jobs",
    ),
    url(
        r"^walkins-in-(?P<skill_name>[-\w]+)/(?P<page_num>[0-9]+)/$",
        skill_location_walkin_jobs,
    ),
    url(
        r"^walkins-in-(?P<skill_name>[-\w]+)/$",
        skill_location_walkin_jobs,
        name="location_walkin_jobs",
    ),
    url(r"^skill-auto/$", skill_auto_search),
    url(r"^city-auto/$", city_auto_search),
    url(r"^get/search-slugs/$", search_slugs, name="get_search_slugs"),
    url(r'^admin/', admin.site.urls),# Here's the typo
    url(r"^search/", include("search.urls", namespace="search")),
    url(r"^skill-auto/$", skill_auto_search),
    url(
        r"^unsubscribe_email/(?P<email_type>([a-z0-9-])+)/(?P<message_id>[a-zA-Z0-9_-]+.*?)/$",
        applicant_email_unsubscribing,
        name="applicant_email_unsubscribing",
    ),
    url(
        r"^email-unsubscribe/(?P<message_id>[a-zA-Z0-9_-]+.*?)/$",
        applicant_unsubscribing,
        name="applicant_unsubscribing",
    ),
    url(r"^social/", include("social.urls", namespace="social")),
    url(r"^dashboard/", include("dashboard.urls", namespace="dashboard")),
    url(r"^recruiter/", include("recruiter.urls", namespace="recruiter")),
    url(r"^agency/", include("agency.urls", namespace="agency")),
    url(r"^tellme/", include("tellme.urls")),
    url(r"^post-job/$", index, name="post_job"),
    url(r"^bounces/$", bounces),
    url(r"registration/using_email/$", register_using_email, name="register_email"),
    url(r"applicant/login/$", login_user_email, name="login_user"),
    url(r"user/forgot_password/$", forgot_password, name="forgot_password"),
    url(
        r"^user/set_password/(?P<user_id>[0-9]+)/(?P<passwd>[a-zA-Z0-9]+)/$",
        set_password,
        name="set_password",
    ),
    url(
        r"^user/activation/(?P<user_id>[a-zA-Z0-9]+)/$",
        user_activation,
        name="user_activation",
    ),
    url(r"^user/reg_success/$", user_reg_success, name="user_reg_success"),
    url(r"^social/user/update/$", user_reg_success, name="social_user"),
    url(r"^recruiters/page/(?P<page_num>[0-9]+)/$", recruiters),
    url(
        r"^recruiters/(?P<recruiter_name>[a-zA-Z0-9_-]+.*?)/(?P<page_num>[0-9]+)/$",
        recruiter_profile,
    ),
    url(
        r"^recruiters/(?P<recruiter_name>[a-zA-Z0-9_-]+.*?)/$",
        recruiter_profile,
        name="recruiter_profile",
    ),
    url(
        r"^(?P<job_type>[-\w]+)-jobs-by-skills/$",
        fresher_jobs_by_skills,
        name="fresher_jobs_by_skills",
    ),
    url(
        r"^(?P<job_type>[-\w]+)-by-location/$",
        jobs_by_location,
        name="jobs_by_location",
    ),
    url(r"^jobs-by-skill/$", jobs_by_skill, name="jobs_by_skill"),
    url(r"^jobs-by-industry/$", jobs_by_industry, name="jobs_by_industry"),
    url(r"^jobs-by-degree/$", jobs_by_degree, name="jobs_by_degree"),
    url(r"^full-time-jobs/$", full_time_jobs, name="full_time_jobs"),
    url(r"^full-time-jobs/(?P<page_num>[0-9]+)/$", full_time_jobs),
    url(r"^walkin-jobs/$", walkin_jobs, name="walkin_jobs"),
    url(r"^walkin-jobs/(?P<page_num>[0-9]+)/$", walkin_jobs),
    url(r"^internship-jobs/$", internship_jobs, name="internship_jobs"),
    url(r"^internship-jobs/(?P<page_num>[0-9]+)/$", internship_jobs),
    url(r"^government-jobs/$", government_jobs, name="government_jobs"),
    url(r"^government-jobs/(?P<page_num>[0-9]+)/$", government_jobs),
    url(
        r"^assessment/question/view/(?P<que_id>[0-9]+)/$",
        question_view,
        name="question_view",
    ),
    url(
        r"^assessment-questions/$", assessments_questions, name="assessments_questions"
    ),
    url(r"^assessment-questions/(?P<page_num>[0-9]+)/$", assessments_questions),
    url(r"^assessment-changes/$", assessment_changes),
    url(r"^sitemap.xml$", sitemap_xml, name="sitemap_xml"),
    # url(r"^login/$", users_login, name="users_login"),
    url(r"^contact/$", contact, name="contact"),
    url(
        r"^unsubscribe/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$",
        unsubscribe,
        name="unsubscribe",
    ),
    url(r"^sitemap/$", sitemap, name="sitemap"),
    url(r"^sitemap/(?P<page_num>[0-9]+)/$", sitemap, name="sitemap"),
    url(r"^logout/$", get_out, name="get_out"),
    url(
        r"^(?P<company_name>[-\w]+)-job-openings/(?P<page_num>[0-9]+)/$",
        each_company_jobs,
    ),
    url(
        r"^(?P<company_name>[-\w]+)-job-openings/$",
        each_company_jobs,
        name="company_jobs",
    ),
    url(
        r"^(?P<industry>[-\w]+)-industry-jobs/$", job_industries, name="job_industries"
    ),
    url(r"^(?P<industry>[-\w]+)-industry-jobs/(?P<page_num>[0-9]+)/$", job_industries),
    url(r"^jobs-for-(?P<industry>[-\w]+)-industry/$", job_industries),
    url(
        r"^jobs-for-(?P<industry>[-\w]+)-industry/(?P<page_num>[0-9]+)/$",
        job_industries,
    ),
    url(r"^(?P<skill>[a-z0-9-.*?]+)-jobs/$", job_skills, name="job_skills"),
    url(r"^(?P<skill>[a-z0-9-.*?]+)-jobs/(?P<page_num>[0-9]+)/$", job_skills),
    url(r"^page/(?P<page_name>([a-z0-9-])+)/$", pages, name="pages"),
    url(r"^companies/(?P<page_num>[0-9]+)/$", companies),
    url(r"companies/$", companies, name="companies"),
    url(r"^", include("candidate.urls", namespace="my")),
    url(
        r"jobposts/year/(?P<year>\w{0,})/month/(?P<month>\w{0,})/date/(?P<date>\w{0,})/$",
        jobposts_by_date,
        name="jobposts_by_date",
    ),
    url(
        r"jobposts/year/(?P<year>\w{0,})/month/(?P<month>\w{0,})/date/(?P<date>\w{0,})/(?P<page_num>[0-9]+)/$",
        jobposts_by_date,
    ),
    # url(
    #     r"calendar/(?P<year>\w{0,})/month/(?P<month>\w{0,})/week/(?P<week>\w{0,})/$",
    #     week_calendar,
    #     name="week_calendar",
    # ),
    url(r"tickets/", include("tickets.urls", namespace="tickets")),
    url(r"^jobs-in-(?P<location>[-\w]+)/$", job_locations, name="job_locations"),
    url(r"^jobs-in-(?P<location>[-\w]+)/(?P<page_num>[0-9]+)/$", job_locations),
    url(r"^jobs-for-(?P<skill>[-\w]+)/$", job_skills),
    # url(r"calendar/(?P<year>\w{0,})/$", year_calendar, name="year_calendar"),
    # url(r"calendar/add/event/$", calendar_add_event, name="calendar_add_event"),
    # url(r"calendar/event/list/$", calendar_event_list, name="calendar_event_list"),
    # url(
    #     r"calendar/(?P<year>\w{0,})/month/(?P<month>\w{0,})/$",
    #     month_calendar,
    #     name="month_calendar",
    # ),
    url(r"^oauth2callback/$", auth_return, name="auth_return"),
    url(r"recruiters/$", recruiters, name="recruiters"),
    url(r"^jobs/$", job_list, name="job_list"),
    url(r"^jobs/", include("pjob.urls", namespace="jobs")),
    url(r"user_subscribe/$", user_subscribe, name="user_subscribe"),
    url(
        r"^(?P<obj_type>([a-z0-9-])+)/verification/(?P<obj_id>[a-zA-Z0-9_-]+.*?)/$",
        alert_subscribe_verification,
        name="alert_subscribe_verification",
    ),
    url(r"^process-email/$", process_email, name="process_email"),
    # url(r'^dj-rest-auth/', include('dj_rest_auth.urls')),
    url(r"^api-recruiter/", include("recruiter.api_urls", namespace="api_recruiter")),
    url(r"^celery-check/", include("mp_celery_monitor.urls", namespace="celery-check"))
]

handler404 = custom_404
handler500 = custom_500

# if settings.DEBUG:
#     # url(r'^profiler/', include('django_web_profiler.urls', namespace="django_web_profiler")),

#     import debug_toolbar

#     urlpatterns.append(url(r"^__debug__/", include(debug_toolbar.urls)))

# urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]

# if settings.DEBUG is False:   # if DEBUG is True it will be served automatically
#     urlpatterns += [
#         url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
#     ]
