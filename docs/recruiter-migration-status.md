# Recruiter migration status: Django → SvelteKit + DRF

Audit of the legacy Django recruiter app against what exists today in
`recruiter/` (SvelteKit) and `backend/api/v1/recruiter/` (DRF).

**Baseline** — the pre-migration URLconf, recovered from git:
`git show ad39524:recruiter/urls.py`, which names **52 live routes**.

> **Baseline corrected 2026-08-13.** Earlier passes said 61. The URLconf does
> contain 61 `name=` occurrences, but nine of them are the mail-template and
> sent-mail routes, which were **already commented out** at that commit — dead
> before the migration started, so they were never the migration's to carry.
> Counts below reconcile to 52. Earlier passes used 53, then 61; this is the
> first that separated live routes from commented ones.

> **Re-audit 2026-08-12 (third pass).** Verified by matching every API path the
> SvelteKit app calls against `api/v1/recruiter/urls.py` in both directions.
> Forward direction is clean. The *reverse* direction found two mis-credited
> routes: `change_password` and `google_login` had working DRF endpoints that
> no UI called. Both since wired — see
> [API built, UI missing](#api-built-ui-missing--found-on-third-pass).

## Headline

> **Django app deleted 2026-08-13.** `backend/recruiter/` no longer exists —
> `git ls-files backend/recruiter` returns nothing, and `jobsp/urls.py` includes
> neither `/recruiter/` nor `/api-recruiter/`. The three redirect shims went with
> the templates that reversed their names. What survives is
> `backend/templates/recruiter/email/` (4 templates), still rendered by
> `api/v1/recruiter/auth_views.py` and `dashboard/views/job_helpers.py`.

**Route coverage is closed.** All 52 legacy routes are rebuilt or deliberately
dropped.

| Status | Routes | |
| --- | --- | --- |
| ✅ Migrated | 32 / 52 | Page + endpoint exist and are wired end to end |
| 🚫 Dropped by decision | 20 / 52 | See [Dropped](#dropped--decided-2026-08-12) |

Analytics (`dashboard/analytics` + 2 endpoints) is new capability with no Django
ancestor.

> **Route coverage is not the same as feature parity.** The 2026-08-13 re-audit
> found five gaps *inside* routes counted as migrated — including a job type
> with 1,973 posts that the dashboard could not create at all. See
> [Re-audit 2026-08-13](#re-audit-2026-08-13--five-gaps-inside-migrated-routes).
> Counting routes cannot catch this class; a route is "migrated" the moment a
> page exists at that address, however much of the page is missing.

## Re-audit 2026-08-13 — five gaps inside migrated routes

Re-checked both directions again: all 41 endpoints in `api/v1/recruiter/urls.py`
have a caller in `recruiter/src/`, and every frontend call resolves to a real
route. No stranded endpoints, no dead call sites. The gaps were all *inside*
routes already counted as migrated — which is the blind spot of a route-count
audit.

### 1. Team management was half-wired — fixed

Every job, applicant and analytics view filtered `user=request.user`
(`job_views.py`, `analytics_views.py`). The legacy dashboard scoped on
`user__company` when the caller was a company admin or held `jobposts_edit`
(`recruiter/views.py:748` at `ad39524`). So an admin could invite a recruiter,
see their stats on the team page, and then not open, edit or triage a single
thing they posted.

`api/v1/recruiter/scoping.py` now holds the rule — company admins get the
company's jobs, everyone else their own — and every view goes through it. The
duplicate `is_company_admin` in `views.py` became a wrapper over the
`User.is_company_admin` property so there is one definition.

### 2. Walk-in and government jobs could not be posted — fixed

The serializer has accepted 14 `walkin_*` / `govt_*` fields since it was
written, and **no form ever rendered them**. The create form offered six of the
model's nine job types; walk-in and government were not among them.

This is not a marginal type. Walk-in is the **second most common job type in
the data — 1,973 posts** — and the job seeker site ships `/walkin-jobs/`,
`/walkins-in-[city]/`, `/[skill]-walkins/` and `/government-jobs/` landing
pages against it. Only the platform-admin dashboard could fill them.

`JobTypeFields.svelte` now renders both field groups, in create and edit, with
the employment-type list shared from `$lib/constants/jobs`. Two traps found
while wiring it: `application_fee` is an `IntegerField` (not free text, so no
"₹500 for SC/ST"), and `govt_job_type` is a choice field with no blank option —
`""` is a 400, so it defaults to `Central` like the model.

`fresher` is deliberately still not offered: zero rows, it duplicates the
experience range, and the site's fresher landing pages key off
`max_experience = 0` rather than the type.

### 3. Editing a draft silently reset fields — fixed

`extractJobDataFromForm` always emitted a value for fields the edit form does
not render. PATCH is partial, but a key that is present is a key that gets
written:

| Field | Was written as | Consequence |
| --- | --- | --- |
| `show_salary` | `false` | **Defaults to true** — the salary range vanished from the listing |
| `company_description` | the Benefits textarea, which started blank | **Wiped on every save**, and benefits never saved |
| `salary_type` | hardcoded `"Year"` | Monthly pay silently rewritten as annual |
| `hiring_priority` | `"Normal"` | Every Urgent job demoted |
| `application_method` | `"portal"` | External-URL application flows quietly disabled |
| `fresher`, `relocation_required` | `false` | Cleared |

`getBoolean` now returns `undefined` when the key is absent, the two `||`
defaults are gone, and Benefits / salary period / hide-salary are seeded from
the job and submitted under their own names. A "Perks" textarea was removed:
there is no perks field on `JobPost` and nothing ever submitted it, so
everything typed into it was discarded on save.

### 4. The edit form's job-type list was a four-item subset — fixed

`['Full-time', 'Part-time', 'Contract', 'Internship']`, against create's six.
A Permanent or Freelance draft rendered an unselected `required` select, so it
could not be saved without changing its type. Both forms now read
`EMPLOYMENT_TYPES` from `$lib/constants/jobs`.

### 5. The edit form's Application Settings step wrote nowhere — fixed

Step 5 held an Auto-Reply Email Template textarea and an `assignedRecruiters`
array. `JobPost` has neither field and neither was ever submitted, so
everything typed into the auto-reply box was discarded on save — the same
shape as the Perks box in step 4. Both removed.

That would have left the step empty, so it now carries the application method
and external URL, which the edit form had never exposed. Those were the fields
whose `|| 'portal'` default was silently disabling external application flows
(#3 above): removing the default stopped the damage, and this makes the field
editable rather than merely preserved.

### Not changed — deliberate, worth confirming

**Live jobs cannot be edited.** `update_job` rejects `Live`/`Disabled`/`Expired`
(`job_views.py:250`) and the UI gates the Edit button to `Draft` consistently,
so this reads as a decision rather than an oversight. It is still a capability
the Django app had — `edit_job` had no status guard. A typo in a live posting
currently means close and repost.

One smaller one left alone: `getString` treats `""` as "absent", so text fields
can be *changed* through the edit form but not *cleared*.

### Coverage

`api/v1/recruiter/tests.py`: **57 tests** (was 40). New: 11 for company
scoping, 3 for walk-in/government round trips, 3 pinning that a partial update
leaves unsent fields alone and that the application method is writable. Full
backend suite 158 passing; recruiter frontend type-checks and builds clean.

---

## Defects found on re-audit — all fixed 2026-08-12

These were inside routes counted as migrated, so they move no route numbers —
they were live bugs, not gaps.

| # | Defect | Impact | Fix |
| --- | --- | --- | --- |
| 1 | **Applicant search did nothing** — the UI sent `search=`, `get_job_applicants` read only `status` and `ordering` | Typing in the applicant search box returned the full unfiltered list | `search` now filters on applicant first/last name, username and email |
| 2 | **CSV export ignored the search filter** — same root cause as #1 | Recruiter filters to 12 candidates, exports, silently gets all 400 | Fixed by #1; export link now rebuilt from the same `$derived` params as the on-screen filters |
| 3 | **Status tab counts collapsed** — stats were counted *after* the status filter | Picking "Pending" showed Shortlisted/Hired/Rejected as 0 | Counts are aggregated before the status filter (but inside the search filter, so they narrow with the query) |
| 4 | **"Hired" count was always 0** — stats queried `status="Selected"`, which is not in `POST_STATUS` (`Pending/Shortlisted/Hired/Rejected`) | The Hired tab read 0 even with hired applicants. The write path was already correct, so only the count was wrong | Counts `Hired`; `selected` kept as the wire name the UI reads |
| 5 | **"Share Job" was a dead button** — `<button>` with no `onclick` | Clicking did nothing | Copies the public job URL, with a "Link copied" state; now shown only for Live/Published jobs |
| 6 | **"View Public Page" 404'd** — `href="/jobs/<id>/"` resolved against the recruiter origin, which has no such route | The public listing link was broken | Built from `SITE_URL` |
| 7 | **19 hardcoded `http://localhost:8000`** across 6 files | Dashboard, analytics, job list/create/edit broke outside dev | All replaced with `API_BASE_URL` from `$lib/config/env`, matching the 8 sibling files that already did |
| 8 | **3 hardcoded `localhost:5174` redirects** in `backend/recruiter/urls.py` | Legacy redirects broke outside dev | Read from `settings.RECRUITER_FRONTEND_URL` |
| 9 | **Export link had unencoded query params** | A search for `a&b` or a name with a space corrupted the export URL | Built with `URLSearchParams` |

Coverage: `backend/api/v1/recruiter/tests.py` is now **24 tests** (was 16); the
8 new ones in `JobApplicantsListTests` pin #1–#4.

### Related, not fixed

- **`RECRUITER_FRONTEND_URL` is set to `http://localhost:5173` in the local
  gitignored `.env`** — that is the *job-seeker* port. The tracked default in
  `settings.py` and `.env.example` are corrected to 5174, but the local `.env`
  overrides both, so team-invitation emails and the legacy redirects still
  point at the wrong app until that line is changed by hand.
- ~~**Neither SvelteKit app sets `trailingSlash`**~~ — fixed since. Both set it
  at the root (`recruiter/src/routes/+layout.ts:8`, `site/src/routes/+layout.js:7`),
  and every `site/src/routes/api/**/+server.ts` re-declares it because endpoints
  do not inherit the layout's value.
- `get_job_applicants` still does not paginate, so the export's
  `page_size=10000` is inert — harmless today, latent on a job with many
  applicants.

---

## Dropped — decided 2026-08-12

21 routes, closing out the migration. Most were not recruiter features that got
skipped — they belong to **other apps that are still Django and still running**,
so dropping them from the recruiter scope removes nothing a user has today.

Row counts are from the development database (a production snapshot: 34,775
users).

### Email templates (5) and sent mail (4) — the models stay, the recruiter UI does not

`emailtemplates`, `new_template`, `edit_mailtemplate`, `view_mailtemplate`,
`delete_mailtemplate`, `send_mail`, `sent_mails`, `view_sent_mail`,
`delete_sent_mail`.

`MailTemplate` (10 rows) and `SentMail` (15 rows) are **owned by the
platform-admin dashboard**, not the recruiter: `dashboard/views/email_management.py`
serves the whole CRUD at `dashboard/urls.py:219,238-247`, and the Celery task
`sending_mail` (`dashboard/tasks.py:244-256`) writes `SentMail`. Dropping the
recruiter routes deletes no model and removes no admin capability.

The two versions did different jobs, though, and the difference is the actual
decision: the admin's mails **recruiters** (`sent_mail.recruiter.add(...)`) — a
broadcast tool — while the recruiter's was per-job
(`mail-template/list/<jobpost_id>/`) and mailed **that job's applicants**.

**Consequence, stated plainly:** the applicant pipeline can move a candidate to
Rejected or Hired and the candidate is never told. That is now the product
position, not an oversight. Revisit by building on the existing models.

### Resume pool (5) — an agency feature, not a recruiter one

`resume_pool`, `resume_upload`, `multiple_resume_upload`, `resume_view`,
`resume_edit`.

`resume_pool` gates on `request.user.agency_admin or has_perm("jobposts_resume_profiles")`,
and `AgencyResume` (78 rows) was served by `agency/views.py`. It was never in
the recruiter dashboard's remit.

> **Correction 2026-08-13.** The reasoning above was "the feature is live for
> the people who use it, just not here" — and that is no longer true. `agency/`
> was **deleted** in the Django retirement, so the resume pool is gone
> platform-wide, not relocated. The models remain; nothing serves them. Reopen
> this if agency users turn out to still exist.

### Non-Google social login (3) — cannot function today

`facebook_login`, `linkedin_login`, `twitter_login`.

`AUTHENTICATION_BACKENDS` (`jobsp/settings.py:212`) contains only
`PasswordlessAuthBackend` and `ModelBackend` — no social backends. Settings
define `FB_APP_ID`/`FB_SECRET` but **no LinkedIn or Twitter credentials at
all**. These were dead before the migration started; dropping them changes
nothing.

### Mobile verification (2) — already retired platform-wide

`verify_mobile`, `send_mobile_verification_code`.

`candidate/urls.py:101-102` has both **commented out** — the job-seeker side
was retired earlier and the recruiter side simply never got the same
treatment.

`mobile_verified` is **kept**: 19,160 of 34,775 users have it set, and
`dashboard/views/auth_views.py` plus `templates/email/daily_report.html` still
report on it. It is a historical flag now — nothing sets it going forward.

### Messaging (1) and Google account linking (1)

`messages`, `google_connect`.

`UserMessage` has **3 rows** and `site/` has no messaging routes at all.
`google_connect` linked Google to an *existing* password account — distinct
from Google sign-in, which is now built.

> **Correction 2026-08-13.** This originally read "the candidate half still
> runs on Django (`candidate/views/message_views.py`)", implying messaging
> survived on the seeker side. `candidate/` has since been deleted, so
> recruiter↔candidate messaging is gone platform-wide. With 3 rows, that is
> almost certainly the right outcome — but it is a removal, not a hand-off.

### Dead code removed

Eight form classes in `backend/recruiter/forms.py` with zero references
repo-wide (checked across every file type, not just Python):

| Removed | Belonged to |
| --- | --- |
| `MobileVerifyForm` | mobile verification, dropped above |
| `ResumeUploadForm`, `ApplicantResumeForm` | resume pool, dropped above |
| `Company_Form`, `User_Form`, `LoginForm` | the legacy registration/login flow, migrated |
| `EditCompanyForm`, `RecruiterForm` | legacy company/recruiter management, migrated |

Six dead helpers in `backend/recruiter/views/job_helpers.py` —
`adding_keywords`, `set_other_fields`, `adding_other_fields_data`,
`save_job_post`, `checking_error_value`, `retreving_form_errors`. Reached only
through `from .job_helpers import *` in `recruiter/views/__init__.py`, and no
name was referenced anywhere, so the star import re-exported nothing live.
364 → 178 lines; the four `add_other_*`/`add_interview_location` helpers
`dashboard/views/job_management.py` calls are untouched.

Seven orphaned templates in `backend/templates/recruiter/email/` —
`activate`, `applicants`, `invoice_pdf`, `recruiter_account`, `support`, plus
`google_welcome` and `google_registration_welcome` from the legacy Django
Google flow. The rebuilt flow sends no welcome mail: Google has already
verified the address and the user is logged straight in. Checked that no view
builds a template name dynamically — only `psite/views.py` does, from
`pages/`. Four remain (`add_other_fields`, `password_reset`,
`team_invitation`, `verification`), all still rendered.

`recruiter/forms.py`: 932 → 613 lines. The file stays — `ChangePasswordForm`,
`PersonalInfoForm`, `JobPostForm`, `MailTemplateForm`, `MenuForm`,
`ClientForm`, `AgencyWorkLogForm` and `UserStatus` are all still imported by
`dashboard/` and `agency/`.

---

## Retirement 2026-08-12

The migration being closed did not make the Django app go away — 823 lines
survived it. Almost none of it was the recruiter's.

### The forms and helpers belonged to other apps

`recruiter/forms.py` had **zero** recruiter callers. It was a container for code
`dashboard/` and `agency/` imported, and that import was the last thing pinning
the app into the graph. Moved to the apps that actually use them:

| Moved | To | Sole consumer |
| --- | --- | --- |
| `JobPostForm`, `MenuForm` (+ `valid_time_formats`) | `dashboard/forms.py` | `dashboard/views/{job,company}_management.py` |
| `ClientForm`, `AgencyWorkLogForm` | `agency/forms.py` (new) | `agency/views.py` |
| `UserStatus` (+ its status choices) | `peeldb/forms.py` (new) | `peeldb/templatetags/page_tags.py` |
| `job_helpers.py` — 4 functions | `dashboard/views/job_helpers.py` | `dashboard/views/job_management.py` |

`job_helpers.py` already imported `dashboard.tasks`, so it had been pointing
back at its own consumer.

`ChangePasswordForm`, `PersonalInfoForm` and `MailTemplateForm` were **not**
moved — they were dead duplicates. `dashboard/forms.py` and `candidate/forms.py`
already define their own, and nothing imported the `recruiter.forms` copies. An
earlier name-based scan had counted the other apps' usages and marked them
live; matching on the import source instead is what caught it.

### The duration constants

`MONTHS`/`YEARS` were defined in both `recruiter/forms.py` and
`candidate/forms.py`, and `dashboard/` and `peeldb/templatetags/` each reached
into a different one. Now `peeldb/choices.py`:

| Constant | Range | Was |
| --- | --- | --- |
| `EXPERIENCE_MONTHS` | 0–12 | byte-identical in both apps |
| `JOB_EXPERIENCE_YEARS` | 0–20 | `recruiter.forms.YEARS` — what a *job* asks for |
| `PROFILE_EXPERIENCE_YEARS` | 0–40 | `candidate.forms.YEARS` — what a *seeker* has |

The two `YEARS` were **not** interchangeable, so merging them into one constant
would have silently changed both dropdowns. Each new constant was asserted
equal to the original tuple before anything was repointed.

Not to be confused with `peeldb.models.MONTHS`, which is calendar month names.

### Two dead pages

**`post_job`** was already migrated to the recruiter signup, but was still
rendering `recruiter_v2/post_job.html`. View and template deleted; `/post-job/`
is a redirect in `jobsp/urls.py` now. The URL *name* stays — `base.html`,
`auth_base.html`, `base_with_tailwind_megamenu.html` and `sitemap.html` all
reverse it, and they are surviving job-seeker templates.

**`how_it_works`** was deleted outright. It extended `recruiter/index.html`,
which was removed in commit `d6763e9`, so every request had been a
`TemplateDoesNotExist` 500 — and **no template reversed either name**. It was
routed twice, at `recruiter:how_it_works` and `agency:how_it_works`; both are
gone, along with `templates/recruiter/how_it_works.html`. Same shape as
`interview_location`, found the same way.

That removed the last view, so `recruiter/views/` is gone as a package.

### Verified

- `manage.py check` clean; ruff clean across 259 files
- Every moved form **instantiated**, not just imported — `JobPostForm` (66
  fields, bound), `MenuForm`, `ClientForm`, `AgencyWorkLogForm`, and
  `UserStatus` rendering its `user_status_<id>` widget
- Full suite: 111 tests, unchanged at the 23-error + 1-failure baseline
- `check_url_names`: **45 unresolvable, unchanged** — the deletions introduced
  no new dangling `{% url %}`
- All four surviving redirects return 302 on a freshly started server; the two
  former 500s now 404

> The redirects resolve to **`localhost:5173`** in this dev environment — the
> job-seeker port. That is the stale `RECRUITER_FRONTEND_URL` in the gitignored
> `backend/.env`, still unfixed. The tracked default is correct.

---

## Wired up 2026-08-12

The two routes the third pass found stranded. Both had a finished, routed DRF
endpoint and no caller.

### `change_password`

`dashboard/account` grew a Password card: `changePassword` action in
`+page.server.ts` posting to `auth/change-password/`, and a three-field form.
Uses its own `passwordError`/`passwordSuccess` keys so a failed password change
does not light up the profile form's banner. DRF field errors
(`{"old_password": ["Current password is incorrect"]}`) are flattened to the
first message rather than dumped raw.

### `google_login`

- `(auth)/login` fetches the auth URL server-side, so the button ships as a
  real `href` and works before hydration
- `auth/google/callback/+page.server.ts` — new; exchanges the code, sets
  HttpOnly cookies, redirects. Never existed before
- `(auth)/complete-signup/` — new; the gap between callback and
  `auth/google/complete/` for a Google account we have never seen. Kept out of
  `/signup/`, which is a 628-line wizard built around choosing an account type
  and setting a password, none of which applies
- `$lib/server/google.ts` holds the pending signup in an HttpOnly cookie
  between the two, so the token stays out of the URL, browser history and any
  `Referer`

**168 employer accounts already have a Google account linked**, so the
sign-in path serves real users from day one.

#### The backend bug this uncovered

`google_callback` stashed the pending signup in `request.session` and
`google_complete` read it back. That could never work: the only caller is the
SvelteKit server, which talks to Django machine-to-machine and holds no session
cookie, so every request built a fresh empty session and `google_complete`
**always** answered `"Invalid or expired session token"`. The code carried a
`TODO: Use Redis or Django cache` acknowledging the storage was unfinished.

A cache would work but adds shared state — and `CACHES` is commented out
(`settings.py:413-429`), so it is per-process `LocMemCache`, wrong the moment
there is more than one worker. Replaced with `django.core.signing`: the
identity is signed with `SECRET_KEY` and handed to the client, which replays
it. Stateless, tamper-proof, no new dependency, correct across workers.

Also: `GoogleCompleteSerializer.session_token` capped at `max_length=100`,
while a signed payload is ~162 characters — the flow would have 400'd on length
before the signature was ever checked. Cap removed.

Google's own `access_token` is no longer round-tripped through the client;
`google_complete` never used it.

### Also fixed here

**"View Public Page" still 404'd.** The second pass rebuilt it from `SITE_URL`,
but in the recruiter app `PUBLIC_SITE_URL` is *this app's own origin*
(`:5174`, labelled "Frontend URL for OAuth callbacks") — and this app has no
public job route. Added `PUBLIC_JOBSEEKER_URL` and pointed the link at it;
`SITE_URL` now has one job, the OAuth `redirect_uri`.

> `PUBLIC_JOBSEEKER_URL` was appended to `recruiter/.env.example` **and** to the
> local gitignored `recruiter/.env`. Other machines need it added by hand or
> the build fails on the missing `$env/static/public` import.

### The security hole this uncovered

Testing the new form, **`password123` was accepted**. `AUTH_PASSWORD_VALIDATORS`
was defined in no settings module, and Django treats a missing setting as an
empty list — so every `validate_password()` call in the API ran **zero** checks.
Only the serializers' `min_length=8` applied. This predated the migration and
hit registration, password reset and change password alike, on both the
recruiter and job seeker APIs.

Added Django's four standard validators to `jobsp/settings.py`: user-attribute
similarity, minimum length 8 (matching the serializer fields so the two cannot
drift), common-password, and all-numeric.

`UserAttributeSimilarityValidator` only runs when `validate_password()` is
handed the user, and all six call sites passed none — so adding it alone would
have been another validator that silently does nothing. All six now pass one:

| Call site | User source |
| --- | --- |
| `recruiter` register | unsaved `User` built from the posted email/name |
| `recruiter` reset password | `self.context["user"]`, set in `validate_token` |
| `recruiter` change password | `self.context["request"].user` |
| `auth` (job seeker) register | unsaved `User` built from the posted email/name |
| `auth` (job seeker) reset password | `self.user`, set in `validate_token` |

Existing password hashes are untouched; only new and changed passwords are
validated.

### Coverage

`api/v1/recruiter/tests.py`: **24 → 40 tests**.

- `ChangePasswordTests` (4)
- `GoogleSignupTokenTests` (6) — pins the signing round trip and rejects
  tampered, foreign-salt and expired tokens, so the session bug cannot return
- `PasswordStrengthTests` (6) — rejects common, all-numeric and
  email-resembling passwords on both change and registration. If
  `AUTH_PASSWORD_VALIDATORS` is dropped again, or a serializer stops passing
  the user, one of these fails

Full suite: 111 tests, unchanged at the 23-error + 1-failure baseline (all
Haystack reaching for Elasticsearch in legacy `candidate`/`pjob` form tests).

---

## API built, UI missing — found on third pass

> **Resolved** — all four are wired and tested; see
> [Wired up](#wired-up-2026-08-12). Kept because the *way* they were missed is
> the reusable lesson.

The second pass checked "does every endpoint the UI calls exist?" and found the
microsite-menu hole. It never asked the mirror question: **does every endpoint
have a caller?** Four did not. All four were routed, importable and — to a
static reading — complete. They were simply unreachable, because nothing in
`recruiter/src/` referenced them, and nothing in `api/v1/recruiter/tests.py`
covered them. One of the four could never have worked even if called.

| Endpoint | View | Callers then | Now |
| --- | --- | --- | --- |
| `POST auth/change-password/` | `auth_views.change_password` | 0 | `dashboard/account` |
| `GET auth/google/url/` | `auth_views.google_auth_url` | 0 | `(auth)/login` |
| `POST auth/google/callback/` | `auth_views.google_callback` | 0 | `auth/google/callback` |
| `POST auth/google/complete/` | `auth_views.google_complete` | 0 | `(auth)/complete-signup` |

≈310 lines of `api/v1/recruiter/auth_views.py` that no client could execute.

### `change_password` — recruiters could not change their password

Legacy `change-password/` had a form. `dashboard/account/+page.server.ts`
exports exactly two actions, `updateProfile` and `uploadPicture`;
`account/+page.svelte` contains no occurrence of "password" or "security" at
all. A signed-in recruiter's only route to a new password is to sign out and go
through forgot-password → email → reset, which *is* wired.

Closed with one form section plus one action, since the endpoint was done.

### `google_login` — no Google button on the recruiter login page

`grep -ri google recruiter/src/` returns **nothing**. The login page's only
submit control is the email/password button (`login/+page.svelte:204`), and
there is no `(auth)/google/` callback route to receive a redirect.

Note these are recruiter-specific views, not shared with the job-seeker flow —
`api/v1/auth/urls.py` routes a *different* pair (`views.google_auth_url`,
`views.google_auth_callback`) which `site/` does use and `GoogleAuthAPITests`
does cover. The recruiter trio at `api/v1/recruiter/auth_views.py:506-792`,
including the `google_complete` registration-finishing step, has neither a
caller nor a test.

This also revises the second pass's note on `google_connect`. That entry said
`auth/google/complete/` "only finishes registration — it is not a substitute"
for linking Google to an existing account. True, but it understated the gap:
there is no Google entry point in the recruiter UI whatsoever, so
`google_login` is unmigrated too, not just `google_connect`.

### What was checked and is clean

- **All 38 API paths** called from `recruiter/src/` resolve to a route in
  `api/v1/recruiter/urls.py` — no repeat of the microsite-menu class of defect
- **No unreferenced form actions.** Every non-`default` action in every
  `+page.server.ts` is reachable from a `?/name` form in its own directory, so
  the dead-`toggleStatus` class of defect is closed. The four bare `default`
  actions (login, logout, forgot-password, reset-password) are posted to by
  actionless `<form method="POST">`, which is correct
- **No API surface** for `MailTemplate`, `SentMail`, `UserMessage` or
  `AgencyResume` — confirms those 15 routes are genuinely unbuilt, not merely
  unwired
- **`check_url_names`: 45 unresolvable, 0 in the `recruiter:` namespace** —
  unchanged from the second pass; the survivors are `candidate:`, `dashboard:`
  and `agency:` reverses in job-seeker templates
- **No hardcoded hosts** anywhere in `recruiter/src/` or `site/src/` outside
  `lib/config/env.ts`, where they are the documented fallbacks

---

## Resolved — the seven shipped-but-broken items

All seven are closed. Two were dropped, five were finished; tests live in
`backend/api/v1/recruiter/tests.py` (16 tests).

| # | Item | Outcome |
| --- | --- | --- |
| 1 | Company microsite menu CRUD | **Dropped** — UI deleted |
| 2 | Team activate/deactivate | **Finished** — endpoint + `is_active` + button |
| 3 | Job email-notification toggle | **Finished** — dedicated endpoint |
| 4 | Company logo upload | **Finished** — real multipart upload |
| 5 | Job view counts | **Finished** — real counter |
| 6 | Job location editing | **Finished** — picker ported |
| 7 | `interview_location` | **Dropped** — view + route deleted |

### 1. Company microsite menu CRUD — dropped

Nothing consumed company menus: `site/src/routes/(site)/companies/[id]` has no
menu markup, so five endpoints would have fed an admin screen with no public
surface. `dashboard/company/microsite/` and the card linking to it are deleted.
`peeldb.models.Menu` stays — it is the platform-admin dashboard's concern.

### 2. Team member activate/deactivate — finished

Was three failures in one feature: a `toggleStatus` action calling an unrouted
endpoint, no component invoking that action, and `is_active` missing from the
serializers so **every** member rendered the grey "Inactive" badge.

- `POST /api/v1/recruiter/team/<user_id>/toggle-status/` →
  `toggle_team_member_status`, admin-only, company-scoped, cannot toggle self
- `is_active` added to `TeamMemberSerializer`
- Activate/deactivate button wired into `dashboard/team/+page.svelte`, plus an
  "Inactive" badge on the list

No last-admin guard: the caller is an active admin and cannot deactivate
itself, so one active admin always survives. (The equivalent guard in
`remove_team_member` is unreachable for the same reason.)

### 3. Job email-notification toggle — finished

Two defects, not one. `send_email_notifications` was in no serializer, *and*
`update_job` refuses any edit to a Live/Disabled/Expired job — so routing the
toggle through `jobs/<id>/update/` could never have worked on a Live job, the
only state where applicant notifications exist.

- `PATCH /api/v1/recruiter/jobs/<job_id>/notifications/` →
  `set_job_notifications`, allowed at any job status
- `send_email_notifications` added to the detail and create serializers, so the
  UI can read current state and set it at creation
- `jobs/[id]/+page.server.ts` points at the new endpoint

Kept separate from `update_job` on purpose: this is the recruiter's own
notification preference, not public job content, so the
published-jobs-are-immutable rule should not apply to it.

### 4. Company logo upload — finished

The old control was pure theatre — `FileReader` painted a local preview and
nothing was ever uploaded, so the logo vanished on reload.

- `uploadLogo` action posts multipart to `company/profile/update/`, which
  already accepted `profile_pic`
- Mirrors the user-avatar pattern in `dashboard/account/+page.server.ts`
- JPEG/PNG, 2 MB cap, admin-only

### 5. Job view counts — finished

`get_views_count()` returned a hardcoded `0` while four screens displayed it as
a real metric.

- `JobPost.views_count` (`PositiveIntegerField`, migration `0073`)
- Incremented in `JobViewSet.retrieve()` with `F("views_count") + 1` so
  concurrent views cannot clobber each other
- Raw count, not unique visitors — a refresh counts again. The job's own
  recruiter is excluded so checking your own listing does not inflate it

### 6. Job location editing — finished

The searchable city picker (max 3) from `jobs/new/+page.svelte` is now in
`jobs/[id]/edit/+page.svelte`, replacing the read-only chips and the "coming
soon" note.

Caveat inherited from the API: `update_job` still refuses to edit a
Live/Disabled/Expired job, so this — like every other field on that form —
only applies to Draft jobs.

### 7. `interview_location` — dropped

Rendered `recruiter/job/add_interview_location.html`, which does not exist →
`TemplateDoesNotExist` on every request. View and route deleted.

`recruiter/views/job_helpers.py:add_interview_location` is a **different**
function, imported by `dashboard/views/job_management.py` — left untouched.

---

## Original findings (kept for context)

These are worse than "not migrated" — the UI is present and looks functional,
so the failure is silent.

### 1. Company microsite menu CRUD — endpoints do not exist

`recruiter/src/routes/(dashboard)/dashboard/company/microsite/+page.server.ts`
calls five endpoints that are absent from `backend/api/v1/recruiter/urls.py`:

| Call site | Endpoint requested | Exists? |
| --- | --- | --- |
| `+page.server.ts:26` | `GET /api/v1/recruiter/company/menu/` | No |
| `+page.server.ts:68` | `POST /api/v1/recruiter/company/menu/add/` | No |
| `+page.server.ts:131` | `POST .../company/menu/edit/<menuId>/` | No |
| `+page.server.ts:182` | `POST .../company/menu/delete/<menuId>/` | No |
| `+page.server.ts:227` | `POST .../company/menu/status/<menuId>/` | No |

The `load()` swallows the 404 (`response.ok ? … : { menus: [] }`), so the page
renders as an empty menu list rather than an error. Every create/edit/delete
action fails. Legacy equivalents: `add_menu`, `edit_menu`, `delete_menu`,
`menu_status` in `recruiter/views.py`.

### 2. Team member activate/deactivate — endpoint does not exist, and status always renders "Inactive"

Three layers of the same missing feature. Legacy equivalent:
`activate_company_recruiter` (`/recruiter/company/recruiters/status/<id>/`).

- `team/+page.server.ts:292-330` defines a `toggleStatus` form action calling
  `POST /api/v1/recruiter/team/<userId>/toggle-status/` — **not routed**
- No component invokes that action; the team list has no button wired to it, so
  the action is unreachable dead code
- `team/[id]/+page.svelte:83` branches on `member.is_active`, but `is_active`
  is in neither `TeamMemberSerializer.Meta.fields`
  (`api/v1/recruiter/serializers.py:57`) nor `TeamMemberDetailSerializer`
  (`:95`) → always `undefined` → **every team member renders the grey
  "Inactive" badge**, including active ones

`update_team_member` (`api/v1/recruiter/views.py:347`) handles only `job_title`
and `is_admin`, so there is no existing endpoint to reuse.

### 3. Job email-notification toggle — field silently dropped

`recruiter/src/routes/(dashboard)/dashboard/jobs/[id]/+page.server.ts:81-132`
reads `job.send_email_notifications`, inverts it, and PATCHes it to
`jobs/<id>/update/`.

- `send_email_notifications` is a real model field (`peeldb/models.py:1265`)
- It is **not** in `RecruiterJobDetailSerializer.Meta.fields`
  (`api/v1/recruiter/job_serializers.py:276`) → the read is `undefined`, so the
  toggle always computes `!undefined === true`
- It is **not** in `RecruiterJobCreateSerializer.Meta.fields`
  (`api/v1/recruiter/job_serializers.py:436`), which `RecruiterJobUpdateSerializer`
  inherits → DRF drops the unknown key

Result: the PATCH returns 200, the UI reports "Email notifications enabled",
and nothing changes in the database. Legacy equivalent: `enable_email_notifications`.

### 4. Company logo — API supports it, UI does not send it

`CompanyUpdateSerializer` accepts `profile_pic`
(`api/v1/recruiter/serializers.py:324`), but
`dashboard/company/+page.server.ts` never submits it. Legacy `upload_profilepic`
has no UI replacement.

### 5. Job view counts hardcoded to zero

`api/v1/recruiter/job_serializers.py:190-193` — `get_views_count()` returns `0`
with a `TODO`. The job list and dashboard stats display it as a real metric.

### 6. Job locations cannot be edited (UI gap only — no data loss)

`recruiter/src/routes/(dashboard)/dashboard/jobs/[id]/edit/+page.svelte:458` —
"Location editing coming soon. Please contact support to change locations."

The API fully supports `location_ids` on update, and the form does submit it
(`+page.server.ts:281`) — the existing values are round-tripped through hidden
inputs (`+page.svelte:280`), so an edit does **not** wipe the job's locations.
The only thing missing is a location picker in the form.

### 7. Interview locations — Django view is broken, no replacement

`backend/recruiter/views/dashboard.py:23` (`interview_location`) renders
`recruiter/job/add_interview_location.html`, which **does not exist** anywhere in
`backend/templates/` → `TemplateDoesNotExist` (500) on every request. The
route is still live at `/recruiter/job/interview-location/<count>/`.

The walk-in fields (`walkin_from_date`, `walkin_to_date`, `walkin_time`,
`walkin_contactinfo`) did make it into the job serializer, but the legacy
multi-interview-location feature did not.

---

## ❌ Not migrated

| Legacy route | View | Notes |
| --- | --- | --- |
| `/recruiter/resume/pool/` | `resume_pool` | Whole resume-pool feature absent from DRF and SvelteKit |
| `/recruiter/resume/upload/` | `resume_upload` | " |
| `/recruiter/multiple/resumes/upload/` | `multiple_resume_upload` | " |
| `/recruiter/resume/view/<id>/` | `resume_view` | " |
| `/recruiter/resume/edit/<id>/` | `resume_edit` | " |
| `/recruiter/messages/` | `messages` | Recruiter inbox — no equivalent (`UserMessage` model still exists) |
| `mail-template/list/<jobpost_id>/` | `emailtemplates` | **Not in the first pass's tally.** Per-job email templates; `MailTemplate` model still exists, no API |
| `mail-template/new/<jobpost_id>/` | `new_template` | " |
| `mail-template/edit/<jobpost_id>/<template_id>/` | `edit_mailtemplate` | " |
| `mail-template/view/<template_id>/` | `view_mailtemplate` | " |
| `mail-template/delete/<template_id>/` | `delete_mailtemplate` | " |
| `send_mail/<template_id>/<jobpost_id>/` | `send_mail` | **Not in the first pass's tally.** Mail a job's applicants from a template; `SentMail` model still exists, no API |
| `sent-mail/list/<jobpost_id>/` | `sent_mails` | " |
| `sent-mail/view/<sent_mail_id>/` | `view_sent_mail` | " |
| `sent-mail/delete/<sent_mail_id>/` | `delete_sent_mail` | " |
| `/recruiter/mobile/verify/` | `verify_mobile` | Mobile verification dropped; `mobile` is a plain profile field now |
| `/recruiter/send/mobile_verification_code/` | `send_mobile_verification_code` | " |
| `/recruiter/facebook_login/` | `facebook_login` | Only Google OAuth was carried over |
| `/recruiter/linkedin_login/` | `linkedin_login` | " |
| `/recruiter/twitter_login/` | `twitter_login` | " |
| `/recruiter/google_connect/` | `google_connect` | Link Google to an *existing* account. `auth/google/complete/` only finishes **registration** — it is not a substitute, and is itself uncalled |
| `/recruiter/google_login/` | `google_login` | **Moved here on the third pass.** `auth/google/url|callback|complete/` are all routed, but `recruiter/src/` has zero references to Google — no button, no callback route |
| `/recruiter/change-password/` | `change_password` | **Moved here on the third pass.** `auth/change-password/` is routed and complete; `dashboard/account` has no password UI, so a signed-in recruiter cannot change their password |
| `/recruiter/company/menu/add|edit|delete|status/` | `add_menu` etc. | **Dropped 2026-08-12** — microsite admin UI deleted, nothing renders company menus |
| `/recruiter/company/menu/order/` | `menu_order` | Menu reordering — dropped with the rest of the menu feature |
| `/recruiter/how-it-works/` | `how_it_works` | Still served by Django (`templates/recruiter/how_it_works.html`) |
| `/post-job/` | `post_job` | Still served by Django (`templates/recruiter_v2/post_job.html`) |
| `/recruiter/job/interview-location/<n>/` | `interview_location` | **Deleted 2026-08-12** — view + route removed (was a guaranteed 500) |

Resume pool, messaging, mobile verification, Facebook/LinkedIn/Twitter login
and microsite menus are product decisions, recorded 2026-08-12 so the decision
survives.

**Email templates and sent mail are not covered by that decision.** The first
pass omitted them from the inventory, so they were never put to a finish/drop
call. They are 10 routes and two live models — the largest open question in
this migration.

---

## ✅ Migrated

### Auth & account

| Legacy | SvelteKit | DRF |
| --- | --- | --- |
| `login/` (`new_user`) | `(auth)/login` | `auth/login/` |
| `out/` (`getout`) | `api/auth/clear-cookies` | `auth/logout/` |
| `pwdreset/` | `(auth)/forgot-password`, `(auth)/reset-password` | `auth/forgot-password/`, `auth/reset-password/` |
| `activation/<user_id>/` | `(auth)/verify-email` | `auth/verify-email/`, `auth/resend-verification/` |
| `thank-you-message/` | folded into `(auth)/verify-email` + `(auth)/onboarding` | — |
| `profile/` | `dashboard/account` | `auth/me/` |
| `profile/edit/` | `dashboard/account` | `profile/update/`, `profile/picture/` |

`change-password/` and `google_login/` were listed here by the second pass.
Both are wrong — the endpoints exist but no UI reaches them, so they are in
[❌ Not migrated](#-not-migrated) now.

### Jobs

| Legacy | SvelteKit | DRF |
| --- | --- | --- |
| `dashboard/` | `(dashboard)/dashboard` | `dashboard/stats/` |
| `job/list/` | `dashboard/jobs` | `jobs/` |
| `job/inactive/list/` | `dashboard/jobs/inactive` | `jobs/?status=…` |
| `job/<status>/new/` | `dashboard/jobs/new` | `jobs/create/`, `jobs/metadata/` |
| `job/<status>/copy/` | `dashboard/jobs/new?copyFrom=<id>` | `jobs/<id>/` (prefill) |
| `job/edit/<id>/` | `dashboard/jobs/[id]/edit` | `jobs/<id>/update/` — partial, see ⚠️ 6 |
| `job/view/<id>/` | `dashboard/jobs/[id]` | `jobs/<id>/` |
| `job/preview/<id>/` | `dashboard/jobs/[id]/preview` | `jobs/<id>/` |
| `job/deactivate/<id>/` | job detail action | `jobs/<id>/close/` |
| `job/enable/<id>/` | job detail action | `jobs/<id>/publish/` |
| `job/delete/<id>/` | job list/detail action | `jobs/<id>/delete/` |

### Applicants

| Legacy | SvelteKit | DRF |
| --- | --- | --- |
| `job/applicants/<id>/` | `dashboard/jobs/[id]/applicants` | `jobs/<id>/applicants/` |
| `download/<jobpost_id>/<status>/` | `jobs/[id]/applicants/download/+server.ts` (CSV built in SvelteKit) | `jobs/<id>/applicants/?page_size=10000` |

### Company & team

| Legacy | SvelteKit | DRF |
| --- | --- | --- |
| `microsite-page/` (`view_company`) | `dashboard/company`, `dashboard/company/microsite` | `company/profile/` |
| `company/edit/` | `dashboard/company` | `company/profile/update/` |
| `company/recruiters/` | `dashboard/team` | `team/` |
| `company/recruiter/add/` | `dashboard/team` (invite flow) | `team/invite/` |
| `company/recruiter/edit/<id>/` | `dashboard/team/[id]` | `team/<id>/update/` |
| `company/recruiter/delete/<id>/` | `dashboard/team` | `team/<id>/remove/` |
| `company/recruiters/profile/<id>/` | `dashboard/team/[id]` | `team/<id>/` |

---

## New in the rewrite (no Django ancestor)

- `dashboard/analytics` → `analytics/applications/`, `jobs/<id>/analytics/`
- `(auth)/onboarding` — post-signup company setup
- Team invitation lifecycle — `team/invitations/`, `.../resend/`, `.../cancel/`,
  `auth/accept-invitation/` (legacy created recruiter accounts directly)
- Applicant detail + status pipeline — `jobs/<id>/applicants/<id>/`, `.../update/`

---

## Django-side leftovers

Dead weight that the migration left behind. All of it is safe to delete once
the ⚠️ items above have real endpoints.

**`/api-recruiter/` — 17 routes, zero callers.** `backend/recruiter/api_urls.py`
+ `api_views.py` (~900 lines) was the API for the *previous* rewrite attempt.
Neither `recruiter/src` nor `site/src` references it; everything goes through
`/api/v1/recruiter/`.

**Unrouted views** in `backend/recruiter/views/dashboard.py`:
- `dashboard()` (line 9) — the URL is a `RedirectView`, this never runs
- `get_autocomplete()` (line 57) — zero references repo-wide
- `create_slug()` (line 38) — helper for the deleted registration flow

**Orphaned templates** (no view, no `{% include %}`, no `{% extends %}`):
- `templates/recruiter/dashboard.html`
- `templates/recruiter/user/description.html`, `user/mobile_verify.html`, `user/payment_details.html`
- `templates/recruiter/company/edit_microsite_page.html`, `company/view_microsite_page.html`
- `templates/recruiter_v2/jobs/list.html`, `jobs/new.html`, `job/preview.html`, `register.html`

**Still referenced, keep for now:**
- `templates/recruiter/how_it_works.html` → `how_it_works` view
- `templates/recruiter/recruiter_404.html` → `psite`, `tickets`, `pjob`, `agency` views
- `templates/recruiter/company/add_branch.html`, `add_client.html`, `client_list.html`, `edit_client.html`, `add_contract_details.html` → `agency/views.py`
- `templates/recruiter/email/*` (11 files) → transactional mail, permanent
- `templates/recruiter/tickets/*` → `tickets` app

~~**Hardcoded `localhost:5174`** in all five redirects~~ — fixed; the three
surviving redirects read `settings.RECRUITER_FRONTEND_URL`.

---

## What is left

The seven broken/partial items are closed. Remaining:

1. ~~Delete `/api-recruiter/`, the unrouted views, and the orphaned
   templates.~~ **Done 2026-08-12** — see [Cleanup](#cleanup-2026-08-12).
2. ~~Replace the hardcoded `localhost:5174` redirect host with a setting.~~
   **Done 2026-08-12** — `backend/recruiter/urls.py` reads
   `settings.RECRUITER_FRONTEND_URL`. The local gitignored `.env` still
   overrides it to `:5173`; that line has to be changed by hand.
3. **Wire the four orphaned auth endpoints, or delete them** — change-password
   and the Google trio, see
   [API built, UI missing](#api-built-ui-missing--found-on-third-pass).
   Change-password is the one with a real user cost: a signed-in recruiter
   currently has no way to change their password.
4. `update_job` refuses to edit Live/Disabled/Expired jobs. That is a
   deliberate product rule, but it means the whole edit form — not just
   locations — is Draft-only. Worth confirming that is intended.
5. ~~`jobs/[id]/edit/+page.server.ts:31` hardcodes `http://localhost:8000`.~~
   **Done 2026-08-12** — no hardcoded host survives anywhere in `recruiter/src/`.
6. Decide finish-or-drop on email templates and sent mail (10 routes, 2 live
   models, no API). Still the largest open question in this migration.
7. The backend suite has 23 errors + 1 failure on a clean tree: every error is
   Haystack's realtime signal processor reaching for Elasticsearch during
   legacy `candidate`/`pjob` form tests. `api/v1/recruiter/tests.py` sidesteps
   it with a mixin that detaches the signal processor; the real fix is to stop
   wiring Elasticsearch into the test settings at all.

---

## Cleanup (2026-08-12)

Removed the Django code the finished migration and the drops left behind.

### Legacy `/api-recruiter/` API — gone

17 routes, ~900 lines, zero callers. It was the API for a previous rewrite
attempt, superseded by `/api/v1/recruiter/`.

| Deleted | Why it was safe |
| --- | --- |
| `recruiter/api_urls.py` | Only referenced by the `jobsp/urls.py` include, removed with it |
| `recruiter/api_views.py` | Nothing imported it but `api_urls` |
| `recruiter/serializers.py` | Only imported by `api_views` |
| `recruiter/permissions.py` | Only imported by `api_views` |
| `recruiter/exceptions.py` | Zero importers |
| `recruiter/utils.py` | Only imported by `exceptions`, itself dead |
| `recruiter/status.py` | Zero importers |
| `recruiter/middleware.py` | Zero importers, absent from `MIDDLEWARE` |

**Side effect worth noting:** `manage.py spectacular` now generates with **zero
warnings and zero errors**. All 88 errors (17 unique) originated in
`api_views.py`.

`recruiter/forms.py` and `recruiter/views/job_helpers.py` were **kept** — the
platform-admin dashboard, `agency/` and `peeldb/templatetags/page_tags.py`
import from them.

### Unrouted views — gone

`recruiter/views/dashboard.py` is down to `post_job` and `how_it_works`.
Removed `dashboard()` (the URL is a `RedirectView`, so it never ran),
`get_autocomplete()` and `create_slug()` (zero references repo-wide).

### Orphaned templates — gone

12 files with no view, no `{% include %}` and no `{% extends %}`:
`recruiter/dashboard.html`; `recruiter/user/{description,mobile_verify,payment_details}.html`;
`recruiter/company/{edit_microsite_page,view_microsite_page}.html`;
`recruiter_v2/{jobs/list,jobs/new,job/preview,register}.html`; and
`recruiter_v2/{recruiter_base_with_menu,recruiter_base}.html`, which only the
above extended.

`templates/recruiter_v2/` is now just `post_job.html`.

### Redirects — 2 of 5 gone

`index` and `profile` had no reverses left and were removed. Three stay because
live templates reverse them:

| Name | Reversed by |
| --- | --- |
| `new_user` | `base.html`, `auth_base.html`, `base_with_tailwind_megamenu.html`, `recruiter_v2/post_job.html` |
| `list` | `recruiter/company/{client_list,add_client,edit_client}.html` (rendered by `agency/views.py`) |
| `dashboard` | `recruiter/recruiter_404.html` (rendered by psite, tickets, pjob, agency) |

### Verification

- `check_url_names`: **113 → 45 unresolvable**, and **zero** in the `recruiter:`
  namespace. The drop is the orphaned templates taking their dangling
  `recruiter:`/`agency:` reverses with them
- `manage.py check` clean; 16/16 new tests pass; full suite unchanged at the
  23-error + 1-failure baseline
- `ruff check` + `format --check` clean across all 258 backend files
- OpenAPI: 90 paths, 0 warnings, 0 errors
