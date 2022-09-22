import json
import requests
import math

from django.shortcuts import render
from django.contrib.auth import logout
from django.http.response import HttpResponseRedirect, HttpResponse
from django.conf import settings
from itertools import chain
from django.template import loader
# from oauth2client.contrib import xsrfutil
from django.urls import reverse

from peeldb.models import JobPost, ENQUERY_TYPES, Skill, City, Qualification, State
from .forms import SimpleContactForm
from mpcomp.views import get_prev_after_pages_count
from django.db.models import Count, F
# from pjob.calendar_events import FLOW
# from oauth2client.contrib.django_util.storage import DjangoORMStorage
# from peeldb.models import CredentialsModel
from dashboard.tasks import send_email


def pages(request, page_name):
    pages_slugs = [
        "about-us",
        "terms-conditions",
        "privacy-policy",
        "recruiter-faq",
        "faq",
    ]
    if page_name in pages_slugs:
        return render(request, "pages/" + page_name + ".html")
        

    message = "Sorry, the page you requested can not be found"
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    if request.user.is_authenticated and request.user.is_recruiter:
        return render(
            request,
            "recruiter/recruiter_404.html",
            {"message": message, "reason": reason},
            status=404,
        )
    return render(
        request, "404.html", {"message": message, "reason": reason}, status=404
    )


# def users_login(request):
    # return render(request, "login.html")


def get_out(request):
    url = request.GET.get("next")
    logout(request)
    request.session.flush()
    if url:
        return HttpResponseRedirect(url)
    return HttpResponseRedirect("/")


def custom_404(request, exception):
    message = "Sorry, the page you requested can not be found"
    reason = "The URL may be misspelled or the page you're looking for is no longer available."

    if request.user.is_authenticated:
        if request.user.is_recruiter:
            return render(
                request,
                "recruiter/recruiter_404.html",
                {"message": message, "reason": reason},
                status=404,
            )
        if request.user.is_staff:
            return render(
                request,
                "dashboard/404.html",
                {"message": message, "reason": reason},
                status=404,
            )
    return render(
        request, "404.html", {"message": message, "reason": reason}, status=404
    )


def custom_500(request):
    message = "500, We are sorry! The server Encountered an Internal error"
    reason = "We are unable to complete your request. Please try again later"

    if request.user.is_authenticated:
        if request.user.is_recruiter:
            return render(
                request,
                "recruiter/recruiter_404.html",
                {"message": message, "reason": reason},
                status=404,
            )
        if request.user.is_staff:
            return render(
                request,
                "dashboard/404.html",
                {"message": message, "reason": reason},
                status=404,
            )
    return render(
        request, "404.html", {"message": message, "reason": reason,}, status=404,
    )


def sitemap_xml(request):
    with open("sitemap/sitemap.xml") as file:
        xml_cont = file.read()
    return HttpResponse(xml_cont, content_type="text/xml")


def contact(request):
    if request.method == "POST":
        validate_simplecontactform = SimpleContactForm(request.POST)
        if validate_simplecontactform.is_valid():
            payload = {
                "secret": "6LdZcgkTAAAAAGkY3zbzO4lWhqCStbWUef_6MWW-",
                "response": request.POST.get("g-recaptcha-response"),
                "remoteip": request.META.get("REMOTE_ADDR"),
            }
            r = requests.get(
                "https://www.google.com/recaptcha/api/siteverify", params=payload
            )
            if json.loads(r.text)["success"]:
                validate_simplecontactform.save()

                c = {
                    "email": request.POST.get("email"),
                    "subject": request.POST.get("subject"),
                    "first_name": request.POST.get("first_name"),
                    "mobile": request.POST.get("phone"),
                    "enquiry_type": request.POST.get("enquery_type"),
                    "comment": request.POST.get("comment"),
                }
                subject = "New Request ContactUs | PeelJobs"
                mto = settings.SUPPORT_EMAILS
                t = loader.get_template("email/contactus_email.html")
                rendered = t.render(c)
                send_email.delay(mto, subject, rendered)

                subject = "Thanks for contacting us | PeelJobs"
                mto = settings.SUPPORT_EMAILS
                t = loader.get_template("email/user_contactus.html")
                rendered = t.render(c)
                send_email.delay(mto, subject, rendered)

                data = {
                    "error": False,
                    "response": "Thanks for contacting Us, we will reach you soon!",
                }
                return HttpResponse(json.dumps(data))
            data = {"error": True, "captcha_response": "Choose Correct Captcha"}
            return HttpResponse(json.dumps(data))
        data = {"error": True, "response": validate_simplecontactform.errors}
        return HttpResponse(json.dumps(data))
    return render(request, "pages/contact-us.html", {"enquery_types": ENQUERY_TYPES})


def sitemap(request, **kwargs):

    locations = (
        City.objects.annotate(num_posts=Count("locations"))
        .filter(status="Enabled", parent_city=None)
        .order_by("-num_posts")
    )
    skills = (
        Skill.objects.annotate(num_posts=Count("jobpost"))
        .filter(status="Active")
        .exclude(name="Fresher")
        .order_by("-num_posts")
    )
    full_jobposts = JobPost.objects.filter(status="Live", job_type="full-time")
    internships = JobPost.objects.filter(status="Live", job_type="internship")
    walk_ins = JobPost.objects.filter(status="Live", job_type="walk-in")
    government_jobs = JobPost.objects.filter(status="Live", job_type="government")
    states = State.objects.filter(status="Enabled").exclude(state__name__in=[F("name")])
    jobposts = list(chain(full_jobposts, internships, walk_ins, government_jobs))
    no_pages = int(math.ceil(float(len(jobposts)) / 100))
    page = 1
    if kwargs:
        page = int(kwargs["page_num"])
        page = page if (page - 7) < no_pages else 1
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    if page > 7:
        jobposts = jobposts[(page - 8) * 100 : (page - 7) * 100]
    else:
        jobposts = jobposts[(page - 1) * 100 : page * 100]
    template = "sitemap.html"
    return render(
        request,
        template,
        {
            "jobposts": jobposts,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "states": states,
            "locations": locations,
            "educations": Qualification.objects.filter(status="Active"),
            "skills": skills,
        },
    )


def auth_return(request):
    state = str(request.GET.get("state"))
    token_valid = xsrfutil.validate_token(
        settings.SECRET_KEY, bytearray(state, "utf-8"), request.user
    )
    if not token_valid or not state:
        return HttpResponseRedirect("/jobs/")
    credential = FLOW.step2_exchange(request.GET)
    storage = DjangoORMStorage(CredentialsModel, "id", request.user, "credential")
    storage.put(credential)
    return HttpResponseRedirect(reverse("pjob:job_add_event"))
