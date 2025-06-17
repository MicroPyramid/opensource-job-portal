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
    my_home,
    edit_personal_info,
)
from .views.my_views import (
    edit_job_preferences,
    edit_project_modal,
    add_project_modal,
    delete_project_modal,
    edit_language_modal,
    add_language_modal,
    delete_language_modal,
    edit_experience_modal,
    add_experience_modal,
    delete_experience_modal,
    test_experience_view,
    edit_education_modal,
    add_education_modal,
    delete_education_modal,
    add_skill_modal,
    edit_skill_modal,
    delete_skill_modal,
    edit_account_settings,
    add_certification_modal,
    edit_certification_modal,
    delete_certification_modal,
    upload_resume_modal,
    update_resume_modal,
    delete_resume_modal,
    get_resume_info,
    edit_basic_profile,
)

app_name = "candidate"

urlpatterns = [
    # url(r'^home/$','home'),
    url(r"^$", index, name="index"),
    url(r"^profile/$", profile, name="profile"),

    url(r"^my/home/$", my_home, name="my_home"),

    url(r"personalinfo/edit/$", edit_personalinfo, name="edit_personalinfo"),
    url(
        r"profile_description/edit/$",
        edit_profile_description,
        name="edit_profile_description",
    ),
    url(
        r"profile/personal_info/edit/$",
        edit_personal_info,
        name="edit_personal_info",
    ),
    url(
        r"profile/basic_profile/edit/$",
        edit_basic_profile,
        name="edit_basic_profile",
    ),
    url(
        r"job-preferences/edit/$",
        edit_job_preferences,
        name="edit_job_preferences",
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
    url(
        r"project/edit-modal/(?P<project_id>[a-zA-Z0-9_-]+)/$",
        edit_project_modal,
        name="edit_project_modal",
    ),
    url(
        r"project/add-modal/$",
        add_project_modal,
        name="add_project_modal",
    ),
    url(
        r"project/delete-modal/(?P<project_id>[a-zA-Z0-9_-]+)/$",
        delete_project_modal,
        name="delete_project_modal",
    ),
    # experience modal urls
    url(
        r"experience/edit-modal/(?P<experience_id>[a-zA-Z0-9_-]+)/$",
        edit_experience_modal,
        name="edit_experience_modal",
    ),
    url(
        r"experience/add-modal/$",
        add_experience_modal,
        name="add_experience_modal",
    ),
    url(
        r"experience/delete-modal/(?P<experience_id>[a-zA-Z0-9_-]+)/$",
        delete_experience_modal,
        name="delete_experience_modal",
    ),
    # language modal urls
    url(
        r"language/edit-modal/(?P<language_id>[a-zA-Z0-9_-]+)/$",
        edit_language_modal,
        name="edit_language_modal",
    ),
    url(
        r"language/add-modal/$",
        add_language_modal,
        name="add_language_modal",
    ),
    url(
        r"language/delete-modal/(?P<language_id>[a-zA-Z0-9_-]+)/$",
        delete_language_modal,
        name="delete_language_modal",
    ),
    # education modal urls
    url(
        r"education/edit-modal/(?P<education_id>[a-zA-Z0-9_-]+)/$",
        edit_education_modal,
        name="edit_education_modal",
    ),
    url(
        r"education/add-modal/$",
        add_education_modal,
        name="add_education_modal",
    ),
    url(
        r"education/delete-modal/(?P<education_id>[a-zA-Z0-9_-]+)/$",
        delete_education_modal,
        name="delete_education_modal",
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
    
    # skills modal urls
    url(
        r"skill/add-modal/$",
        add_skill_modal,
        name="add_skill_modal",
    ),
    url(
        r"skill/edit-modal/(?P<skill_id>[a-zA-Z0-9_-]+)/$",
        edit_skill_modal,
        name="edit_skill_modal",
    ),
    url(
        r"skill/delete-modal/(?P<skill_id>[a-zA-Z0-9_-]+)/$",
        delete_skill_modal,
        name="delete_skill_modal",
    ),
    
    # test url (temporary)
    url(r"test/experience/$", test_experience_view, name="test_experience_view"),
    
    # account settings
    url(
        r"account-settings/edit/$",
        edit_account_settings,
        name="edit_account_settings",
    ),
    
    # certification modal urls
    url(
        r"certification/add-modal/$",
        add_certification_modal,
        name="add_certification_modal",
    ),
    url(
        r"certification/edit-modal/(?P<certification_id>[a-zA-Z0-9_-]+)/$",
        edit_certification_modal,
        name="edit_certification_modal",
    ),
    url(
        r"certification/delete-modal/(?P<certification_id>[a-zA-Z0-9_-]+)/$",
        delete_certification_modal,
        name="delete_certification_modal",
    ),
    
    # resume modal urls
    url(
        r"resume/upload-modal/$",
        upload_resume_modal,
        name="upload_resume_modal",
    ),
    url(
        r"resume/update-modal/$",
        update_resume_modal,
        name="update_resume_modal",
    ),
    url(
        r"resume/delete-modal/$",
        delete_resume_modal,
        name="delete_resume_modal",
    ),
    url(
        r"resume/info/$",
        get_resume_info,
        name="get_resume_info",
    ),
]
