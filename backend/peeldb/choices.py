"""
Shared form choices.

These lived in ``recruiter/forms.py`` and ``candidate/forms.py``, which meant
``dashboard/`` and ``peeldb/templatetags/`` had to import from two legacy apps
just to render a duration dropdown — the last thing keeping those apps pinned
in the import graph. They are plain data with no app of their own, so they live
in ``peeldb`` alongside the models they describe.

Note ``peeldb.models.MONTHS`` is a *different* constant: calendar month names
(January…December). These are durations.
"""


def _numeric_choices(stop):
    """(("0", "0"), ("1", "1"), …) up to and including `stop`."""
    return tuple((str(n), str(n)) for n in range(stop + 1))


#: Months of experience, 0–12. Was byte-identical in both legacy apps.
EXPERIENCE_MONTHS = _numeric_choices(12)

#: Years of experience a *job* asks for, 0–20. Was ``recruiter.forms.YEARS``.
JOB_EXPERIENCE_YEARS = _numeric_choices(20)

#: Years of experience a *job seeker* has, 0–40, thinning out past 25. Was
#: ``candidate.forms.YEARS`` — deliberately a wider range than the job side,
#: which is why the two cannot share one constant.
PROFILE_EXPERIENCE_YEARS = _numeric_choices(25) + tuple(
    (str(n), str(n)) for n in (30, 35, 40)
)
