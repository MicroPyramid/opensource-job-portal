"""
What is left of the legacy recruiter views.

Everything else moved to the SvelteKit dashboard (`recruiter/`) and the REST
API (`/api/v1/recruiter/`). These two render Django templates that the new
stack has no equivalent for yet, and both are reachable from the surviving
job-seeker templates.
"""

from django.shortcuts import render


def post_job(request):
    return render(request, "recruiter_v2/post_job.html", {})


def how_it_works(request):
    return render(request, "recruiter/how_it_works.html", {})
