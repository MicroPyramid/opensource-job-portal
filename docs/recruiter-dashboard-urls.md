# Recruiter Dashboard URLs (Django)

Inventory of the Django URLs that serve the recruiter dashboard, as routed by
`backend/jobsp/urls.py`. One surface is left:

| Surface | Prefix | Included from | Status |
| --- | --- | --- | --- |
| Recruiter REST API v1 | `/api/v1/recruiter/` | `api/v1/recruiter/urls.py` | **Active** — consumed by `recruiter/` SvelteKit dashboard |

> `/dashboard/` (`dashboard/urls.py`) is the **platform-admin** dashboard
> (Super Admin / Support Staff), not the recruiter dashboard. It is out of scope
> for this document.

> **Updated 2026-08-13.** This document used to describe two further surfaces:
> the legacy recruiter pages at `/recruiter/` (8 routes, mostly `RedirectView`
> shims) and the legacy hybrid API at `/api-recruiter/` (17 routes). Both are
> **gone** — `git ls-files backend/recruiter` returns nothing and `jobsp/urls.py`
> includes neither prefix. Their inventories were removed rather than kept as
> history; `git show ad39524:recruiter/urls.py` and
> `git show ad39524:recruiter/api_urls.py` still have them if needed.
>
---

## Recruiter REST API v1 — `/api/v1/recruiter/`

Namespace: `api:v1:recruiter` (`backend/api/v1/recruiter/urls.py`)

Authentication is JWT via the `Authorization: Bearer <token>` header. The
SvelteKit server (never the browser) attaches the header. Permission column:
`AllowAny` = public, `Auth` = `IsAuthenticated`.

### Authentication — `auth_views.py`

| Method | URL | Name | View | Perm |
| --- | --- | --- | --- | --- |
| POST | `/api/v1/recruiter/auth/register/` | `register` | `register` | AllowAny |
| POST | `/api/v1/recruiter/auth/login/` | `login` | `login` | AllowAny |
| POST | `/api/v1/recruiter/auth/logout/` | `logout` | `logout` | AllowAny |
| POST | `/api/v1/recruiter/auth/verify-email/` | `verify-email` | `verify_email` | AllowAny |
| POST | `/api/v1/recruiter/auth/resend-verification/` | `resend-verification` | `resend_verification` | AllowAny |
| POST | `/api/v1/recruiter/auth/forgot-password/` | `forgot-password` | `forgot_password` | AllowAny |
| POST | `/api/v1/recruiter/auth/reset-password/` | `reset-password` | `reset_password` | AllowAny |
| POST | `/api/v1/recruiter/auth/change-password/` | `change-password` | `change_password` | Auth |
| POST | `/api/v1/recruiter/auth/accept-invitation/` | `accept-invitation` | `accept_invitation` | AllowAny |
| GET | `/api/v1/recruiter/auth/me/` | `me` | `me` | Auth |

### Google OAuth — `auth_views.py`

| Method | URL | Name | View | Perm |
| --- | --- | --- | --- | --- |
| GET | `/api/v1/recruiter/auth/google/url/` | `google-auth-url` | `google_auth_url` | AllowAny |
| POST | `/api/v1/recruiter/auth/google/callback/` | `google-callback` | `google_callback` | AllowAny |
| POST | `/api/v1/recruiter/auth/google/complete/` | `google-complete` | `google_complete` | AllowAny |

### Profile — `auth_views.py`

| Method | URL | Name | View | Perm |
| --- | --- | --- | --- | --- |
| PATCH | `/api/v1/recruiter/profile/update/` | `profile-update` | `update_profile` | Auth |
| POST | `/api/v1/recruiter/profile/picture/` | `profile-picture` | `upload_profile_picture` | Auth |

### Team management — `views.py`

| Method | URL | Name | View | Perm |
| --- | --- | --- | --- | --- |
| GET | `/api/v1/recruiter/team/` | `team-list` | `list_team_members` | Auth |
| GET | `/api/v1/recruiter/team/<user_id>/` | `team-detail` | `get_team_member` | Auth |
| PATCH | `/api/v1/recruiter/team/<user_id>/update/` | `team-update` | `update_team_member` | Auth |
| DELETE | `/api/v1/recruiter/team/<user_id>/remove/` | `team-remove` | `remove_team_member` | Auth |
| POST | `/api/v1/recruiter/team/<user_id>/toggle-status/` | `team-toggle-status` | `toggle_team_member_status` | Auth |
| POST | `/api/v1/recruiter/team/invite/` | `team-invite` | `invite_team_member` | Auth |
| GET | `/api/v1/recruiter/team/invitations/` | `invitations-list` | `list_invitations` | Auth |
| POST | `/api/v1/recruiter/team/invitations/<invitation_id>/resend/` | `invitation-resend` | `resend_invitation` | Auth |
| DELETE | `/api/v1/recruiter/team/invitations/<invitation_id>/cancel/` | `invitation-cancel` | `cancel_invitation` | Auth |

Team writes additionally gate on `is_company_admin(user)` inside the view.

### Jobs — `job_views.py`

| Method | URL | Name | View | Perm |
| --- | --- | --- | --- | --- |
| GET | `/api/v1/recruiter/jobs/` | `jobs-list` | `list_jobs` | Auth |
| POST | `/api/v1/recruiter/jobs/create/` | `jobs-create` | `create_job` | Auth |
| GET | `/api/v1/recruiter/jobs/<job_id>/` | `jobs-detail` | `get_job` | Auth |
| PATCH, PUT | `/api/v1/recruiter/jobs/<job_id>/update/` | `jobs-update` | `update_job` | Auth |
| DELETE | `/api/v1/recruiter/jobs/<job_id>/delete/` | `jobs-delete` | `delete_job` | Auth |
| POST | `/api/v1/recruiter/jobs/<job_id>/publish/` | `jobs-publish` | `publish_job` | Auth |
| POST | `/api/v1/recruiter/jobs/<job_id>/close/` | `jobs-close` | `close_job` | Auth |
| PATCH | `/api/v1/recruiter/jobs/<job_id>/notifications/` | `jobs-notifications` | `set_job_notifications` | Auth |
| GET | `/api/v1/recruiter/jobs/metadata/` | `jobs-metadata` | `get_job_form_metadata` | Auth |

> Route order note: `jobs/metadata/` is declared **before** `jobs/<int:job_id>/`,
> so it resolves correctly despite the overlap.

### Applicants — `job_views.py`

| Method | URL | Name | View | Perm |
| --- | --- | --- | --- | --- |
| GET | `/api/v1/recruiter/jobs/<job_id>/applicants/` | `jobs-applicants` | `get_job_applicants` | Auth |
| GET | `/api/v1/recruiter/jobs/<job_id>/applicants/<applicant_id>/` | `applicant-detail` | `get_applicant_detail` | Auth |
| PATCH | `/api/v1/recruiter/jobs/<job_id>/applicants/<applicant_id>/update/` | `applicant-update` | `update_applicant_status` | Auth |

### Dashboard stats & analytics — `job_views.py`, `analytics_views.py`

| Method | URL | Name | View | Perm |
| --- | --- | --- | --- | --- |
| GET | `/api/v1/recruiter/dashboard/stats/` | `dashboard-stats` | `job_views.get_dashboard_stats` | Auth |
| GET | `/api/v1/recruiter/analytics/applications/` | `application-analytics` | `analytics_views.get_application_analytics` | Auth |
| GET | `/api/v1/recruiter/jobs/<job_id>/analytics/` | `job-analytics` | `analytics_views.get_job_application_analytics` | Auth |

### Company profile — `views.py`

| Method | URL | Name | View | Perm |
| --- | --- | --- | --- | --- |
| GET | `/api/v1/recruiter/company/profile/` | `company-profile` | `get_company_profile` | Auth |
| PATCH | `/api/v1/recruiter/company/profile/update/` | `company-profile-update` | `update_company_profile` | Auth |

---

## Counts

| Surface | Routes |
| --- | --- |
| `/api/v1/recruiter/` | 41 |

Every one has a caller in `recruiter/src/`, and every API path the SvelteKit
app builds resolves to a route here — checked in both directions 2026-08-13.

## Scoping

Job, applicant and analytics views resolve their queryset through
`api/v1/recruiter/scoping.py`: a company admin sees every job posted by anyone
in their company, everyone else sees their own. Team endpoints gate separately
on `is_company_admin` inside the view.

## Source files

- `backend/jobsp/urls.py` — root URLconf
- `backend/api/v1/recruiter/urls.py` — REST API v1 routes
- `backend/api/v1/recruiter/{auth_views,job_views,analytics_views,views}.py` — views
- `backend/api/v1/recruiter/scoping.py` — who may see which jobs
