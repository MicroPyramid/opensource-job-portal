# Background Jobs

Celery handles email notification, job alerts and scheduled reports, brokered
through Redis. Task definitions live in `backend/dashboard/tasks.py`; the
schedule is `CELERY_BEAT_SCHEDULE` in `backend/jobsp/settings.py`.

```bash
cd backend

# Worker — executes tasks
DJANGO_SETTINGS_MODULE=jobsp.settings_local \
  uv run celery -A jobsp worker --loglevel=info

# Beat — schedules them
DJANGO_SETTINGS_MODULE=jobsp.settings_local \
  uv run celery -A jobsp beat --loglevel=info
```

Both are needed: beat only enqueues, the worker only executes. The timezone is
`Asia/Calcutta`, so every schedule below is in IST.

!!! danger "Read this before relying on any scheduled email"

    **Six of the tasks in `dashboard/tasks.py` are disabled**, and one beat
    entry points at a task that does not exist. If you are self-hosting and
    expecting job alerts to go out, they will not. This is the current state of
    the source, not a misconfiguration you can fix with settings.

## Scheduled tasks

Nine beat entries are active:

| Schedule name | Task | When (IST) | State |
| --- | --- | --- | --- |
| `moving-published-jobs-to-live` | `jobpost_published` | every minute, Mon–Sat | **Disabled** |
| `sending-today-applied-users-info-to-recruiters` | `recruiter_jobpost_applicants` | 16:00, Mon–Sat | Working |
| `sending-daily-statistics-report-to-admins` | `daily_report` | 08:00, daily | Working |
| `sending-weekly-jobs-notifications-to-applicants` | `applicants_job_notifications` | 09:00, Mon | **Disabled** |
| `sending-profile-update-notifications-two-hours-after-registering` | `applicants_profile_update_notifications_two_hours` | every 2 hours | **Task does not exist** |
| `sending-today-live-jobs-to-users-based-on-profile` | `job_alerts_to_users` | 17:00, daily | Working |
| `sending-today-live-jobs-to-alerts` | `job_alerts_to_alerts` | 10:00, daily | **Disabled** |
| `sending-today-live-jobs-to-subscribers` | `job_alerts_to_subscribers` | 18:00, daily | **Disabled** |
| `check-expiring-jobs-and-send-notifications` | `check_expiring_jobs` | 09:00, daily | Working |

A further six entries are commented out in `settings.py`, including sitemap
generation — replaced by the Django sitemap framework — and walk-in
notifications.

## The disabled tasks

These six functions have a bare `return` as their first statement. The
implementation is still there, underneath, unreachable:

| Task | Line |
| --- | --- |
| `job_alerts_to_subscribers` | 145 |
| `job_alerts_to_alerts` | 181 |
| `jobpost_published` | 219 |
| `applicants_profile_update_notifications` | 684 |
| `applicants_all_job_notifications` | 772 |
| `applicants_job_notifications` | 788 |

They were short-circuited in a single commit that removed Facebook posting.
Rather than untangle the Facebook calls from each task body, the tasks were
disabled wholesale — and never re-enabled.

Consequences worth knowing:

- **Job alerts do not send.** `job_alerts_to_alerts` and
  `job_alerts_to_subscribers` are the two delivery paths for saved alerts and
  subscriptions. Users can subscribe and confirm their address, and nothing
  will ever arrive.
- **Weekly job digests do not send.**
- **`jobpost_published` is harmless.** It promoted `Published` to `Live`, but
  the recruiter API creates jobs as `Draft` and publishing sets `Live`
  directly, so nothing writes `Published` any more. Its schedule is also
  `crontab(minute="*")` — every minute, not the "5:00 PM" its comment claims —
  which would matter if it did anything.

## The missing task

`sending-profile-update-notifications-two-hours-after-registering` schedules
`dashboard.tasks.applicants_profile_update_notifications_two_hours`. No function
by that name exists in `dashboard/tasks.py`. Beat enqueues it every two hours
and the worker raises `NotRegistered` each time.

The similarly-named `applicants_profile_update_notifications` does exist — and
is one of the six disabled tasks.

## Working tasks

| Task | Does |
| --- | --- |
| `recruiter_jobpost_applicants` | Daily digest of new applicants, to recruiters |
| `daily_report` | Platform statistics to admins in `SUPPORT_EMAILS` |
| `job_alerts_to_users` | Live jobs matched to job seeker profiles |
| `check_expiring_jobs` | Warns recruiters about jobs nearing expiry |

## Email in development

`settings_local` uses Django's console email backend, so locally-triggered mail
prints to the terminal running Django rather than being sent. Production uses
Amazon SES.

!!! warning "Before re-enabling anything on a real deployment"

    These tasks mail the entire subscriber base. On a production database that
    is a large, irreversible send to addresses that may not have heard from the
    platform in a long time. Re-enable against a test address first, and leave
    the beat entries commented until you have confirmed the recipient set.
