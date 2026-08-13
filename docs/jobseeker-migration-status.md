# Job-seeker migration status: Django → SvelteKit + DRF

Route-by-route audit of the legacy Django job-seeker apps (`candidate/`,
`pjob/`, `search/`) against what exists today in `site/` (SvelteKit) and
`backend/api/v1/` (DRF). Companion to
[recruiter-migration-status.md](recruiter-migration-status.md).

**Method** — this is built from the *live* URLconf, the *live* API URLconf and
the *live* `site/src/routes` tree, not from the pre-migration baseline. Every
row below was checked; nothing is left at `unverified`.

Audited 2026-08-13. Supersedes the 2026-08-12 pass, which was written against
`git show ad39524:` and undercounted the surface by 25 routes.

**Revised 2026-08-13 (second pass).** The first 2026-08-13 pass scoped itself
to `candidate/` + `pjob/` and so missed `search/`, which owns two SEO listing
families mounted at the site root by `jobsp/urls.py` — including
`/{skill}-jobs-in-{city}/`, the single largest family in the sitemap at 5,924
URLs. Corrected below.

## Headline

| | Routes | |
| --- | --- | --- |
| ✅ Migrated | 100 | Endpoint exists **and** UI is wired to it |
| ❌ Not migrated | 30 | No SvelteKit page, or page exists but is fake |
| 🚫 Not needed | 25 | Duplicates, dev leftovers, dropped features, dead Elasticsearch autocompletes |
| **Total** | **155** | `candidate/` 65 + `pjob/` 76 + `search/` 14 |

Route counts include paginated duplicates (`/jobs-in-{loc}/{page}/`), which is
why the total is higher than the 40 in the first audit. Grouped by *feature*
the picture is much simpler — see the three sections below.

**Substantially complete.** The profile tree, the auth flow, 21 of the 26 SEO
landing families, the recruiter directory, job alerts, languages, change-email
and email unsubscribe are all live. What remains is four low-value landing
families that each need a new endpoint, plus two inbound mail webhooks.

---

## Blockers in auth

### 1. ~~There is no email/password login~~ — fixed 2026-08-13

Was: `/api/v1/auth/` had no `login/` endpoint, and
`site/src/routes/login/+page.svelte` rendered only a "Sign in with Google"
link. A user could register with a password, verify their email, and then have
no way to sign in.

Now: `POST /api/v1/auth/login/` (`LoginSerializer` + `views.login`) returns
JWTs in the body only, and the login page has an email/password form posting
to a `+page.server.ts` action that writes them to HttpOnly cookies. Employer
accounts are pointed at the recruiter login; unverified accounts at email
verification. 9 tests in `api/v1/auth/tests.py`.

**Found while building it:** `social/auth_backend.py:PasswordlessAuthBackend`
is *first* in `AUTHENTICATION_BACKENDS` and returns the user **without
checking anything** when handed a falsy password — confirmed against the dev
database, `authenticate(username=<real user>, password='')` returns that user.
Any `authenticate()` call reachable with a blank password is an account
takeover.

It is not exploitable through the API: DRF's `CharField` rejects `""` before
`validate()` runs on both the recruiter endpoint and the new one, and the new
serializer adds an explicit guard plus a regression test. Its only consumers
are three legacy views that call `authenticate(username=…)` with no password
(`jobsp/views.py:216`, `pjob/views.py:2437,2465`), all slated for deletion;
`social/views.py:113` already names `ModelBackend` explicitly. So it can drop
out of `AUTHENTICATION_BACKENDS` when those views go. Left in place pending
that decision — see `tasks/todo.md`.

### 2. ~~`/forgot-password/` and `/reset-password/` are fake~~ — fixed 2026-08-13

Was: neither page had a `+page.server.ts`, and both submit handlers were a
`console.log` followed by `setTimeout(1500)` and a success message. They sent
nothing. `reset-password` also ran a `validateToken()` that resolved to `true`
after a 500ms sleep, so every link looked valid until submitted.

Now both post to `+page.server.ts` actions calling the endpoints that already
existed. `forgot-password` renders one "check your email" state regardless of
whether the account exists, preserving the endpoint's deliberate
anti-enumeration behaviour. `reset-password` derives its invalid-token state
from the two things that can actually know — no `?token=` in the URL, or a
submit the server rejected — and surfaces Django's password-validator messages
verbatim.

**Also fixed:** `settings.SITE_FRONTEND_URL` was **never defined**.
`send_password_reset_email` read it through `hasattr()` with a hardcoded
`http://localhost:5173` fallback, so every password-reset email in production
would have linked to localhost. It is now a real setting
(`SITE_FRONTEND_URL`, env-overridable) read directly, so a missing value fails
loudly instead of silently mailing a dead link.

---

## The SEO landing pages — 23 of 26 built

A job board's organic traffic is these pages, and none of them existed in
`site/` before 2026-08-13.

**23 of 26 are now live**, over a shared engine: `site/src/lib/server/landing.ts`
plus `JobLandingPage.svelte` (listings) and `FacetDirectory.svelte`
(directories). The 3 left are unticked in the table below, and all three were
dropped rather than deferred — each needs a new backend endpoint to serve a
page with no organic value (see "Not needed").

| Django URL | View | Kind |
| --- | --- | --- |
| ✅ `/jobs-in-{location}/` | `job_locations` | listing — **done** |
| ✅ `/{skill}-jobs/` | `job_skills` | listing — **done** |
| ✅ `/jobs-for-{skill}/` | `job_skills` | **301 → `/{skill}-jobs/`** |
| ✅ `/{industry}-industry-jobs/` | `job_industries` | listing — **done** |
| ✅ `/jobs-for-{industry}-industry/` | `job_industries` | **301 → `/{industry}-industry-jobs/`** |
| ✅ `/{company}-job-openings/` | `each_company_jobs` | listing — **done** |
| ✅ `/walkin-jobs/` | `walkin_jobs` | listing — **done** |
| ✅ `/{skill_name}-walkins/` | `skill_location_walkin_jobs` | listing — **done** |
| ✅ `/walkins-in-{city}/` | `skill_location_walkin_jobs` | listing — **done** |
| ✅ `/internship-jobs/` | `internship_jobs` | listing — **done** |
| ✅ `/internship-jobs-in-{location}/` | `city_internship_jobs` | listing — **done** |
| ✅ `/government-jobs/` | `government_jobs` | listing — **done** |
| ✅ `/full-time-jobs/` | `full_time_jobs` | listing — **done** |
| ✅ `/fresher-jobs-in-{city}/` | `location_fresher_jobs` | listing — **done** |
| ✅ `/{skill_name}-fresher-jobs/` | `skill_fresher_jobs` | listing — **done** |
| ✅ `/{skill_name}-fresher-jobs-in-{city_name}/` | `skill_location_wise_fresher_jobs` | listing — **done** |
| ✅ `/{skill}-jobs-in-{city}/` | `search.views.custome_search` | listing — **done**, 5,924 sitemap URLs |
| ✅ `/{skill}-walkins-in-{city}/` | `search.views.custom_walkins` | listing — **done**, 1,128 pairs |
| `/{job_type}-jobs-by-skills/` | `fresher_jobs_by_skills` | index |
| `/{job_type}-by-location/` | `jobs_by_location` | index |
| ✅ `/jobs-by-skill/` | `jobs_by_skill` | directory — **done** |
| ✅ `/jobs-by-industry/` | `jobs_by_industry` | directory — **done** |
| ✅ `/jobs-by-degree/` | `jobs_by_degree` | directory — **done** |
| `/jobposts/year/{y}/month/{m}/date/{d}/` | `jobposts_by_date` | archive |
| ✅ `/recruiters/` | `recruiters` | directory — **done**, 5,340 recruiters |
| ✅ `/recruiters/{recruiter_name}/` | `recruiter_profile` | profile — **done** |

**The listings need essentially no backend work.** `GET /api/v1/jobs/` already
accepts `location`, `skills`, `industry` and `job_type` slug filters
(`JobFilter`, `api/v1/jobs/views.py:74`). A bogus slug returns 400, which maps
cleanly to a hard 404 — important, because a soft-404 empty page is penalised.

Three backend changes were needed along the way:

- **`CityListSerializer` had no `slug`** — it returned
  `id/name/state_name/country_name`, so `/jobs-in-<slug>/` could not recover
  the city name. Added.
- **`filter-options` capped `locations`/`skills` at 50**, so it could not
  enumerate 589 skills for `/jobs-by-skill/`. It now takes `?limit=`, default
  50 (sidebar behaviour unchanged), `limit=0` for everything.
- **`JobFilter` had no `company` filter** — see below. This was a live bug, not
  just a gap.

### `?company=` was silently ignored

`site/`'s company detail page calls `GET /api/v1/jobs/?company=<id>`, but
`company` was never declared on `JobFilter`, and **django-filter drops params
it does not know about**. Measured before the fix:

```
/api/v1/jobs/                    12770
/api/v1/jobs/?company=11551      12770   <- should be 10
/api/v1/jobs/?company=99999999   12770   <- no such company
```

So `/companies/<slug>/` presented the whole board as that company's openings.
`company` and `company_slug` are now real filters, covered by
`CompanyFilterTests` in `api/v1/jobs/tests.py`.

`jobposts_by_date` still needs a new endpoint and the two `{job_type}-by-*`
indexes need job_type-scoped facet counts. `recruiters/` shipped 2026-08-13 —
see below.

### The recruiter directory

5,340 recruiters have a live job, a larger crawlable surface than the 4,089
company pages. `GET /api/v1/recruiters/` and `/recruiters/<username>/` back
`/recruiters/` and `/recruiters/[username]/`.

Two things the legacy version got wrong, not reproduced:

- It listed **every** active recruiter ordered by post count, which put
  thousands of zero-job profiles into the crawlable set. The API restricts to
  accounts with at least one *live* job.
- The A–Z filter was a `POST` (`alphabet_value`) against a full page reload, so
  no letter bucket was reachable by a crawler. It is now `?letter=`.

`JobFilter` gained a `recruiter` filter (case-insensitive, matching the legacy
`username__iexact`) so the profile pages can list that recruiter's jobs.

**The first build returned an empty directory.** The legacy view filters
`user_type in (RR, AR, AA)`; those were consolidated into a single `EM`
(`peeldb.models.USER_TYPE`, "Simplified from RR, RA, AA, AR"), and all 5,345
accounts with a live job now carry it.

### The biggest single family: `/{skill}-jobs-in-{city}/` — built 2026-08-13

`SkillLocationSitemap` advertises **5,924** of these to Google, more than every
other landing family put together. It was missed by the first audit because it
lives in `search/`, not `pjob/`:

```
jobsp/urls.py  ^(?P<skill_name>[-\w]+)-jobs-in-(?P<city_name>[-\w]+)/$
               → search.views.custome_search
```

Despite living in the search app it never touched Elasticsearch — it ran
through `pjob.refine_search.refined_search`, which is plain ORM, so it was one
of the few legacy pages still working. (`search/`'s six `*_auto_search`
autocomplete endpoints *do* use `SearchQuerySet` and are dead.)

No backend work was needed: `GET /api/v1/jobs/?skills=<slug>&location=<slug>`
already composes, so the route is the same shape as
`[skill]-fresher-jobs-in-[city]` minus the `max_experience=0`.

**Route collisions were the real risk**, since `[skill]-jobs-in-[city]` can in
principle swallow four existing routes. SvelteKit resolves by specificity and
all four still win, verified at runtime rather than assumed:

| URL | Resolves to | |
| --- | --- | --- |
| `/jobs-in-hyderabad/` | `jobs-in-[city]` | ✅ |
| `/fresher-jobs-in-hyderabad/` | `fresher-jobs-in-[city]` | ✅ |
| `/internship-jobs-in-hyderabad/` | `internship-jobs-in-[city]` | ✅ |
| `/java-fresher-jobs-in-hyderabad/` | `[skill]-fresher-jobs-in-[city]` | ✅ |

The greedy-match case also resolves correctly with hyphens on **both** sides —
`/basic-computer-skills-jobs-in-tamil-nadu/` splits at the right `-jobs-in-`.

Counts were checked against the API to prove the filters bind (the `?company=`
bug shape), all exact and all distinct from the 12,770 board total:

```
/java-jobs-in-bangalore/                          184 = 184
/basic-computer-knowledge-jobs-in-kolkata/        295 = 295
/java-jobs-in-hyderabad/                          168 = 168
/engineering-jobs-in-panipat-haryana-shamli-up/     5 =   5
/basic-computer-skills-jobs-in-tamil-nadu/          7 =   7
```

Bogus skill, bogus city and both-bogus all hard-404; page 11 of a 10-page
facet 404s; `?page=0` and `?page=abc` collapse to page 1.

### Paginated canonicals — fixed 2026-08-13

`JobLandingPage.svelte` emitted `<link rel="canonical">` pointing at page 1 on
*every* page of a series, so `/java-jobs-in-bangalore/?page=2` declared itself a
duplicate of page 1. Google's guidance is that paginated pages self-canonicalise;
as written, the job links that appear only on pages 2..N had no crawlable path
in through these routes — on that facet, 164 of 184 jobs.

Now `href={pageHref(currentPage)}`, which affects all **20** landing routes.
Page 1 still canonicalises to the clean URL rather than `?page=1`:

```
/java-jobs-in-bangalore/           canonical=/java-jobs-in-bangalore/          next=?page=2
/java-jobs-in-bangalore/?page=2    canonical=?page=2   prev=(clean)            next=?page=3
/java-jobs-in-bangalore/?page=10   canonical=?page=10  prev=?page=9            (no next)
```

### The sitemaps were broken two ways — both fixed 2026-08-13

Both pre-existing and unrelated to the rewrite.

**1. `/sitemap-static.xml` returned a 500.** `StaticPagesSitemap.items()` listed
`jobs_by_location` and `fresher_jobs_by_skills`, but both URL patterns take a
required `job_type`, so the bare `reverse(item)` in `location()` raised
`NoReverseMatch`. Dropped from the list rather than given a filler `job_type` —
they are the two families in the table above that nothing has migrated, so
advertising them points crawlers at pages on their way out.

**2. Every `<loc>` in every section said `example.com`.** `django.contrib.sitemaps`
resolves the host through `Site.objects.get_current()`, and the Sites row had
never been moved off Django's stock `example.com` — so all ~27,000 URLs, plus
the index's links to the sections themselves, advertised the wrong domain. The
comment in `jobsp/urls.py` asserting "Domain (peeljobs.com) configured via
Django Site framework (SITE_ID=1)" was simply untrue.

Nothing else in the codebase reads `Site.objects` or `get_current()`, so the row
had no other job. Fixed at two levels, because the two views resolve the host
differently:

- `PeelJobsSitemap.get_domain()` now returns `settings.SITE_DOMAIN` (new,
  env-overridable, defaults to `peeljobs.com`). This is the documented hook and
  covers every section.
- The **index** view resolves through `get_current_site(request)` and has no
  equivalent hook, so it reads the database row regardless. Migration
  `peeldb/0074_set_site_domain` syncs that row from `settings.SITE_DOMAIN`.

Settings is the source of truth; the row is a materialised copy.

After both fixes: 8/8 sections return 200, **27,160 URLs, 0 on the wrong
domain**.

### There is no legacy SEO copy to port

The legacy pages built their meta through `mpcomp.views.get_meta()`, which
renders Django template strings out of the `MetaData` table. **That table has
0 rows** — so every legacy landing page would render a blank title and
description today. `City.meta_title`/`meta_description`/`page_content` are
empty across all 113 rows, and only 76 of 866 skills have a `meta_title`.

So the new pages generate their own titles, descriptions and H1s from the
facet name and the live job count. The 76 skill overrides are not wired up;
doing so would need them exposed on the API.

### The fresher pages do not use `fresher=true`

`JobPost.fresher` is `True` on **1 of 12,770** live jobs — the flag was never
adopted. The real signal is `min_year = 0`, which covers **6,936** and is
reachable through the API as `max_experience=0`. The four fresher families use
that; on the flag they would all have shipped empty.

## ✅ Features migrated 2026-08-13 (13 routes)

Usage data drove these, and it flipped several earlier "low value" calls.

| Feature | Rows in the live DB | What shipped |
| --- | --- | --- |
| **Job alerts** | 64,673 alerts / 63,985 emails — but only **822 verified** | `POST /api/v1/alerts/{subscribe,verify,unsubscribe}/`, `/job-alerts/` form, `/job-alerts/verify/`. `JobAlert` has **no user FK**, so six authenticated `candidate/alert/*` routes collapse into one public form plus a verification callback |
| **Languages** | 6,283 `UserLanguage` rows (~28% of seekers) | `/api/v1/profile/languages/` CRUD + `language-options/`, `/profile/languages/` page, nav tab. `read`/`write`/`speak` kept as independent booleans — flattening to one level would lose data |
| **Change email** | — | `User.pending_email` (`0075`), `POST /auth/change-email/` + `verify-email-change/`, Account & Security section on the profile |

**The 98.7% unverified rate on alerts is the real finding.** The weekly digest
only sends to `is_verified=True`, so 63,851 subscriptions are inert. That is a
bug worth more than the migration was.

### Change email: why it is not a one-line PATCH

`email` is `USERNAME_FIELD`, so it is the login identifier. It must not move
until a token mailed *to the new address* comes back — otherwise a typo strands
the account between two inboxes it cannot reach. `username` is updated in
lockstep because it mirrors the email for **22,037 of 22,131** job seekers and
is `unique`; a stale copy would block whoever later registers with the freed
address.

**Found while building it:** there was no change-*password* UI either. The
endpoint existed and nothing in `site/` called it, though this document
previously claimed the feature was migrated. Both now live in the same section.

## Email infrastructure — 4 of 6 migrated

**This was never optional.** `CELERY_BEAT_SCHEDULE` runs
`dashboard.tasks.applicants_job_notifications` every Monday at 09:00, the
templates it renders link to these handlers, and **2,785 users have already
used unsubscribe** — so the mechanism is demonstrably in use. Continuing to mail
64,673 alerts and 60,805 subscribers with a dead unsubscribe link is a
compliance problem, not a UX one.

| Django URL | Status |
| --- | --- |
| ✅ `/unsubscribe_email/{email_type}/{message_id}/` | `POST /api/v1/alerts/unsubscribe/` + `/unsubscribe/` page |
| ✅ `/email-unsubscribe/{message_id}/` | same endpoint, `type=user` |
| ✅ `/unsubscribe/{email}/` | same endpoint, `type=subscriber` |
| ✅ `/user_subscribe/` | `POST /api/v1/alerts/subscribe/` |
| ✅ `/bounces/` | ported to `api/v1/webhooks/views.ses_bounce`, still answering on the legacy path |
| 🚫 `/process-email/` | dropped 2026-08-13, confirmed not wanted — see below |

One endpoint covers all three unsubscribe targets. `type` deliberately keeps the
legacy `alert` / `subscriber` / `user` values, because those strings are baked
into `/unsubscribe_email/<email_type>/...` links sitting in mail that has
already been delivered.

Two behaviours are deliberate: the unsubscribe applies on **GET**, not behind a
confirm button (one-click is what bulk-sender rules expect), and a **second
click still returns success** — an already-redeemed code means the person is
unsubscribed, and erroring would tell someone who clicked twice that it had not
worked.

Both inbound webhooks are settled. `/bounces/` moved to `api/v1/webhooks/` and
kept its path, because a live SNS subscription points at it.

`/process-email/` was **dropped**, confirmed 2026-08-13. It parsed an inbound
message body, regex-matched the first email address in it, and if no user held
that address it created a Job Seeker account with `registered_from="Careers"`,
generated a random password and mailed it out — all unauthenticated, with none
of the SNS envelope verification the bounce handler does. Anyone able to POST to
it could mint accounts and trigger mail to arbitrary addresses.

It also never did anything: **zero users** in the 34,775-user production
snapshot have `registered_from="Careers"`, so the path never created a single
account. Nothing in the repo references it — no code, no config, no `.env`.

The `("Careers", "Careers")` choice went too (`peeldb.models.REGISTERED_FROM`,
migration `0078_alter_user_registered_from`). It was the webhook's signature and
had no other writer. Choices are not enforced by Postgres, so the migration
alters no rows and reverses cleanly.

## 🚫 Not needed (12)

| Route(s) | Why |
| --- | --- |
| `candidate/test/experience/` | Dev leftover — `test_experience_view`, never linked |
| `candidate/messages/` | Dropped 2026-08-12. `UserMessage` is referenced nowhere outside `models.py`; nothing writes a message, so an inbox would be permanently empty |
| `candidate/profile/personal_info/edit/`<br>`candidate/profile/basic_profile/edit/` | Duplicates of `personalinfo/edit/` from an abandoned `my_views` rewrite — all three PATCH the same fields |
| `candidate/my/home/` | Duplicate of `candidate/` index |
| `candidate/account-settings/edit/` | Superseded — its fields are on `PATCH /api/v1/profile/` |
| `pjob/jobs/applied_for/` | `user_applied_job` — superseded by `GET /api/v1/jobs/applied/` |
| `pjob/user/reg_success/`<br>`pjob/social/user/update/` | Post-registration interstitials; the SvelteKit flow redirects straight to `/verify-email/` |
| `candidate/resume/info/` | AJAX helper for the legacy modal UI; the resume fields are on `GET /api/v1/profile/` |
| the 24 `-modal/` routes | Not counted here — they are the same features as their non-modal twins (see below) |

### About the `-modal/` routes

`candidate/views/my_views.py` adds 24 `…-modal/` endpoints — `add_project_modal`,
`edit_education_modal`, `delete_skill_modal` and so on. They are an abandoned
in-place rewrite of the same CRUD the non-modal views already did, differing
only in returning a rendered fragment instead of a redirect. They are counted
as **migrated** alongside their twins, because the SvelteKit page covers the
feature; none of them needs separate work.

---

## ✅ Migrated (66 routes / 13 features)

Every row verified against both a live API route and a live SvelteKit page.

| Feature | Legacy routes | API | SvelteKit |
| --- | --- | --- | --- |
| Job list | `pjob:index` (+paged) | `GET /api/v1/jobs/` | `/(site)/jobs/` |
| Job detail | `pjob:job_detail` | `GET /api/v1/jobs/{id}/` | `/(site)/jobs/[id]/` |
| Apply | `pjob:job_apply` | `POST /api/v1/jobs/{id}/apply/` | `/(site)/jobs/[id]/` |
| My applications | `pjob:jobs_applied` | `GET /api/v1/jobs/applied/` | `/(site)/applications/` |
| Companies | `pjob:companies` (+paged) | `GET /api/v1/companies/` | `/(site)/companies/`, `/[id]/` |
| Skill lookup | `pjob:get_skills` | `GET /api/v1/skills/` | — (used by filters) |
| Register | `pjob:register_email` | `POST /api/v1/auth/register/` | `/register/` |
| Email verification | `pjob:user_activation` | `POST /api/v1/auth/verify-email/` | `/verify-email/` |
| Profile view/edit | `candidate:index`, `profile`, `edit_personalinfo`, `edit_professionalinfo`, `edit_profile_description` | `GET/PATCH /api/v1/profile/` | `/(site)/profile/` |
| Education | `add_`/`edit_`/`delete_education` +3 modal | `/api/v1/profile/education/` | `/(site)/profile/education/` |
| Employment | `add_`/`edit_`/`delete_experience` +3 modal | `/api/v1/employment/my-history/` | `/(site)/profile/employment/` |
| Skills | `add_`/`edit_`/`delete_technicalskill` +3 modal | `/api/v1/skills/my-skills/` | `/(site)/profile/skills/` |
| Projects | `add_`/`edit_`/`delete_project` +3 modal | `/api/v1/profile/projects/` | `/(site)/profile/projects/` |
| Certifications | 3 modal routes | `/api/v1/profile/certifications/` | `/(site)/profile/certifications/` |
| Resume & photo | `upload_resume`, `delete_resume`, `upload_profilepic` +4 modal | `/api/v1/profile/upload/`, `/api/v1/profile/resume/delete/` | `/(site)/profile/` |
| Password change | `user_password_change` | `POST /api/v1/auth/change-password/` | `/(site)/profile/` |
| Email prefs + job prefs | `edit_emailnotifications`, `edit_job_preferences` | `PATCH /api/v1/profile/` (`email_notifications`, `is_unsubscribe`, `is_looking_for_job`, `is_open_to_offers`, `notice_period`, `relocation`, `preferred_city`) | `PreferencesSection.svelte` |

Built in the rewrite with no Django ancestor: saved jobs
(`/api/v1/jobs/saved/` → `/(site)/saved/`), certifications, company browsing,
Google OAuth, education lookup endpoints, and the static pages (`/about/`,
`/contact/`, `/help/`, `/pricing/`, `/privacy/`, `/terms/`).

---

## ✅ Resolved since the 2026-08-12 audit

Both items that pass flagged as blocking are fixed:

| Was | Now |
| --- | --- |
| 🔴 JWT in `localStorage`; browser called Django directly | `token-storage.ts` deleted. JWT is in an HttpOnly cookie; the browser calls 27 same-origin `/api/*` forwarders in `site/src/routes/api/` which inject the Bearer header via `hooks.server.ts` |
| 🔴 `(site)/+layout.server.ts` returned `{user: null}` unconditionally | Resolves the user server-side from the cookie; signed-in pages render signed-in HTML on first response |
| 3 pages rendered hardcoded fake data | `/saved/` and `/applications/` wired to real endpoints; `/messages/` deleted |

One deviation from CLAUDE.md survives: the six `/(site)/profile/*` pages load
via `onMount` → proxy rather than `+page.server.ts`. The token never reaches
JS so this is no longer a security issue, but those pages do not SSR.

`site/src/routes/(site)/@u/` is still a stub whose `+page.server.js` returns
`{}`.

---

## The Django apps are deleted — 2026-08-13

`candidate/`, `pjob/`, `search/`, `agency/` and `recruiter/` are gone, along
with `jobsp/views.py`, the template half of `psite/`, and 125 templates.
Django now serves the REST API, transactional email, XML sitemaps and platform
admin, and nothing else. See "Pass 10" in `tasks/todo.md` for what moved and
what was found on the way.

Nothing was redirected: the platform has had no live traffic for years, so
there are no rankings or inbound links to honour.

## Recommended order

1. ~~**Ship email/password login**~~ — done 2026-08-13.
2. ~~**Wire `/forgot-password/` and `/reset-password/`**~~ — done 2026-08-13.
   The auth flow is now complete end to end: register → verify → sign in →
   forget → reset → sign in again.
3. ~~**Build the SEO landing pages**~~ — 19 of 26 done 2026-08-13.
4. ~~**Build `/{skill}-jobs-in-{city}/`**~~ — done 2026-08-13. 20 of 26.
5. ~~**Fix the paginated canonicals**~~ — done 2026-08-13, all 20 routes.
6. ~~**Fix the sitemaps**~~ — done 2026-08-13. `/sitemap-static.xml`'s 500 and
   the `example.com` domain on all 27,160 URLs.
7. ~~**Take a finish/drop call**~~ — taken and acted on 2026-08-13. Job alerts,
   languages, change-email, the recruiter directory, `/{skill}-walkins-in-{city}/`
   and 4 of the 6 email handlers are built; the date archive and the two
   `{job_type}-by-*` indexes are dropped.
8. ~~**Move `/bounces/` and `/process-email/`**~~ — done 2026-08-13. `/bounces/`
   is `api/v1/webhooks/` now, still answering on the same path so the SNS
   subscription keeps working; `/process-email/` was dropped.
9. ~~**Then delete** `candidate/`, `pjob/` and `search/`~~ — done 2026-08-13,
   together with `agency/` and `recruiter/`.

What is left is not migration work:

- **Haystack is still installed with nothing reading it.** `RealtimeSignalProcessor`
  opens a connection to an absent Elasticsearch on every `Skill`/`City`/`User`/
  `JobPost` save. Deliberately deferred, not overlooked.
- **SNS messages to `/bounces/` are unauthenticated.** Carried over from the
  legacy handler; see the module docstring for the two ways to close it.
