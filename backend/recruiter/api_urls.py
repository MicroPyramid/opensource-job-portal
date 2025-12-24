from django.urls import path, re_path
from recruiter import api_views


app_name = "api_recruiter"


urlpatterns = [
    path("login/", api_views.login_view, name="api_login"),
    path("out/", api_views.getout, name="getout"),
    path("change-password/", api_views.change_password, name="api_change_password"),
    path("profile/", api_views.user_profile, name="api_user_profile"),
    path("job/list/", api_views.jobs_list, name="api_list"),
    path("skill/list/", api_views.skill_list),
    path("industry/list/", api_views.industry_list),
    path("city/list/", api_views.city_list),
    path("state/list/", api_views.state_list),
    path("company/list/", api_views.company_list),
    path("functional-area/list/", api_views.functional_area_list),
    path("job/inactive/list/", api_views.inactive_jobs, name="api_inactive_jobs"),
    path("profile/edit/", api_views.edit_profile, name="edit_profile"),
    path("company-profile/", api_views.view_company, name="view_company"),
    re_path(r"^job/(?P<job_type>[-\w]+)/new/$", api_views.new_job, name="api_new_job"),
    re_path(
        r"^job/edit/(?P<job_post_id>[a-zA-Z0-9]+)/$",
        api_views.edit_job,
        name="api_edit_job",
    ),
    re_path(
        r"^job/delete/(?P<job_post_id>[a-zA-Z0-9]+)/$",
        api_views.delete_job,
        name="api_delete_job",
    ),
]
