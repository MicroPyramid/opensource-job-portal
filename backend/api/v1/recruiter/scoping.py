"""
Which jobs a recruiter may see and manage.

A company admin acts for the whole company — they invite the team, so they own
what the team posts. Everyone else sees only their own jobs.

This restores a rule the migration dropped. The legacy dashboard scoped on
``user__company`` whenever the caller was a company admin or held
``jobposts_edit`` (``recruiter/views.py:748`` at ``ad39524``); every DRF view
was written with a hardcoded ``user=request.user`` instead. The effect was that
team management worked end to end — invite, roles, activate/deactivate — and
then an admin could see nothing their invitees posted.

Import ``recruiter_jobs`` rather than filtering ``JobPost`` directly, so the
rule stays in one place.
"""

from peeldb.models import JobPost


def recruiter_jobs(user):
    """The ``JobPost`` queryset ``user`` is allowed to read and mutate.

    Company admins get every job posted by anyone in their company; everyone
    else gets their own. ``is_company_admin`` already requires a company, so
    the admin branch can never widen to ``company IS NULL``.
    """
    if user.is_company_admin:
        return JobPost.objects.filter(user__company_id=user.company_id)
    return JobPost.objects.filter(user=user)
