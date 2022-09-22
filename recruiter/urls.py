from django.urls import re_path as url 

from recruiter.views import (
    index,
    getout,
    registration_success,
    how_it_works,
    dashboard,
    jobs_list,
    inactive_jobs,
    new_job,
    copy_job,
)
from recruiter.views import (
    edit_job,
    view_job,
    preview_job,
    deactivate_job,
    enable_job,
    delete_job,
    applicants,
    multiple_resume_upload,
)
from recruiter.views import (
    new_user,
    user_password_reset,
    change_password,
    user_profile,
    facebook_login,
    linkedin_login,
    resume_view,
)
from recruiter.views import (
    verify_mobile,
    send_mobile_verification_code,
    edit_profile,
    account_activation,
    twitter_login,
    resume_edit,
)
from recruiter.views import (
    view_company,
    edit_company,
    upload_profilepic,
    company_recruiter_list,
    messages,
    resume_upload,
    resume_pool,
    google_connect,
)
from recruiter.views import (
    add_menu,
    edit_menu,
    delete_menu,
    menu_status,
    menu_order,
    interview_location,
    enable_email_notifications,
    google_login,
)
from recruiter.views import (
    company_recruiter_create,
    edit_company_recruiter,
    delete_company_recruiter,
    activate_company_recruiter,
    company_recruiter_profile,
    download_applicants,
)

app_name = "recruiter"

urlpatterns = [
    url(r"^$", index, name="index"),
    url(r"^out/$", getout, name="getout"),
    url(r"^thank-you-message/$", registration_success, name="registration_success"),
    url(r"^how-it-works/$", how_it_works, name="how_it_works"),
    url(r"^dashboard/$", dashboard, name="dashboard"),
    url(r"^job/list/$", jobs_list, name="list"),
    url(r"^job/inactive/list/$", inactive_jobs, name="inactive_jobs"),
    url(r"^job/(?P<status>[-\w]+)/new/$", new_job, name="new"),
    url(r"^job/(?P<status>[-\w]+)/copy/$", copy_job, name="copy"),
    url(r"^job/edit/(?P<job_post_id>[a-zA-Z0-9]+)/$", edit_job, name="edit"),
    url(r"^job/view/(?P<job_post_id>[a-zA-Z0-9]+)/$", view_job, name="view"),
    url(r"^job/preview/(?P<job_post_id>[a-zA-Z0-9]+)/$", preview_job, name="preview"),
    url(
        r"^job/deactivate/(?P<job_post_id>[a-zA-Z0-9]+)/$",
        deactivate_job,
        name="deactivate_job",
    ),
    url(r"^job/enable/(?P<job_post_id>[a-zA-Z0-9]+)/$", enable_job, name="enable"),
    url(r"^job/delete/(?P<job_post_id>[a-zA-Z0-9]+)/$", delete_job, name="delete"),
    url(
        r"^job/applicants/(?P<job_post_id>[a-zA-Z0-9]+)/$",
        applicants,
        name="applicants",
    ),
    url(
        r"^job/enable-email-notifications/(?P<job_post_id>[a-zA-Z0-9]+)/$",
        enable_email_notifications,
        name="enable_email_notifications",
    ),
    url(r"^login/$", new_user, name="new_user"),
    url(r"^pwdreset/$", user_password_reset, name="user_password_reset"),
    url(r"^change-password/$", change_password, name="change_password"),
    url(r"^profile/$", user_profile, name="profile"),
    url(r"^mobile/verify/$", verify_mobile, name="verify_mobile"),
    url(
        r"^send/mobile_verification_code/$",
        send_mobile_verification_code,
        name="send_mobile_verification_code",
    ),
    url(r"^profile/edit/$", edit_profile, name="edit_profile"),
    url(
        r"^activation/(?P<user_id>[a-zA-Z0-9]+)/$",
        account_activation,
        name="account_activation",
    ),
    url(r"^twitter_login/$", twitter_login, name="twitter_login"),
    url(r"^google_connect/$", google_connect, name="google_connect"),
    url(r"^google_login/$", google_login, name="google_login"),
    url(r"^facebook_login/$", facebook_login, name="facebook_login"),
    url(r"^linkedin_login/$", linkedin_login, name="linkedin_login"),
    url(r"^microsite-page/$", view_company, name="view_company"),
    url(r"^company/edit/$", edit_company, name="edit_company"),
    url(r"^company/profile-pic/$", upload_profilepic, name="upload_profilepic"),
    url(
        r"^company/recruiters/$", company_recruiter_list, name="company_recruiter_list"
    ),
    url(
        r"^company/recruiter/add/$",
        company_recruiter_create,
        name="company_recruiter_create",
    ),
    url(
        r"^company/recruiter/edit/(?P<recruiter_id>[a-zA-Z0-9]+)/$",
        edit_company_recruiter,
        name="edit_company_recruiter",
    ),
    url(
        r"^company/recruiter/delete/(?P<recruiter_id>[a-zA-Z0-9]+)/$",
        delete_company_recruiter,
        name="delete_company_recruiter",
    ),
    url(
        r"^company/recruiters/status/(?P<recruiter_id>[a-zA-Z0-9]+)/$",
        activate_company_recruiter,
        name="activate_company_recruiter",
    ),
    url(
        r"^company/recruiters/profile/(?P<recruiter_id>[a-zA-Z0-9]+)/$",
        company_recruiter_profile,
        name="company_recruiter_profile",
    ),
    url(r"^company/menu/add/$", add_menu, name="add_menu"),
    url(
        r"^download/(?P<jobpost_id>[0-9]+)/(?P<status>[a-zA-Z]+)/$",
        download_applicants,
        name="download_applicants",
    ),
    url(r"^company/menu/edit/(?P<menu_id>[a-zA-Z0-9]+)/$", edit_menu, name="edit_menu"),
    url(
        r"^company/menu/delete/(?P<menu_id>[a-zA-Z0-9]+)/$",
        delete_menu,
        name="delete_menu",
    ),
    url(
        r"^company/menu/status/(?P<menu_id>[a-zA-Z0-9]+)/$",
        menu_status,
        name="menu_status",
    ),
    url(r"^company/menu/order/$", menu_order, name="menu_order"),
    url(r"^messages/$", messages, name="messages"),
    url(r"^resume/pool/$", resume_pool, name="resume_pool"),
    url(r"^resume/upload/$", resume_upload, name="resume_upload"),
    url(
        r"^multiple/resumes/upload/$",
        multiple_resume_upload,
        name="multiple_resume_upload",
    ),
    url(r"^resume/view/(?P<resume_id>[a-zA-Z0-9]+)/$", resume_view, name="resume_view"),
    url(r"^resume/edit/(?P<resume_id>[a-zA-Z0-9]+)/$", resume_edit, name="resume_edit"),
    # mail templates
    # url(r'^mail-template/list/(?P<jobpost_id>[a-zA-Z0-9]+)/', emailtemplates, name="emailtemplates"),
    # url(r'^mail-template/new/(?P<jobpost_id>[a-zA-Z0-9]+)/', new_template, name="new_template"),
    # url(r'^mail-template/edit/(?P<jobpost_id>[a-zA-Z0-9]+)/(?P<template_id>[-\w]+)/', edit_template, name="edit_mailtemplate"),
    # url(r'^mail-template/view/(?P<template_id>[-\w]+)/', view_template, name="view_mailtemplate"),
    # url(r'^mail-template/delete/(?P<template_id>[-\w]+)/', delete_template, name="delete_mailtemplate"),
    # url(r'^send_mail/(?P<template_id>[-\w]+)/(?P<jobpost_id>[a-zA-Z0-9]+)/', send_mail, name="send_mail"),
    # view sent mails
    # url(r'^sent-mail/list/(?P<jobpost_id>[a-zA-Z0-9]+)/', sent_mails, name="sent_mails"),
    # url(r'^sent-mail/view/(?P<sent_mail_id>[-\w]+)/', view_sent_mail, name="view_sent_mail"),
    # url(r'^sent-mail/delete/(?P<sent_mail_id>[-\w]+)/', delete_sent_mail, name="delete_sent_mail"),
    url(
        r"^job/interview-location/(?P<location_count>[a-zA-Z0-9]+)/$",
        interview_location,
        name="interview_location",
    ),
]
