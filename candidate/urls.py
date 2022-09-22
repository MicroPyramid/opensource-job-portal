from django.urls import re_path as url 
from .views import (
    index,
    upload_resume,
    upload_profilepic,
    profile,
    edit_personalinfo,
    edit_profile_description,
    edit_professionalinfo,
    add_language,
    edit_language,
    delete_language,
    add_experience,
    edit_experience,
    delete_experience,
    add_education,
    edit_education,
    delete_education,
    add_technicalskill,
    edit_technicalskill,
    delete_technicalskill,
    add_project,
    edit_project,
    delete_project,
    edit_email,
    job_alert,
    job_alert_results,
    modify_job_alert,
    alerts_list,
    delete_job_alert,
    edit_emailnotifications,
    delete_resume,
    user_password_change,
    messages,
)

app_name = "candidate"

urlpatterns = [
    # url(r'^home/$','home'),
    url(r"^$", index, name="index"),
    url(r"^profile/$", profile, name="profile"),
    url(r"personalinfo/edit/$", edit_personalinfo, name="edit_personalinfo"),
    url(
        r"profile_description/edit/$",
        edit_profile_description,
        name="edit_profile_description",
    ),
    url(r"email/edit/$", edit_email, name="edit_email"),
    url(
        r"professionalinfo/edit/$", edit_professionalinfo, name="edit_professionalinfo"
    ),
    # mobile verify
    # url(r'^mobile/verify/$', verify_mobile, name="verify_mobile"),
    # url(r'^send/mobile_verification_code/$', send_mobile_verification_code, name="send_mobile_verification_code"),
    # language urls
    url(r"language/add/$", add_language, name="add_language"),
    url(
        r"language/edit/(?P<language_id>[a-zA-Z0-9_-]+)/$",
        edit_language,
        name="edit_language",
    ),
    url(
        r"language/delete/(?P<language_id>[a-zA-Z0-9_-]+)/$",
        delete_language,
        name="delete_language",
    ),
    # experience urls
    url(r"experience/add/$", add_experience, name="add_experience"),
    url(
        r"experience/edit/(?P<experience_id>[a-zA-Z0-9_-]+)/$",
        edit_experience,
        name="edit_experience",
    ),
    url(
        r"experience/delete/(?P<experience_id>[a-zA-Z0-9_-]+)/$",
        delete_experience,
        name="delete_experience",
    ),
    # education urls
    url(r"education/add/$", add_education, name="add_education"),
    url(
        r"education/edit/(?P<education_id>[a-zA-Z0-9_-]+)/$",
        edit_education,
        name="edit_education",
    ),
    url(
        r"education/delete/(?P<education_id>[a-zA-Z0-9_-]+)/$",
        delete_education,
        name="delete_education",
    ),
    # techskill urls
    url(r"technicalskill/add/$", add_technicalskill, name="add_technicalskill"),
    url(
        r"technicalskill/edit/(?P<technical_skill_id>[a-zA-Z0-9_-]+)/$",
        edit_technicalskill,
        name="edit_technicalskill",
    ),
    url(
        r"technicalskill/delete/(?P<technical_skill_id>[a-zA-Z0-9_-]+)/$",
        delete_technicalskill,
        name="delete_technicalskill",
    ),
    # project urls
    url(r"project/add/$", add_project, name="add_project"),
    url(
        r"project/edit/(?P<project_id>[a-zA-Z0-9_-]+)/$",
        edit_project,
        name="edit_project",
    ),
    url(
        r"project/delete/(?P<project_id>[a-zA-Z0-9_-]+)/$",
        delete_project,
        name="delete_project",
    ),
    # resume urls
    url(r"upload_resume/$", upload_resume, name="upload_resume"),
    url(r"delete-resume/$", delete_resume, name="delete_resume"),
    url(r"upload_profilepic/$", upload_profilepic, name="upload_profilepic"),
    url(
        r"edit_emailnotifications/$",
        edit_emailnotifications,
        name="edit_emailnotifications",
    ),
    # job alert
    url(r"^alert/create/$", job_alert, name="job_alert"),
    url(r"^alert/list/$", alerts_list, name="alerts_list"),
    url(r"^alert/list/(?P<page_num>[-\w]+)/$", alerts_list),
    url(
        r"^alert/results/(?P<job_alert_id>[a-zA-Z0-9_-]+)/$",
        job_alert_results,
        name="job_alert_results",
    ),
    url(
        r"^alert/modify/(?P<job_alert_id>[a-zA-Z0-9_-]+)/$",
        modify_job_alert,
        name="modify_job_alert",
    ),
    url(
        r"^alert/delete/(?P<job_alert_id>[a-zA-Z0-9_-]+)/$",
        delete_job_alert,
        name="delete_job_alert",
    ),
    url(r"user/password/change/", user_password_change, name="user_password_change"),
    url(r"^messages/$", messages, name="messages"),
]
