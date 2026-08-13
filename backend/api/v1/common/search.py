"""Shared text-matching helpers for lookup endpoints.

Job search lives in ``api/v1/jobs/filters.py`` — it ranks a stored full-text
vector and is a different problem. This module covers the name lookups behind
autocomplete widgets (skills, cities), where the input is a fragment rather
than a sentence.
"""

from django.contrib.postgres.search import TrigramWordSimilarity

# Same cutoff as the job-search fallback, and measured the same way — see the
# table in api/v1/jobs/filters.py. It is what makes "banglore" find Bangalore
# (0.583) without "java" also offering Jalandhar (0.400).
TRIGRAM_FALLBACK_THRESHOLD = 0.4


def fuzzy_name_filter(queryset, term, field="name"):
    """Filter ``queryset`` by ``term``, falling back to fuzzy matching.

    Substring matching stays the primary path, because that is what a fragment
    typed into an autocomplete means: "pyt" should offer "Python", and trigram
    similarity scores that pairing poorly — three characters share too little
    with the whole word.

    Only when the substring match finds nothing does this fall back to
    word-level trigram similarity, which is what rescues a genuine typo like
    "pyhton". Ordering differs per path deliberately: alphabetical for
    substring hits (unchanged, and predictable in a dropdown), best-match-first
    for fuzzy hits, where alphabetical order would bury the answer.

    Neither path is indexed. Skill and City hold 866 and 113 rows, so a
    sequential scan is measured in microseconds and a GIN index would be
    maintenance cost for no gain.
    """
    term = (term or "").strip()
    if not term:
        return queryset.order_by(field)

    matches = queryset.filter(**{f"{field}__icontains": term})
    if matches.exists():
        return matches.order_by(field)

    return (
        queryset.annotate(name_similarity=TrigramWordSimilarity(term, field))
        .filter(name_similarity__gt=TRIGRAM_FALLBACK_THRESHOLD)
        .order_by("-name_similarity")
    )
