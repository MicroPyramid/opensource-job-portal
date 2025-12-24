import json
import math
import re
from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.urls import reverse
from django.template import loader, Template, Context
from django.utils.crypto import get_random_string

from mpcomp.views import get_prev_after_pages_count
from candidate.forms import JobAlertForm, YEARS
from peeldb.models import (
    MetaData,
    User,
    City,
    Industry,
    Skill,
    JobPost,
    JobAlert,
    Subscriber,
)
from dashboard.tasks import send_email


def job_alert(request):
    if request.method == "GET":
        meta_title = meta_description = h1_tag = ""
        meta = MetaData.objects.filter(name="alerts_list")
        if meta:
            meta_title = Template(meta[0].meta_title).render(Context({}))
            meta_description = Template(meta[0].meta_description).render(Context({}))
            h1_tag = Template(meta[0].h1_tag).render(Context({}))
        template = "alert/job_alert.html"
        return render(
            request,
            template,
            {
                "skills": Skill.objects.filter(status="Active"),
                "industires": Industry.objects.filter(status="Active"),
                "cities": City.objects.filter(status="Enabled"),
                "years": YEARS,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "h1_tag": h1_tag,
            },
        )
    validate_jobalert = JobAlertForm(request.POST)
    if validate_jobalert.is_valid():
        job_alert = JobAlert.objects.create(name=request.POST.get("name"))
        if request.POST.get("min_year"):
            job_alert.min_year = request.POST.get("min_year")
            job_alert.max_year = request.POST.get("max_year", "")
        if request.POST.get("min_salary"):
            job_alert.min_salary = request.POST.get("min_salary", "")
            job_alert.max_salary = request.POST.get("max_salary", "")
        job_alert.role = request.POST.get("role", "")
        if request.POST.getlist("location"):
            job_alert.location.add(*request.POST.getlist("location"))
        if request.POST.getlist("industry"):
            job_alert.industry.add(*request.POST.getlist("industry"))
        job_alert.email = (
            request.user.email
            if request.user.is_authenticated
            else request.POST.get("email", "")
        )
        while True:
            unsubscribe_code = get_random_string(length=15)
            if not JobAlert.objects.filter(unsubscribe_code__iexact=unsubscribe_code):
                break
        job_alert.unsubscribe_code = unsubscribe_code
        while True:
            subscribe_code = get_random_string(length=15)
            if not JobAlert.objects.filter(subscribe_code__iexact=subscribe_code):
                break
        job_alert.subscribe_code = subscribe_code
        job_alert.save()
        job_alert.skill.add(*request.POST.getlist("skill"))
        temp = loader.get_template("email/job_alert.html")
        subject = "Job Alert Confirmation"
        url = (
            request.scheme
            + "://"
            + request.META["HTTP_HOST"]
            + "/alert/verification/"
            + str(job_alert.subscribe_code)
            + "/"
        )
        c = {
            "alert": job_alert,
            "user": request.user,
            "new_alert": True,
            "verify_alert": True,
            "redirect_url": url,
        }
        rendered = temp.render(c)
        user_active = (
            True if request.user.is_authenticated and request.user.is_active else False
        )
        mto = request.POST.get("email")
        send_email.delay(mto, subject, rendered)
        return HttpResponse(
            json.dumps(
                {
                    "error": False,
                    "message": "job alert created successfully",
                    "alert_id": job_alert.id,
                }
            )
        )
    else:
        return HttpResponse(
            json.dumps({"error": True, "message": validate_jobalert.errors})
        )


def alert_subscribe_verification(request, obj_type, obj_id):
    if obj_type == "alert":
        value = JobAlert.objects.filter(subscribe_code__iexact=obj_id).first()
    else:
        value = Subscriber.objects.filter(subscribe_code__iexact=obj_id).first()
        if value:
            subscribers = Subscriber.objects.filter(email=value.email)
            for sub in subscribers:
                sub.is_verified = True
                sub.save()
    if value:
        verified = value.is_verified
        value.is_verified = True
        value.save()
        user = User.objects.filter(email=value.email).first()
        if user:
            user.is_active = True
            user.save()
        if verified:
            return HttpResponseRedirect("/jobs/?verification=verified")
        return HttpResponseRedirect("/jobs/?verification=success")
    return HttpResponseRedirect(
        "/jobs/?verification=error&type="
        + ("Alerts" if obj_type == "alert" else "Subscribers")
    )


def job_alert_results(request, job_alert_id):
    if request.user.is_authenticated and request.user.user_type == "JS":
        job_alerts = JobAlert.objects.filter(id=job_alert_id, email=request.user.email)
    else:
        job_alerts = JobAlert.objects.filter(id=job_alert_id)

    if request.user.is_authenticated:
        if request.user.is_staff or request.user.user_type == "RR":
            message = "Sorry, No Job Alerts Availableble"
            template = "404.html"
            return render(request, template, {"message": message}, status=404)

    if job_alerts:
        job_alert = job_alerts[0]
        jobs_list = JobPost.objects.filter(
            (Q(skills__in=job_alert.skill.all(), status="Live"))
            & (
                Q(industry__in=job_alert.industry.all())
                | Q(min_year=job_alert.min_year)
                | Q(max_year=job_alert.max_year)
                | Q(max_salary=job_alert.max_salary)
                | Q(min_salary=job_alert.min_salary)
                | Q(job_role=job_alert.role)
                | Q(location__in=job_alert.location.all())
            )
        ).distinct()
        if not jobs_list:
            jobs_list = JobPost.objects.filter(
                status="Live", skills__in=job_alert.skill.all()
            )
        items_per_page = 10
        no_pages = int(math.ceil(float(jobs_list.count()) / items_per_page))

        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                page = 1
                return HttpResponseRedirect("/")
            else:
                page = int(request.GET.get("page"))
        else:
            page = 1

        jobs_list = jobs_list[(page - 1) * items_per_page : page * items_per_page]

        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        data = {
            "jobs_list": jobs_list,
            "job_alert": job_alert,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
        }
        template = "alert/job_alert_results.html"
        return render(request, template, data)
    else:
        template = "alert/list.html"
        return render(request, "alert/list.html", {"job_alerts": []})


def modify_job_alert(request, job_alert_id):
    job_alerts = JobAlert.objects.filter(id=job_alert_id)
    if job_alerts:
        job_alert = job_alerts[0]
        if request.method == "GET":
            data = {
                "skills": Skill.objects.filter(status="Active"),
                "industires": Industry.objects.filter(status="Active"),
                "cities": City.objects.filter(status="Enabled"),
                "years": YEARS,
                "job_alert": job_alert,
            }
            template = "alert/modify_job_alert.html"
            return render(request, template, data)
        validate_jobalert = JobAlertForm(request.POST, instance=job_alert)
        if validate_jobalert.is_valid():
            job_alert.name = request.POST.get("name")
            if request.POST.get("min_year"):
                job_alert.min_year = request.POST.get("min_year", "")
                job_alert.max_year = request.POST.get("max_year", "")
            if request.POST.get("min_salary"):
                job_alert.min_salary = request.POST.get("min_salary", "")
                job_alert.max_salary = request.POST.get("max_salary", "")
            job_alert.role = request.POST.get("role")
            job_alert.save()

            job_alert.skill.clear()
            job_alert.location.clear()
            job_alert.industry.clear()

            job_alert.skill.add(*request.POST.getlist("skill"))
            if request.POST.getlist("location"):
                job_alert.location.add(*request.POST.getlist("location"))
            if request.POST.getlist("industry"):
                job_alert.industry.add(*request.POST.getlist("industry"))

            data = {
                "error": False,
                "message": "job alert updated successfully",
                "alert_id": job_alert.id,
            }
        else:
            data = {"error": True, "message": validate_jobalert.errors}
        return HttpResponse(json.dumps(data))
    else:
        message = "Sorry, No Alerts Fount"
        template = "404.html"
        return render(request, template, {"message": message}, status=404)


def alerts_list(request, **kwargs):
    meta_title = meta_description = h1_tag = ""
    meta = MetaData.objects.filter(name="alerts_list")
    if meta:
        meta_title = Template(meta[0].meta_title).render(Context({}))
        meta_description = Template(meta[0].meta_description).render(Context({}))
        h1_tag = Template(meta[0].h1_tag).render(Context({}))
    if request.user.is_authenticated:
        job_alerts = JobAlert.objects.filter(email=request.user.email)

        items_per_page = 5
        no_pages = int(math.ceil(float(job_alerts.count()) / items_per_page))

        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                page = 1
                return HttpResponseRedirect("/")
            else:
                page = int(request.GET.get("page"))
        else:
            page = 1
        if kwargs:
            page = int(kwargs["page_num"])

        job_alerts = job_alerts[(page - 1) * items_per_page : page * items_per_page]

        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        template = "alert/list.html"
        return render(
            request,
            template,
            {
                "job_alerts": job_alerts,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
                "current_url": reverse("my:alerts_list"),
                "meta_title": meta_title,
                "meta_description": meta_description,
                "h1_tag": h1_tag,
            },
        )
    else:
        template = "alert/job_alert.html"
        return render(
            request,
            template,
            {
                "skills": Skill.objects.filter(status="Active"),
                "industires": Industry.objects.filter(status="Active"),
                "cities": City.objects.filter(status="Enabled"),
                "years": YEARS,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "h1_tag": h1_tag,
            },
        )


def delete_job_alert(request, job_alert_id):
    job_alerts = JobAlert.objects.filter(id=job_alert_id)
    if job_alerts:
        job_alerts[0].delete()
        data = {"error": False, "response": "job alerts deleted successfully"}
    else:
        data = {"error": True, "response": "job alert not exist"}
    return HttpResponse(json.dumps(data))
