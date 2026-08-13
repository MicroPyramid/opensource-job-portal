"""
Generate the Django retirement inventory (docs/django-retirement.md).

Every Django URL is walked out of the live URLconf, annotated with the view and
the templates that view renders, and — with --probe — checked against the
SvelteKit frontends to see whether a replacement actually answers.

The mechanical columns are regenerated on every run, so the doc can be diffed
against reality instead of trusted. The judgement columns (SvelteKit path,
status, disposition) live in MIGRATION_NOTES below, keyed by URL name or by
pattern, so re-running preserves them.

    uv run manage.py retirement_inventory --probe
"""

import ast
import re
from collections import OrderedDict
from functools import cache
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand
from django.urls import get_resolver

# Lifecycle states. A row only moves to DELETED once REDIRECTED holds, because
# retiring a URL that is indexed or sitting in a delivered email is a 404 on
# live traffic, not a no-op.
MIGRATED = "migrated"  # a SvelteKit page serves the equivalent
REDIRECTED = "redirected"  # Django 301s to it
DELETED = "deleted"  # view + templates removed
TODO = "not started"  # checked by hand — nothing serves this yet
PARTIAL = "partial"  # frontend exists but is mock / incomplete
DROP = "drop"  # feature retired outright — no replacement is coming
KEEP = "keep"  # permanent — never deleted

# The default for any route with no MIGRATION_NOTES entry. It means "nobody has
# assessed this yet", NOT "no replacement exists" — a lot of these turn out to
# be already migrated once someone looks. Never act on this state; re-check the
# route and move it to a real one first.
UNVERIFIED = "unverified"

# Kept for good, keyed by the app that owns the include. The finish line is
# "Django serves the API, transactional email, sitemaps and platform admin" —
# not zero templates.
KEEP_BY_OWNER = {
    "admin": "Django admin",
    "api": "REST API consumed by both SvelteKit frontends",
    "v1": "REST API consumed by both SvelteKit frontends",
    "dashboard": "platform admin — required, explicitly out of scope for deletion",
    "celery-check": "Celery health check",
    "mp_celery_monitor": "Celery health check",
    # Verified 2026-08-12: this is admin surface, not legacy. The platform
    # admin nav links it (templates/dashboard/base.html:333 reverses
    # tickets:admin_tickets_list), dashboard/urls.py routes company_tickets,
    # and templates/dashboard/tickets/*.html render it. It was only grouped
    # with the legacy apps because it lives outside dashboard/.
    "tickets": "support tickets — reached from the platform admin nav",
}

# Kept for good, keyed by view module. Covers routes registered at the root
# URLconf rather than through an include, so they have no owning app.
KEEP_BY_VIEW = {
    "rest_framework": "DRF browsable API / auth",
    "rest_framework_simplejwt": "JWT token endpoints",
    "drf_spectacular": "OpenAPI schema + docs",
    "django.contrib.sitemaps": "sitemap.xml — SEO, server-side by design",
    "django.contrib.admin": "Django admin",
    "django.views.static": "dev-only static/media serving, DEBUG-gated",
    "django_celery_beat": "Celery beat admin",
    "schema_viewer": "dev-only, DEBUG-gated",
}

# Judgement columns, preserved across regeneration. Keyed by namespaced URL
# name where one exists, otherwise by the raw pattern.
# (sveltekit_path, status, note)
MIGRATION_NOTES = {
    # --- job seeker auth: fully served by site/ ---
    "login": ("/login/", MIGRATED, "site/ + /api/v1/auth/login"),
    "register": ("/register/", MIGRATED, "site/ + /api/v1/auth/register"),
    "forgot_password": ("/forgot-password/", MIGRATED, "site/"),
    "set_password": ("/reset-password/", MIGRATED, "site/"),
    "get_out": ("/", MIGRATED, "site/ clears cookies"),
    "user_activation": ("/verify-email/", MIGRATED, "site/"),
    # Migrated, but NOT deletable on its own: templates/base.html:339 reverses
    # this name, and base.html is extended by 44 templates including 404.html
    # and 500.html (the handler404/handler500 targets). It goes when the
    # legacy job seeker templates go, not before. Verified 2026-08-12.
    "social:google_login": (
        "/login/",
        MIGRATED,
        "/api/v1/auth/google/* — blocked on base.html:339",
    ),
    "auth_return": ("/auth/google/callback/", MIGRATED, "/api/v1/auth/google/*"),
    # --- public browse: partially served ---
    "job_list": ("/jobs/", MIGRATED, "site/ (site) /jobs/"),
    "job_detail": ("/jobs/[id]/", MIGRATED, "slug + id lookup both work"),
    "companies": ("/companies/", MIGRATED, "site/ (site) /companies/"),
    "company_jobs": ("/companies/[id]/", PARTIAL, "company page exists, not this URL"),
    "contact": ("/contact/", MIGRATED, "/api/v1/contact/submit/"),
    "pages": ("/about/ /privacy/ /terms/ /help/", MIGRATED, "static pages in site/"),
    # --- SEO landing pages: the bulk of the remaining work ---
    "custome_search": ("", TODO, "14k sitemap URLs — 404 on site/"),
    "custom_walkins": ("", TODO, "404 on site/"),
    "job_skills": ("", TODO, "389 sitemap URLs — 404 on site/"),
    "job_locations": ("", TODO, "112 sitemap URLs — 404 on site/"),
    "job_industries": ("", TODO, "404 on site/"),
    "skill_fresher_jobs": ("", TODO, "404 on site/"),
    "location_fresher_jobs": ("", TODO, "404 on site/"),
    "skill_location_wise_fresher_jobs": ("", TODO, "3.8k sitemap URLs"),
    "skill_walkin_jobs": ("", TODO, "404 on site/"),
    "location_walkin_jobs": ("", TODO, "404 on site/"),
    "city_internship_jobs": ("", TODO, "404 on site/"),
    "walkin_jobs": ("", TODO, "404 on site/"),
    "internship_jobs": ("", TODO, "404 on site/"),
    "government_jobs": ("", DROP, "feature not carried over — needs 410 or 301"),
    "full_time_jobs": ("", TODO, "404 on site/"),
    "fresher_jobs_by_skills": ("", TODO, "404 on site/"),
    "jobs_by_location": ("", TODO, "404 on site/"),
    "jobs_by_skill": ("", TODO, "404 on site/"),
    "jobs_by_industry": ("", TODO, "404 on site/"),
    "jobs_by_degree": ("", TODO, "404 on site/"),
    "jobposts_by_date": ("", TODO, "no equivalent planned — confirm it can 410"),
    "recruiters": ("", TODO, "no equivalent in site/"),
    "recruiter_profile": ("", TODO, "no equivalent in site/"),
    # --- job seeker account: API exists, site/ pages render mock data ---
    "my:index": ("/profile/", PARTIAL, "site/ page is mock — no server load"),
    "my:profile": ("/profile/", PARTIAL, "API ready: /api/v1/profile/"),
    "pjob:job_apply": ("", TODO, "/api/v1/jobs/{id}/apply/ exists, unused by site/"),
    "pjob:jobs_applied": ("/applications/", PARTIAL, "site/ page is mock"),
    "pjob:user_applied_job": ("/applications/", PARTIAL, "site/ page is mock"),
    # --- alerts + unsubscribe: must keep resolving for delivered email ---
    "unsubscribe": ("", TODO, "linked from delivered email — needs permanent 301"),
    "applicant_unsubscribing": ("", TODO, "linked from delivered email"),
    "applicant_email_unsubscribing": ("", TODO, "linked from delivered email"),
    "alert_subscribe_verification": ("", TODO, "linked from delivered email"),
    "user_subscribe": ("", TODO, "no alerts API yet"),
    # --- recruiter: migration closed 2026-08-12, all 61 legacy routes have a
    # verdict (33 migrated / 27 dropped / 1 Django). See
    # docs/recruiter-migration-status.md. `index` and `profile` were deleted
    # once nothing reversed them; the three below survive because live
    # templates still reverse the names. The hardcoded host is fixed — they
    # read settings.RECRUITER_FRONTEND_URL.
    "recruiter:dashboard": (
        "/dashboard/",
        REDIRECTED,
        "reversed by recruiter_404.html",
    ),
    "recruiter:list": (
        "/dashboard/jobs/",
        REDIRECTED,
        "reversed by the agency client templates",
    ),
    "recruiter:new_user": (
        "/login/",
        REDIRECTED,
        "reversed by base.html + post_job.html",
    ),
    # how_it_works (recruiter: and agency:) deleted 2026-08-12. It extended
    # recruiter/index.html, deleted back in d6763e9, so every request had been a
    # TemplateDoesNotExist 500 — and no template reversed either name. Same
    # shape as interview_location.
    "post_job": (
        "/signup/",
        REDIRECTED,
        "view + template deleted 2026-08-12; name kept, base.html reverses it",
    ),
}

# Sample values used to turn a regex pattern into a concrete probeable path.
SAMPLES = {
    "skill_name": "python",
    "skill": "python",
    "city_name": "hyderabad",
    "location": "hyderabad",
    "company_name": "google",
    "industry": "information-technology",
    "job_type": "fresher",
    "page_num": "1",
    "page_name": "about",
    "job_title_slug": "python-developer",
    "job_id": "1",
    "post_id": "1",
    "user_id": "1",
    "recruiter_name": "recruiter",
    "year": "2026",
    "month": "01",
    "date": "01",
}

# Where each Django app's replacement lives, for the probe.
SITE = "http://localhost:5173"
RECRUITER = "http://localhost:5174"
RECRUITER_MODULES = {"recruiter", "agency"}

APP_ORDER = [
    "jobsp",
    "pjob",
    "search",
    "psite",
    "candidate",
    "recruiter",
    "api_recruiter",
    "agency",
    "tickets",
    "social",
]

APP_TITLES = {
    "jobsp": "Root URLconf — auth, SEO landing pages, static pages",
    "pjob": "Job browsing, job detail, apply",
    "search": "Search + autocomplete",
    "psite": "Static pages, contact, sitemap page",
    "candidate": "Job seeker profile, alerts, messages",
    "recruiter": "Recruiter (legacy — superseded by recruiter/)",
    "api_recruiter": "Legacy recruiter API — superseded by /api/v1/recruiter/",
    "agency": "Agency management",
    "tickets": "Support tickets",
    "social": "OAuth login",
}


def walk(resolver, prefix="", namespace=None, owner=None):
    """
    Yield (path, url_name_with_namespace, pattern_obj, owner) per leaf route.

    `owner` is the app that owns the include the route came through, which is
    what decides whether it is legacy — not the view's module. Django admin
    registers routes pointing at django.views.generic.RedirectView, and the
    legacy recruiter app does too; only the owner tells them apart.
    """
    for entry in resolver.url_patterns:
        pattern = prefix + str(entry.pattern)
        if hasattr(entry, "url_patterns"):
            ns = entry.namespace or namespace
            # First include from the root wins: /api/v1/jobs/ is owned by the
            # api app, not by the nested "jobs" include inside it.
            yield from walk(
                entry, pattern, ns, owner or entry.app_name or entry.namespace
            )
        else:
            name = entry.name
            if name and namespace:
                name = f"{namespace}:{name}"
            yield pattern, name, entry, owner


def concretize(pattern):
    """
    Turn a Django route into a concrete path, or return None if it cannot be
    made concrete (leftover regex metacharacters would make the probe a lie).
    """
    out = []
    i = 0
    while i < len(pattern):
        if pattern.startswith("(?P<", i):
            close = pattern.index(">", i)
            group_name = pattern[i + 4 : close]
            # skip to the balanced closing paren of this group
            depth = 1
            j = close + 1
            while j < len(pattern) and depth:
                if pattern[j] == "(":
                    depth += 1
                elif pattern[j] == ")":
                    depth -= 1
                j += 1
            out.append(SAMPLES.get(group_name, "sample"))
            i = j
            continue
        if pattern[i] == "<":  # path() converter, e.g. <int:user_id>
            close = pattern.index(">", i)
            converter = pattern[i + 1 : close]
            group_name = converter.split(":")[-1]
            out.append(SAMPLES.get(group_name, "1"))
            i = close + 1
            continue
        if pattern[i] == "\\":  # escaped literal
            i += 1
            if i < len(pattern):
                out.append(pattern[i])
                i += 1
            continue
        if pattern[i] in "^$":
            i += 1
            continue
        out.append(pattern[i])
        i += 1

    path = "".join(out)
    if re.search(r"[\[\]()+*?|]", path):
        return None
    return "/" + path.lstrip("/")


@cache
def templates_for(lookup_str):
    """
    Best-effort: the .html literals appearing inside the view's own body.
    Views that render through a helper will under-report; the doc says so.
    """
    module_path, _, attr = lookup_str.rpartition(".")
    try:
        module = __import__(module_path, fromlist=["*"])
        source_file = Path(module.__file__)
        tree = ast.parse(source_file.read_text())
    except (ImportError, OSError, SyntaxError, ValueError):
        return ()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            if node.name != attr:
                continue
            found = {
                child.value
                for child in ast.walk(node)
                if isinstance(child, ast.Constant)
                and isinstance(child.value, str)
                and child.value.endswith(".html")
            }
            return tuple(sorted(found))
    return ()


def probe(url, timeout=10):
    try:
        request = Request(url, method="HEAD")
        with urlopen(request, timeout=timeout) as response:
            return str(response.status)
    except URLError as exc:
        reason = getattr(exc, "code", None)
        return str(reason) if reason else "down"
    except OSError:
        return "down"


class Command(BaseCommand):
    help = "Generate docs/django-retirement.md from the live URLconf"

    def add_arguments(self, parser):
        parser.add_argument(
            "--probe",
            action="store_true",
            help="Check each route against the SvelteKit frontends (needs them running)",
        )
        parser.add_argument(
            "--output",
            default="../docs/django-retirement.md",
            help="Path to write, relative to backend/",
        )

    def load_db_samples(self):
        """
        Probe with real slugs where the database can supply them. A synthetic
        slug 404s for reasons that have nothing to do with the migration, which
        makes the probe column worthless.
        """
        from peeldb.models import City, Company, Industry, JobPost, Skill

        lookups = (
            ("skill_name", Skill),
            ("skill", Skill),
            ("city_name", City),
            ("location", City),
            ("company_name", Company),
            ("industry", Industry),
        )
        for key, model in lookups:
            try:
                slug = (
                    model.objects.exclude(slug="")
                    .values_list("slug", flat=True)
                    .first()
                )
            except Exception:  # a missing table must not break the doc
                slug = None
            if slug:
                SAMPLES[key] = slug.strip("/")

        # job_detail splits the URL into title + trailing id, so pick a job whose
        # stored slug actually follows that convention or the probe is meaningless.
        for slug, job_id in (
            JobPost.objects.filter(status="Live")
            .exclude(slug="")
            .values_list("slug", "id")[:200]
        ):
            bare = slug.strip("/")
            if bare.endswith(f"-{job_id}"):
                SAMPLES["job_title_slug"] = bare[: -len(f"-{job_id}")]
                SAMPLES["job_id"] = str(job_id)
                break

    def handle(self, *args, **options):
        self.load_db_samples()

        rows = []
        for pattern, name, entry, owner in walk(get_resolver()):
            lookup = entry.lookup_str
            keep_reason = KEEP_BY_OWNER.get(owner) or next(
                (why for mod, why in KEEP_BY_VIEW.items() if lookup.startswith(mod)),
                None,
            )
            # Root-level routes have no owning app; fall back to the view module.
            module = owner or lookup.split(".")[0]
            sveltekit, status, note = MIGRATION_NOTES.get(name or pattern, ("", "", ""))
            if keep_reason:
                status, note = KEEP, keep_reason
            rows.append(
                {
                    "pattern": pattern,
                    "name": name or "",
                    "module": module,
                    "view": lookup,
                    "templates": templates_for(lookup) if not keep_reason else (),
                    "sveltekit": sveltekit,
                    "status": status or UNVERIFIED,
                    "note": note,
                    "probe": "",
                    "concrete": concretize(pattern),
                }
            )

        self.inherit_from_named_sibling(rows)

        if options["probe"]:
            self.stdout.write("Probing frontends...")
            base_cache = {}
            for row in rows:
                if row["status"] == KEEP or not row["concrete"]:
                    continue
                base = RECRUITER if row["module"] in RECRUITER_MODULES else SITE
                if base not in base_cache:
                    base_cache[base] = probe(base + "/")
                if base_cache[base] == "down":
                    row["probe"] = "server down"
                    continue
                row["probe"] = probe(base + row["concrete"])

        output = Path(options["output"]).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.render(rows, probed=options["probe"]))
        self.stdout.write(self.style.SUCCESS(f"Wrote {output} ({len(rows)} routes)"))

    @staticmethod
    def inherit_from_named_sibling(rows):
        """
        Most routes here are unnamed pagination variants of a named route
        (/government-jobs/ and /government-jobs/<page_num>/ hit the same view).
        Leaving those `unverified` overstates how much is unassessed, so let
        them inherit their named sibling's verdict.
        """
        assessed = {
            row["view"]: row
            for row in rows
            if row["status"] not in (UNVERIFIED, KEEP) and row["name"]
        }
        for row in rows:
            if row["status"] != UNVERIFIED:
                continue
            sibling = assessed.get(row["view"])
            if sibling:
                row["sveltekit"] = sibling["sveltekit"]
                row["status"] = sibling["status"]
                row["note"] = f"same view as `{sibling['name']}`"

    def render(self, rows, probed):
        retire = [r for r in rows if r["status"] != KEEP]
        keep = [r for r in rows if r["status"] == KEEP]

        counts = OrderedDict()
        for row in retire:
            counts[row["status"]] = counts.get(row["status"], 0) + 1

        out = [
            "# Django retirement inventory",
            "",
            "> Generated by `uv run manage.py retirement_inventory --probe`.",
            "> Mechanical columns are regenerated from the live URLconf on every run;",
            "> re-run it to check the doc against reality rather than trusting it.",
            "> Judgement columns live in `MIGRATION_NOTES` in that command.",
            "",
            "## The finish line",
            "",
            "Django keeps serving the REST API, transactional email, sitemaps and",
            "platform admin. Everything else is retired. Zero templates is **not**",
            "the goal — see [Keep (permanent)](#keep-permanent).",
            "",
            "## Read the status column as provisional",
            "",
            f"Anything marked `{UNVERIFIED}` has **not been assessed** — it is the",
            "default for every route this generator has no hand-written note for. It",
            "does not mean no replacement exists. A lot of these are already migrated;",
            "the first pass simply did not check them one by one.",
            "",
            "**So: re-verify each route at the moment you touch it.** Confirm what",
            "actually serves it now, move it to a real state, and record that in",
            "`MIGRATION_NOTES` so the next regeneration keeps the answer. Treat every",
            "state older than the work you are doing as a hint, not a fact.",
            "",
            "## There is no live traffic",
            "",
            "The platform has been down for years. No rankings survive, no inbound",
            "links need honouring, and mail sent before it went down is not being",
            "clicked. That removes the constraint this document was first built",
            "around: **retired URLs do not need redirects.** They can just go.",
            "",
            "It also changes what this inventory is for. It is not a parity checklist",
            "against a running system — it is a record of what the old product did, so",
            "you can decide what the relaunched one should have. The legacy views are a",
            "reference implementation: read them to recover how a feature worked, then",
            "delete them. `drop` is the expected outcome for most rows, not the",
            "exception.",
            "",
            "Working unsubscribe links are still a requirement for any mail the *new*",
            "stack sends. That is a forward obligation on the new stack, not a reason",
            "to keep the old views.",
            "",
            "## Lifecycle",
            "",
            "| State | Meaning |",
            "| --- | --- |",
            f"| `{UNVERIFIED}` | Not assessed yet — check before acting on it |",
            f"| `{TODO}` | Checked by hand: nothing serves this yet |",
            f"| `{PARTIAL}` | A page exists but renders mock data or misses cases |",
            f"| `{MIGRATED}` | A SvelteKit page serves the equivalent, verified |",
            f"| `{REDIRECTED}` | Django 301s the old URL to it |",
            f"| `{DELETED}` | View + templates removed |",
            f"| `{DROP}` | Feature not being carried over — delete, no replacement |",
            f"| `{KEEP}` | Permanent — never deleted |",
            "",
            f"`{DROP}` is a separate decision from `{TODO}`: the feature is going away",
            "rather than moving. With nothing live, dropping a route costs nothing but",
            "the decision itself.",
            "",
            "**Delete in one pass, not route by route.** Templates reverse each other's",
            "URL names, so removing one view breaks `{% url %}` in templates that still",
            "render — that is why `/jobs/{slug}/` currently 500s (`agency:` names were",
            "deleted out from under `job_detail_tailwind.html`). Removing the whole",
            "legacy set together avoids that entirely: nothing is left to hold a",
            "dangling reference.",
            "",
            "The constraint that does survive is the **import graph**. Code that stays",
            "imports code that goes — `dashboard/tasks.py` imports `mpcomp`, and the API",
            "imports `dashboard.tasks.send_email`. That is a compile-time problem, so",
            "`manage.py check` plus the test suite is the gate, not traffic analysis.",
            "",
            "### What survivors currently reach into (verified 2026-08-12)",
            "",
            "`api/` is clean — its only cross-app import is `dashboard.tasks.send_email`,",
            "and `dashboard` is permanent. Everything else below has to be relocated",
            "before the app it points at can be deleted.",
            "",
            "| Survivor | Reaches into | For |",
            "| --- | --- | --- |",
            "| `dashboard/views/auth_views.py` | `pjob.views` | `months` |",
            (
                "| `dashboard/views/job_management.py` | `recruiter.forms`, "
                "`recruiter.views` | `MONTHS`, `YEARS`, `JobPostForm`, 4 job helpers |"
            ),
            "| `dashboard/views/company_management.py` | `recruiter.forms` | `MenuForm` |",
            (
                "| `peeldb/templatetags/page_tags.py` | `candidate.forms`, "
                "`recruiter.forms` | `MONTHS`, `YEARS`, `UserStatus` |"
            ),
            "| `peeldb/search_indexes.py`, `dashboard/` | `mpcomp` | utilities — `mpcomp` is a keeper |",
            "| `jobsp/urls.py`, `jobsp/views.py` | pjob, candidate, psite, search, recruiter | the URLconf itself |",
            "",
            "`MONTHS` is byte-identical in `recruiter.forms` and `candidate.forms`, but",
            "`YEARS` is **not**: candidate runs 0–40 (a job seeker's experience),",
            "recruiter caps at 0–20 (a job's requirement). They cannot be merged into one",
            "constant when relocating.",
            "",
            "`psite` is not deletable as a unit either: `psite/sitemaps.py` is permanent,",
            "and `psite.forms` is imported by `candidate/`, `pjob/` and `jobsp/views.py`.",
            "",
            "## Status",
            "",
            f"{len(rows)} routes total — {len(keep)} permanent, {len(retire)} in scope",
            "for retirement. The counts below are a starting point, not a burndown:",
            (
                f"most of the `{UNVERIFIED}` rows are expected to resolve to "
                f"`{MIGRATED}` or `{DROP}` once checked."
            ),
            "",
            "| State | Routes |",
            "| --- | --- |",
        ]
        for status, count in sorted(counts.items(), key=lambda kv: -kv[1]):
            out.append(f"| `{status}` | {count} |")

        out += [
            "",
            "## Routes to retire",
            "",
        ]

        by_module = OrderedDict()
        for row in retire:
            by_module.setdefault(row["module"], []).append(row)

        ordered = [m for m in APP_ORDER if m in by_module]
        ordered += [m for m in sorted(by_module) if m not in APP_ORDER]

        for module in ordered:
            title = APP_TITLES.get(module, module)
            out += [
                f"### `{module}/` — {title}",
                "",
                f"{len(by_module[module])} routes.",
                "",
                "| Django URL | View | Templates | SvelteKit | "
                + ("Probe | " if probed else "")
                + "Status | Notes |",
                "| --- | --- | --- | --- | --- | --- |" + (" --- |" if probed else ""),
            ]
            for row in by_module[module]:
                templates = "<br>".join(row["templates"]) or "—"
                cells = [
                    f"`/{row['pattern'].lstrip('^')}`",
                    f"`{row['view']}`",
                    templates,
                    f"`{row['sveltekit']}`" if row["sveltekit"] else "—",
                ]
                if probed:
                    cells.append(row["probe"] or "—")
                cells += [f"`{row['status']}`", row["note"] or ""]
                out.append("| " + " | ".join(cells) + " |")
            out.append("")

        out += [
            "## Keep (permanent)",
            "",
            "These are not legacy. They stay in Django after every retirement pass.",
            "",
            "| Module | Routes | Why |",
            "| --- | --- | --- |",
        ]
        keep_by_reason = OrderedDict()
        for row in keep:
            keep_by_reason.setdefault((row["module"], row["note"]), []).append(row)
        for (module, why), grouped in sorted(
            keep_by_reason.items(), key=lambda kv: -len(kv[1])
        ):
            out.append(f"| `{module}` | {len(grouped)} | {why} |")

        out += [
            "",
            "Plus, with no URL of their own:",
            "",
            "- `templates/email/`, `templates/jobseeker/email/`, `templates/recruiter/email/`",
            "  — rendered by `dashboard/tasks.py` and by `/api/v1/` on register, verify,",
            "  password reset and team invite. `dashboard.tasks.send_email` is the API's",
            "  only import from a legacy app.",
            "- `psite/sitemaps.py` — 27k URLs across 6 sections.",
            "- `templates/404.html`, `templates/500.html` — `handler404` / `handler500`.",
            "",
            "## Caveats",
            "",
            "- **Templates are best-effort.** Only `.html` literals in the view's own",
            "  body are detected; views that render through a helper under-report.",
            "  Check `{% extends %}` and `{% include %}` before deleting any file.",
            "- **Probe checks that something answers, not that it is equivalent.**",
            "  `/profile/` returns 200 on site/ while rendering mock data.",
            "- Probed paths use real slugs pulled from the database where possible",
            "  (`load_db_samples`), falling back to the literals in `SAMPLES`. A 404",
            "  on a fallback can mean the sample does not exist rather than the route",
            "  being absent — check before acting on one.",
            "- Routes whose pattern cannot be made concrete are not probed at all.",
            "",
        ]
        return "\n".join(out) + "\n"
