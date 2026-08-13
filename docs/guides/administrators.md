# For Administrators

Platform staff — as distinct from recruiters — moderate content and maintain
reference data.

Two separate interfaces:

| Interface | URL | Use |
| --- | --- | --- |
| **Platform dashboard** | `/dashboard/` | Day-to-day moderation and operations |
| **Django admin** | `/admin/` | Raw model access, for when the dashboard cannot express it |

Access requires a staff account (`is_staff`), created with
`manage.py createsuperuser` or promoted from an existing user.

!!! note "The dashboard is server-rendered Django"

    Unlike the job seeker and recruiter apps, the platform dashboard is still
    rendered from Django templates. It is the largest remaining part of the
    original application and is slated for replacement — see
    [Backend](../architecture/backend.md#what-is-legacy).

## Job moderation

`/dashboard/jobpost/{type}/list/` lists postings by status.

| Action | URL |
| --- | --- |
| View | `/dashboard/jobpost/view/{id}/` |
| Preview as a job seeker | `/dashboard/jobpost/preview/{id}/` |
| Publish | `/dashboard/jobpost/publish/{id}/` |
| Change status | `/dashboard/jobpost/status_change/{id}/` |
| Disable | `/dashboard/jobpost/deactivate/{id}/` |
| Re-enable | `/dashboard/jobpost/enable/{id}/` |
| Delete | `/dashboard/jobpost/delete/{id}/` |
| Edit | `/dashboard/jobpost/edit/{id}/` |
| Edit title only | `/dashboard/jobpost/title/edit/{id}/` |
| Email the recruiter | `/dashboard/jobpost/mail_to_recruiter/{id}/` |

Postings in **Pending** are the moderation queue. Disabling is reversible;
deleting is not.

## Users

| Area | URL |
| --- | --- |
| All users | `/dashboard/users/list/` |
| Create | `/dashboard/users/new-user/` |
| Edit / view / delete | `/dashboard/users/{action}/{id}/` |

### Recruiters

`/dashboard/recruiters/{status}/list/` filters by status.

| Action | URL |
| --- | --- |
| View | `/dashboard/recruiter/view/{id}/` |
| Activate / deactivate | `/dashboard/recruiter/status/{id}/` |
| Set paid status | `/dashboard/recruiter/paid-status/{id}/` |
| Remove | `/dashboard/recruiter/remove/{id}/` |

### Applicants

`/dashboard/applicants/list/`, filterable by status, with per-applicant views
and actions.

## Reference data

The pickers job seekers and recruiters use. Keeping these clean matters:
duplicated or misspelled skills fragment search results and produce near-empty
landing pages.

| Data | URL |
| --- | --- |
| Skills | `/dashboard/technical_skills/` |
| Industries | `/dashboard/industries/` |
| Qualifications | `/dashboard/qualifications/` |
| Functional areas | `/dashboard/functional_area/` |
| Languages | `/dashboard/languages/` |
| Countries | `/dashboard/country/` |
| Locations | `/dashboard/{status}/locations/` |

Most support enable/disable as well as delete. Prefer disabling — deleting a
skill that jobs reference is destructive.

The initial set comes from `manage.py load_initial_data`; see
[Test Data](../getting-started/test-data.md).

## Email

| Area | URL |
| --- | --- |
| Templates | `/dashboard/mail-template/list/` |
| Send from a template | `/dashboard/send_mail/{id}/` |
| Sent history | `/dashboard/sent-mail/list/` |
| Applicant mails | `/dashboard/applicants-mails/` |

## Subscribers and search logs

`/dashboard/subscribers/list/` shows alert subscribers.
`/dashboard/search-log/list/` and `/dashboard/search/{type}/summary/` report
what visitors searched for — useful for spotting skills worth adding.

## Operations

- **Daily statistics** are emailed at 08:00 IST to the addresses in
  `SUPPORT_EMAILS`.
- **Expiring job warnings** go out at 09:00 IST.
- **Several notification tasks are disabled in the source.** Before promising
  anyone an email, check
  [Background Jobs](../architecture/background-jobs.md).
- **Support tickets** live at `/tickets/`.
