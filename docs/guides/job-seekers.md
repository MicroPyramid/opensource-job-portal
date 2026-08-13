# For Job Seekers

## Finding jobs

You do not need an account to search or browse.

### Search

`/jobs/` is the main listing, with keyword search plus filters for location,
skill, industry and job type.

Search understands more than exact substrings:

- **Word order does not matter.** `python developer` finds "Developer —
  Python".
- **Related word forms match.** `manager` also finds "managing" and
  "management".
- **Typos usually still work.** `pyhton` finds Python jobs.
- **Whole words, not fragments.** `java` returns Java jobs, not JavaScript
  ones.

Quoting a phrase and excluding a term with `-` work as in a normal search box.

### Browsing

Jobs are also reachable through readable URLs, which is usually faster than
filtering:

| Browse by | URL |
| --- | --- |
| Skill | `/python-jobs/` |
| Skill and city | `/python-jobs-in-bangalore/` |
| City | `/jobs-in-chennai/` |
| Industry | `/finance-industry-jobs/` |
| Company | `/acme-job-openings/` |
| Fresher roles | `/fresher-jobs-in-hyderabad/` |
| Internships | `/internship-jobs/` |
| Walk-ins | `/walkin-jobs/`, `/python-walkins/` |
| Government | `/government-jobs/` |
| Full time | `/full-time-jobs/` |

Index pages at `/jobs-by-skill/`, `/jobs-by-industry/` and `/jobs-by-degree/`
list everything available.

## Your account

Register at `/register/`, or sign in with Google. Email addresses need
confirming — check for a verification message before trying to log in.

`/profile/` holds your details: contact information, skills, education,
employment history and resume. Recruiters see this when you apply, and it is
what profile-matched job alerts are based on, so an incomplete profile means
fewer relevant matches.

## Applying

Open a job and use the apply action. You need to be signed in; applications are
submitted against your profile, so keep the resume current.

`/applications/` tracks everything you have applied to and its current status.

`/saved/` holds jobs you have bookmarked to apply to later.

## Job alerts

`/job-alerts/` creates a saved search that emails you when matching jobs are
posted. You can also subscribe without a full account.

Alerts need email confirmation. Every alert email carries an unsubscribe link,
and `/unsubscribe/` stops them without deleting your account.

!!! warning "Alert emails may not arrive"

    On a default PeelJobs install the Celery tasks that deliver saved-search
    and subscriber alerts are **disabled in the source**. You can create and
    confirm an alert and still never receive one.

    Profile-matched alerts (`job_alerts_to_users`) do work. Whether any of it
    is running is up to whoever operates your site — see
    [Background Jobs](../architecture/background-jobs.md).

## Other pages

| Page | URL |
| --- | --- |
| Companies | `/companies/` |
| Recruiters | `/recruiters/` |
| Help | `/help/` |
| Contact | `/contact/` |
| About | `/about/` |
| Privacy | `/privacy/` |
| Terms | `/terms/` |
