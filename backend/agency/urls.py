"""
Agency URL Configuration

NOTE: Most recruiter functionality has been migrated to SvelteKit + REST API.
The agency app is deprecated and should be migrated or removed.

For now, this file contains minimal URLs to prevent import errors.
"""
from django.urls import re_path as url
from django.views.generic import RedirectView

from recruiter.views import (
    how_it_works,
)

from .views import (
    dashboard,
    hired_candidates,
    jobs_billing_process,
    client_list,
    add_client,
    edit_client,
    delete_client,
    client_profile,
    add_branch,
    add_contract_deatils,
    applicant_status_change,
    user_work_log,
    delete_applicant_status,
    delete_resume,
    view_resumes,
    job_status_change,
)

app_name = "agency"

urlpatterns = [
    # Redirect to recruiter SvelteKit dashboard
    url(r"^$", RedirectView.as_view(url="http://localhost:5174/dashboard", permanent=False), name="index"),
    url(r"^dashboard/$", dashboard, name="dashboard"),
    url(r"^how-it-works/$", how_it_works, name="how_it_works"),

    # Agency-specific features (client management, billing)
    url(r"^work-log/$", user_work_log, name="user_work_log"),
    url(
        r"^job/hired-candidates/(?P<job_post_id>[a-zA-Z0-9]+)/$",
        hired_candidates,
        name="hired_candidates",
    ),
    url(
        r"^job/billing/(?P<job_post_id>[a-zA-Z0-9]+)/$",
        jobs_billing_process,
        name="jobs_billing_process",
    ),
    url(
        r"^job/resumes/(?P<job_post_id>[a-zA-Z0-9]+)/$",
        view_resumes,
        name="view_resumes",
    ),
    url(
        r"^job/status/(?P<job_post_id>[a-zA-Z0-9]+)/$",
        job_status_change,
        name="job_status_change",
    ),
    url(r"^clients/$", client_list, name="client_list"),
    url(r"^clients/add/$", add_client, name="add_client"),
    url(
        r"^clients/edit/(?P<client_id>[a-zA-Z0-9]+)/$", edit_client, name="edit_client"
    ),
    url(
        r"^clients/delete/(?P<client_id>[a-zA-Z0-9]+)/$",
        delete_client,
        name="delete_client",
    ),
    url(
        r"^clients/profile/(?P<client_id>[a-zA-Z0-9]+)/$",
        client_profile,
        name="client_profile",
    ),
    url(
        r"^clients/branch/(?P<branch_id>[a-zA-Z0-9]+)/$", add_branch, name="add_branch"
    ),
    url(
        r"^clients/contract-details/(?P<contact_details_id>[a-zA-Z0-9]+)/$",
        add_contract_deatils,
        name="add_contract_deatils",
    ),
    url(
        r"^applicant/status/(?P<applicant_id>[a-zA-Z0-9]+)/$",
        applicant_status_change,
        name="applicant_status_change",
    ),
    url(
        r"^applicant/delete/(?P<applicant_id>[a-zA-Z0-9]+)/$",
        delete_applicant_status,
        name="delete_applicant_status",
    ),
    url(
        r"^resume/delete/(?P<resume_id>[a-zA-Z0-9]+)/$",
        delete_resume,
        name="delete_resume",
    ),
]
