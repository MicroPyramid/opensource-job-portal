"""
Assert every URL name referenced in a template or in Python still resolves.

Deleting a view breaks `{% url %}` in whatever else still reverses it, and
Django only tells you at render time — which is how
`templates/job_detail_tailwind.html` ended up reversing `agency:` names that no
longer exist. This turns that into a check you can run.

    uv run manage.py check_url_names

Exits non-zero when a referenced name has no route, so it can gate the deletion
pass. `--ignore` skips paths that are already slated for removal, which is how
you confirm a deletion is safe before making it:

    uv run manage.py check_url_names --ignore templates/jobs --ignore pjob
"""

import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.urls import get_resolver

# {% url 'name' ... %} / {% url "name" ... %} — quoted names only. A name held
# in a variable cannot be checked statically; those are counted and reported.
TEMPLATE_URL = re.compile(r"{%\s*url\s+(?P<quote>[\"'])(?P<name>[^\"']+)(?P=quote)")
TEMPLATE_URL_DYNAMIC = re.compile(r"{%\s*url\s+(?![\"'])")

# reverse("name") / reverse_lazy('name') / redirect("name")
PYTHON_REVERSE = re.compile(
    r"\b(?:reverse|reverse_lazy|redirect)\(\s*(?P<quote>[\"'])(?P<name>[^\"']+)(?P=quote)"
)

SKIP_DIRS = {".venv", "node_modules", "__pycache__", ".git", "migrations"}


def valid_names(resolver, prefix=""):
    """Every reversible name in the URLconf, fully namespaced."""
    for entry in resolver.url_patterns:
        if hasattr(entry, "url_patterns"):
            namespace = entry.namespace or entry.app_name
            child = f"{prefix}{namespace}:" if namespace else prefix
            yield from valid_names(entry, child)
        elif entry.name:
            yield f"{prefix}{entry.name}"


def walk_files(root, suffixes):
    for path in root.rglob("*"):
        if path.suffix not in suffixes or not path.is_file():
            continue
        if SKIP_DIRS & set(path.parts):
            continue
        yield path


class Command(BaseCommand):
    help = "Check that every referenced URL name still resolves"

    def add_arguments(self, parser):
        parser.add_argument(
            "--ignore",
            action="append",
            default=[],
            help="Path prefix to skip, relative to --root; repeatable. "
            "Use to preview a deletion before making it.",
        )
        parser.add_argument(
            "--root",
            default=".",
            help="Directory to scan, relative to backend/ (default: the whole tree)",
        )

    def handle(self, *args, **options):
        known = set(valid_names(get_resolver()))
        root = Path(options["root"]).resolve()
        ignores = options["ignore"]

        missing = []
        dynamic = 0
        checked = 0

        sources = [
            (walk_files(root, {".html"}), TEMPLATE_URL),
            (walk_files(root, {".py"}), PYTHON_REVERSE),
        ]

        for paths, pattern in sources:
            for path in paths:
                # This module's own regex literals look like call sites.
                if path == Path(__file__).resolve():
                    continue
                rel = str(path.relative_to(root))
                # Prefix, not substring: "search/" must not also silence
                # templates/dashboard/search/, or the gate hides real breakage.
                if any(rel.startswith(ignored) for ignored in ignores):
                    continue
                try:
                    text = path.read_text()
                except (OSError, UnicodeDecodeError):
                    continue

                if pattern is TEMPLATE_URL:
                    dynamic += len(TEMPLATE_URL_DYNAMIC.findall(text))

                for match in pattern.finditer(text):
                    name = match.group("name")
                    # redirect() takes paths as well as names; only names here.
                    if name.startswith(("/", "http://", "https://", ".")):
                        continue
                    checked += 1
                    if name not in known:
                        line = text.count("\n", 0, match.start()) + 1
                        missing.append((rel, line, name))

        for rel, line, name in sorted(missing):
            self.stdout.write(self.style.ERROR(f"{rel}:{line}  {name}"))

        summary = (
            f"{checked} references checked against {len(known)} routes, "
            f"{len(missing)} unresolvable, {dynamic} dynamic (uncheckable)"
        )
        if ignores:
            summary += f", ignoring {ignores}"

        if missing:
            self.stdout.write(self.style.ERROR(summary))
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS(summary))
