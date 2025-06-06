"""
Company Management Views
Handles company and recruiter management operations
"""
import json
import math
from datetime import datetime

from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.template import loader
from django.template.loader import render_to_string
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Permission, ContentType
from django.db.models import Q

from dashboard.tasks import send_email
from django.utils.crypto import get_random_string
from mpcomp.views import (
    recruiter_login_required,
    agency_admin_login_required,
    get_prev_after_pages_count,
)

from peeldb.models import (
    JobPost,
    User,
    Company,
    Menu,
    Ticket,
)

from ..forms import (
    RecruiterForm,
    MenuForm,
    YEARS,
)


# Company Management Views will be moved here
# TODO: Move the following functions from the main views.py:
# - company_recruiter_list()
# - company_recruiter_create()
# - edit_company_recruiter()
# - activate_company_recruiter()
# - delete_company_recruiter()
# - company_recruiter_profile()
# - add_menu()
# - menu_status()
# - delete_menu()
# - edit_menu()
# - menu_order()


@recruiter_login_required
def company_recruiter_list(request):
    recruiters = User.objects.filter(company=request.user.company).exclude(
        id=request.user.id
    )
    if "search" in request.GET.keys():
        if str(request.GET["search"].lower()) == "active":
            recruiters = recruiters.filter(is_active=True)
        else:
            recruiters = recruiters.filter(is_active=False)
        if not (
            request.GET["search"].lower() == "active"
            or str(request.GET["search"].lower()).replace(" ", "") == "inactive"
        ):
            recruiters = recruiters.filter(
                Q(first_name__icontains=request.GET["search"])
                | Q(email__icontains=request.GET["search"])
            )
    if "page" in request.GET and int(request.GET.get("page")) > 0:
        page = int(request.GET.get("page"))
    else:
        page = 1
    items_per_page = 10
    no_pages = int(math.ceil(float(recruiters.count()) / items_per_page))
    recruiters = recruiters[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    search_value = request.GET["search"] if "search" in request.GET.keys() else ""
    return render(
        request,
        "recruiter/company/recruiter_list.html",
        {
            "recruiters": recruiters,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "search_value": search_value,
        },
    )




@agency_admin_login_required
def company_recruiter_create(request):
    contenttype = ContentType.objects.get(model="user")
    permissions = Permission.objects.filter(
        content_type_id=contenttype, codename__icontains="jobposts"
    ).order_by("id")

    if request.method == "POST":
        validate_recruiter = RecruiterForm(request.POST, request.FILES)
        if validate_recruiter.is_valid():
            user = User.objects.create(
                first_name=request.POST["first_name"],
                email=request.POST["email"],
                username=request.POST["email"],
                job_role=request.POST["job_role"],
                mobile=request.POST["mobile"],
            )
            if request.FILES.get("profile_pic"):
                user.profile_pic = request.FILES.get("profile_pic")
            user.set_password(request.POST["password"])
            user.company = request.user.company
            user.user_type = "AR"
            user.mobile_verified = True
            while True:
                random_code = get_random_string(length=10)
                u = User.objects.filter(activation_code__iexact=random_code)
                if not u:
                    break
            while True:
                unsub_code = get_random_string(length=10)
                u = User.objects.filter(unsubscribe_code__iexact=random_code)
                if not u:
                    break
            user.activation_code = random_code
            user.unsubscribe_code = unsub_code
            user.save()
            if (
                "is_admin" in request.POST.keys()
                and request.POST.get("is_admin") == "True"
            ):
                user.user_type = "AA"
                user.agency_admin = True
                user.save()
                for permission in permissions:
                    user.user_permissions.add(permission)
            else:
                for perm in request.POST.getlist("permissions"):
                    permission = Permission.objects.get(id=perm)
                    user.user_permissions.add(permission)

            temp = loader.get_template("recruiter/email/recruiter_account.html")
            try:
                url = (
                    "https://"
                    + request.META["HTTP_HOST"]
                    + "/recruiter/activation/"
                    + str(user.activation_code)
                    + "/"
                )
            except:
                url = (
                    "https://peeljobs.com"
                    + "/recruiter/activation/"
                    + str(user.activation_code)
                    + "/"
                )
            c = {
                "user": user,
                "activate_url": url,
                "user_password": request.POST["password"],
            }
            rendered = temp.render(c)
            mto = [user.email]
            subject = "PeelJobs Recruiter Account Activation"
            # user_active = True if request.user.is_active else False
            send_email.delay(mto, subject, rendered)
            data = {"error": False, "response": "Recruiter Created Successfully"}
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "response": validate_recruiter.errors}
            return HttpResponse(json.dumps(data))
    return render(
        request, "recruiter/company/create_recruiter.html", {"permissions": permissions}
    )





@agency_admin_login_required
def edit_company_recruiter(request, recruiter_id):
    recruiters = User.objects.filter(
        company=request.user.company, id=recruiter_id
    ).exclude(id=request.user.id)
    if recruiters:
        recruiter = recruiters[0]
        contenttype = ContentType.objects.get(model="user")
        permissions = Permission.objects.filter(
            content_type_id=contenttype, codename__icontains="jobposts"
        ).order_by("id")

        if request.method == "POST":
            validate_recruiter = RecruiterForm(
                request.POST, request.FILES, instance=recruiter
            )
            if validate_recruiter.is_valid():
                recruiter = validate_recruiter.save(commit=False)
                if recruiter.password != request.POST[
                    "password"
                ] and not check_password(request.POST["password"], recruiter.password):
                    recruiter.set_password(request.POST["password"])
                if request.FILES.get("profile_pic"):
                    recruiter.profile_pic = request.FILES.get("profile_pic")
                recruiter.save()
                recruiter.user_permissions.clear()
                if (
                    "is_admin" in request.POST.keys()
                    and request.POST.get("is_admin") == "True"
                ):
                    recruiter.user_type = "AA"
                    recruiter.agency_admin = True
                    recruiter.save()
                    for permission in permissions:
                        recruiter.user_permissions.add(permission)
                else:
                    recruiter.user_type = "AR"
                    recruiter.agency_admin = False
                    recruiter.save()

                    for perm in request.POST.getlist("permissions"):
                        permission = Permission.objects.get(id=perm)
                        recruiter.user_permissions.add(permission)

                data = {"error": False, "response": "Recruiter Updated Successfully"}
                return HttpResponse(json.dumps(data))
            else:
                data = {"error": True, "response": validate_recruiter.errors}
                return HttpResponse(json.dumps(data))
        return render(
            request,
            "recruiter/company/create_recruiter.html",
            {"recruiter": recruiter, "permissions": permissions},
        )
    message = "Sorry, No Recruiter Available with this id"
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/recruiter_404.html",
        {"message_type": "404", "message": message, "reason": reason},
        status=404,
    )




@agency_admin_login_required
def activate_company_recruiter(request, recruiter_id):
    recruiters = User.objects.filter(company=request.user.company, id=recruiter_id)
    if recruiters:
        recruiter = recruiters[0]
        if recruiter.is_active:
            recruiter.is_active = False
        else:
            recruiter.is_active = True
        recruiter.save()
        return HttpResponseRedirect(reverse("recruiter:company_recruiter_list"))
    message = "Sorry, No Recruiter Available with this id"
    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/recruiter_404.html",
        {"message_type": "404", "message": message, "reason": reason},
        status=404,
    )




@agency_admin_login_required
def delete_company_recruiter(request, recruiter_id):
    recruiters = User.objects.filter(company=request.user.company, id=recruiter_id)
    if recruiters:
        recruiter = recruiters[0]
        recruiter.delete()
        data = {"error": False, "response": "Recruiter Deleted Successfully"}
    else:
        data = {"error": True, "response": "Some Problem Occurs"}
    return HttpResponse(json.dumps(data))




@recruiter_login_required
def company_recruiter_profile(request, recruiter_id):
    recruiters = User.objects.filter(company=request.user.company, id=recruiter_id)
    if recruiters:
        recruiter = recruiters[0]
        if recruiter.is_admin:
            job_posts = JobPost.objects.filter(company=request.user.company)
        else:
            job_posts = JobPost.objects.filter(
                Q(user=recruiter) | Q(agency_recruiters__in=[recruiter])
            )
        if "job_status" in request.GET.keys():
            job_posts = job_posts.filter(status=request.GET["job_status"])

        tickets = Ticket.objects.filter(user=recruiter)
        if "search_value" in request.GET.keys():
            if request.GET["search_value"] == "all":
                pass
            else:
                job_posts = job_posts.filter(job_type=request.GET["search_value"])
        if "page" in request.GET and int(request.GET.get("page")) > 0:
            page = int(request.GET.get("page"))
        else:
            page = 1
        items_per_page = 10
        no_pages = int(math.ceil(float(job_posts.count()) / items_per_page))
        job_posts = job_posts[(page - 1) * items_per_page : page * items_per_page]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        search_value = (
            request.GET.get("search_value") if request.GET.get("search_value") else ""
        )
        job_status = (
            request.GET.get("job_status") if request.GET.get("job_status") else "active"
        )

        return render(
            request,
            "recruiter/company/recruiter_profile.html",
            {
                "recruiter": recruiter,
                "job_posts": job_posts,
                "tickets": tickets,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
                "search_value": search_value,
                "job_status": job_status,
            },
        )

    reason = "The URL may be misspelled or the page you're looking for is no longer available."
    return render(
        request,
        "recruiter/recruiter_404.html",
        {
            "message_type": "404",
            "message": "Sorry, No Recruiter Available with this id",
            "reason": reason,
        },
        status=404,
    )





@agency_admin_login_required
def add_menu(request):
    if request.method == "POST":
        validate_menu = MenuForm(request.POST)
        if validate_menu.is_valid():
            new_menu = validate_menu.save(commit=False)
            if request.POST.get("status") == "True":
                new_menu.status = True
            menu_count = Menu.objects.count()
            new_menu.lvl = menu_count + 1
            new_menu.company = request.user.company
            new_menu.save()
            data = {"error": False, "response": "Menu created successfully"}
        else:
            data = {"error": True, "response": validate_menu.errors}
        return HttpResponse(json.dumps(data))




@agency_admin_login_required
def menu_status(request, menu_id):
    menu = Menu.objects.filter(id=menu_id, company=request.user.company)
    if menu:
        menu = menu[0]
        if menu.status:
            menu.status = False
        else:
            menu.status = True
        menu.save()
    return HttpResponseRedirect(reverse("recruiter:view_company"))




@agency_admin_login_required
def delete_menu(request, menu_id):
    menu = Menu.objects.filter(id=menu_id, company=request.user.company)
    if menu:
        menu = menu[0]
        menu.delete()
        data = {"error": False, "response": "Menu Deleted Successfully"}
    else:
        data = {"error": True, "response": "Some Problem Occurs"}
    return HttpResponse(json.dumps(data))



@agency_admin_login_required
def edit_menu(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id, company=request.user.company)
    if request.method == "POST":
        validate_menu = MenuForm(request.POST, instance=menu)
        if validate_menu.is_valid():
            new_menu = validate_menu.save(commit=False)
            if request.POST.get("status") == "True":
                new_menu.status = True
            new_menu.save()
            data = {"error": False, "response": "Menu created successfully"}
        else:
            data = {"error": True, "response": validate_menu.errors}
        return HttpResponse(json.dumps(data))



@agency_admin_login_required
def menu_order(request):
    menu = get_object_or_404(
        Menu, id=request.GET.get("menu_id"), company=request.user.company
    )
    prev = request.GET.get("prev")
    current = request.GET.get("current")
    if int(prev) < int(current):
        selected_menus = Menu.objects.filter(
            lvl__gt=prev, lvl__lte=current, company=request.user.company
        )
        for each in selected_menus:
            each.lvl = each.lvl - 1
            each.save()
    else:
        selected_menus = Menu.objects.filter(
            lvl__lt=prev, lvl__gte=current, company=request.user.company
        )
        for each in selected_menus:
            each.lvl = each.lvl + 1
            each.save()
    menu.lvl = current
    menu.save()
    return HttpResponseRedirect(reverse("recruiter:view_company"))
