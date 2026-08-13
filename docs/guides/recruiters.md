# For Recruiters

The recruiter dashboard is a separate application from the job seeker site,
usually on its own domain or port.

## Getting an account

Sign up at `/signup/`, or with Google. Confirm your address at
`/verify-email/`, then complete onboarding, which collects your company
details.

Two kinds of recruiter account:

| Type | Meaning |
| --- | --- |
| **Company Admin** | Owns the company profile and can manage team members |
| **Recruiter** | Belongs to a company, manages their own postings |

There is also an independent recruiter with no company attached.

The first person to register a company becomes its admin; everyone added later
is a recruiter.

## Posting a job

`/dashboard/jobs/new/`. You will need the title, description, required skills,
location, job type, experience range and salary.

Job types include full time, permanent, contract, internship, part time,
freelance, walk-in, government and fresher. Walk-in and government postings ask
for extra fields — walk-in dates and venue, or government notification details.

Fill in skills and location carefully. They are what job seekers filter on and
what drives the SEO-friendly listing pages, so a posting missing them is much
harder to find.

`/dashboard/jobs/[id]/preview/` shows the posting as a job seeker will see it.

### Draft, then publish

New jobs are created as **Draft**. Publishing moves them to **Live**.

!!! warning "Only Draft jobs can be edited"

    Once a job is Live or Disabled, the edit endpoint refuses changes. To
    correct a Live posting you disable it and create a new one.

    Plan for this: preview before publishing, because publishing is effectively
    final.

Depending on how your site is configured, new postings may enter a **Pending**
state for moderation before going live.

## Managing jobs

| Page | Purpose |
| --- | --- |
| `/dashboard/jobs/` | All your active postings |
| `/dashboard/jobs/inactive/` | Disabled and expired postings |
| `/dashboard/jobs/[id]/` | A single posting |
| `/dashboard/jobs/[id]/edit/` | Edit — Draft only |
| `/dashboard/jobs/[id]/preview/` | Job seeker's view |

Job statuses you will see:

| Status | Meaning |
| --- | --- |
| Draft | Not submitted |
| Pending | Awaiting moderation |
| Live | Publicly visible |
| Disabled | Withdrawn by you or an admin |
| Expired | Past its closing date |
| Hired | Filled |

## Applicants

`/dashboard/jobs/[id]/applicants/` lists everyone who applied, with their
profile, skills, experience and resume. From here you move candidates through
shortlisting, hiring and rejection.

`/dashboard/jobs/[id]/applicants/download/` exports the list.

If enabled on your site, a daily digest of new applicants is emailed at 16:00
IST.

## Company and team

`/dashboard/company/` holds the company profile — description, industry, size,
location and logo. This is public: job seekers see it at
`/{company}-job-openings/`.

`/dashboard/team/` manages recruiters, for Company Admins only. Added members
can post under the company but cannot edit each other's postings.

`/dashboard/account/` is your own login, password and notification settings.

## Analytics

`/dashboard/analytics/` reports posting performance and application volume.
