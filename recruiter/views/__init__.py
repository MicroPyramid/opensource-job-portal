# Import aggregator for backward compatibility
# This ensures existing imports continue to work after the reorganization

# Job Management Views
from .job_management import (
    jobs_list,
    inactive_jobs,
    new_job,
    edit_job,
    copy_job,
    view_job,
    preview_job,
    deactivate_job,
    delete_job,
    enable_job,
)

# Job Helper Functions
from .job_helpers import (
    add_other_skills,
    add_other_qualifications,
    add_other_functional_area,
    adding_keywords,
    add_interview_location,
    add_other_locations,
    set_other_fields,
    adding_other_fields_data,
    save_job_post,
    checking_error_value,
    retreving_form_errors,
)

# Application Management Views
from .applications import (
    applicants,
)

# Authentication Views
from .authentication import (
    index,
    new_user,
    account_activation,
    user_password_reset,
    change_password,
    verify_mobile,
    send_mobile_verification_code,
    google_login,
    google_connect,
    facebook_login,
)

# Profile Management Views
from .profile_management import (
    user_profile,
    edit_profile,
    upload_profilepic,
    view_company,
    edit_company,
)

# Communication Views
from .communication import (
    new_template,
    edit_template,
    emailtemplates,
    view_template,
    delete_template,
    send_mail,
    sent_mails,
    view_sent_mail,
    delete_sent_mail,
    enable_email_notifications,
    messages,
)

# Company Management Views
from .company_management import (
    company_recruiter_list,
    company_recruiter_create,
    edit_company_recruiter,
    activate_company_recruiter,
    delete_company_recruiter,
    company_recruiter_profile,
    add_menu,
    menu_status,
    delete_menu,
    edit_menu,
    menu_order,
)

# Resume Management Views
from .resume_management import (
    resume_upload,
    multiple_resume_upload,
    resume_pool,
    resume_view,
    resume_edit,
    download_applicants,
)

# Dashboard and Utility Views
from .dashboard import (
    dashboard,
    how_it_works,
    interview_location,
    create_slug,
    get_autocomplete,
)
