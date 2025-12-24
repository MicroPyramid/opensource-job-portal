import json
import math
import re

from django.urls import reverse
from django.db.models import Q
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import slugify

from mpcomp.views import (
    get_aws_file_path,
    get_prev_after_pages_count,
    permission_required,
)
from mpcomp.aws import AWS
from peeldb.models import (
    Company,
    JobPost,
    Menu,
    User,
)
from recruiter.forms import MenuForm

from ..forms import (
    CompanyForm,
)


# Functions to move here from main views.py:

@permission_required("activity_edit", "activity_view")
def companies(request, company_type):
    status = ""
    if company_type == "company":
        companies = Company.objects.filter(company_type__iexact=company_type).distinct()
        if request.GET.get("active") == "false":
            status = "fasle"
            companies = companies.filter(is_active=False)
        else:
            status = "true"
            companies = companies.filter(is_active=True)
    else:
        companies = Company.objects.filter(company_type__iexact=company_type).distinct()
        if "admin" in request.GET:
            if request.GET.get("admin") == "false":
                status = "admin_inactive"
                companies = companies.filter(
                    id__in=User.objects.filter(
                        is_admin=True, is_active=False
                    ).values_list("company", flat=True)
                )
            elif request.GET.get("admin") == "true":
                status = "admin_active"
                companies = companies.filter(
                    id__in=User.objects.filter(
                        is_admin=True, is_active=True
                    ).values_list("company", flat=True)
                )
        if "active" in request.GET:
            if request.GET.get("active") == "false":
                status = "inactive"
                companies = companies.filter(is_active=False)
            elif request.GET.get("active") == "true":
                status = "active"
                companies = companies.filter(is_active=True)

    if request.GET.get("search", ""):
        user_ids = User.objects.filter(
            email__icontains=request.GET.get("search")
        ).values_list("company", flat=True)
        companies = companies.filter(
            Q(id__in=user_ids)
            | Q(name__icontains=request.GET.get("search"))
            | Q(website=request.GET.get("search"))
        )

    items_per_page = 50
    no_pages = int(math.ceil(float(companies.count()) / items_per_page))
    companies = companies.order_by("-registered_date")
    page = request.POST.get("page") or request.GET.get("page")
    if page and bool(re.search(r"[0-9]", page)) and int(page) > 0:
        if int(page) > (no_pages + 2):
            return HttpResponseRedirect(reverse("dashboard:applicants"))
        page = int(page)
    else:
        page = 1
    companies = companies[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )
    return render(
        request,
        "dashboard/company/list.html",
        {
            "companies": companies,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "page": page,
            "last_page": no_pages,
            "company_type": company_type,
            "status": status,
            "search_value": (
                request.GET.get("search") if request.GET.get("search") else ""
            ),
            "active": request.GET.get("active") if request.GET.get("active") else "",
            "admin": request.GET.get("admin") if request.GET.get("admin") else "",
        },
    )



@permission_required("activity_edit", "activity_view")
def new_company(request):
    if request.method == "POST":
        validate_company = CompanyForm(request.POST, request.FILES)
        if validate_company.is_valid():
            company = validate_company.save()
            company.created_from = "dashboard"
            company.email = request.user.email
            company.slug = slugify(request.POST.get("name"))
            company.company_type = "Company"
            company.website = request.POST.get("website")
            company.is_active = request.POST.get("is_active") == "on"
            if request.POST.get("meta_title"):
                company.meta_title = request.POST.get("meta_title")
            if request.POST.get("meta_description"):
                company.meta_description = request.POST.get("meta_description")
            if request.FILES.get("profile_pic"):
                file_path = get_aws_file_path(
                    request.FILES.get("profile_pic"),
                    "company/logo/",
                    slugify(request.POST.get("name")),
                )
                company.profile_pic = file_path
            if request.FILES.get("campaign_icon"):
                file_path = get_aws_file_path(
                    request.FILES.get("campaign_icon"),
                    "company/logo/",
                    slugify(request.POST.get("name")),
                )
                company.campaign_icon = file_path
            company.save()
            data = {"error": False, "response": "Company created successfully"}
        else:
            data = {"error": True, "response": validate_company.errors}
        return HttpResponse(json.dumps(data))

    return render(request, "dashboard/company/new_company.html")


@permission_required("activity_edit", "activity_view")
def edit_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == "POST":
        validate_company = CompanyForm(request.POST, request.FILES, instance=company)
        if validate_company.is_valid():
            company_active = company.is_active
            company = validate_company.save(commit=False)
            company.website = request.POST.get("website")
            company.slug = request.POST.get("slug")
            company.is_active = request.POST.get("is_active") == "on"
            if request.POST.get("meta_title"):
                company.meta_title = request.POST.get("meta_title")
            if request.POST.get("meta_description"):
                company.meta_description = request.POST.get("meta_description")
            if request.FILES.get("profile_pic"):
                if company.profile_pic:
                    url = str(company.profile_pic).split("cdn.peeljobs.com")[-1:]
                    AWS().cloudfront_invalidate(paths=url)
                file_path = get_aws_file_path(
                    request.FILES.get("profile_pic"), "company/logo/", company.slug
                )
                company.profile_pic = file_path
            if request.FILES.get("campaign_icon"):
                if company.campaign_icon:
                    url = str(company.campaign_icon).split("cdn.peeljobs.com")[-1:]
                    AWS().cloudfront_invalidate(paths=url)
                file_path = get_aws_file_path(
                    request.FILES.get("campaign_icon"),
                    "company/logo/",
                    slugify(request.POST.get("name")),
                )
                company.campaign_icon = file_path

            company.save()
            data = {
                "error": False,
                "response": "Company edited successfully",
                "company_active": company_active,
                "edit": True,
            }
        else:
            data = {"error": True, "response": validate_company.errors}
        return HttpResponse(json.dumps(data))
    return render(request, "dashboard/company/new_company.html", {"company": company})



@permission_required("activity_edit", "activity_view")
def view_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    return render(request, "dashboard/company/view.html", {"company": company})



@permission_required("activity_edit")
def enable_company(request, company_id):
    page_value = request.POST.get("page")
    search_value = request.POST.get("search")
    admin = request.POST.get("admin")
    company = get_object_or_404(Company, id=company_id)
    url = reverse("dashboard:companies", kwargs={"company_type": company.company_type})
    if company.is_active:
        company.is_active = False
        is_active = "true"
        if str(admin) == "true":
            is_active = ""
        url = url + "?active=true&page=" + str(page_value) + "&search=" + search_value
        data = {
            "error": False,
            "response": "Company Deactivated Successfully",
            "is_active": is_active,
            "url": url,
        }
    else:
        url = url + "?active=false&page=" + str(page_value) + "&search=" + search_value
        company.is_active = True
        is_active = "false"
        if str(admin) == "true":
            is_active = ""

        data = {
            "error": False,
            "response": "Company Activated Successfully",
            "is_active": is_active,
            "url": url,
        }
    company.save()
    if company.is_active:
        data["active"] = "false"
    else:
        data["active"] = "true"
    return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def delete_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company_users = User.objects.filter(company=company)
    company_users.delete()

    page_value = request.POST.get("page")
    search_value = request.POST.get("search")
    admin = request.POST.get("admin")
    url = reverse("dashboard:companies", kwargs={"company_type": company.company_type})
    if company.is_active:
        company.is_active = False
        is_active = "true"
        if str(admin) == "true":
            is_active = ""
        url = url + "?active=true&page=" + str(page_value) + "&search=" + search_value
        data = {
            "error": False,
            "response": "Company Deactivated Successfully",
            "is_active": is_active,
            "url": url,
        }
    else:
        url = url + "?active=false&page=" + str(page_value) + "&search=" + search_value
        company.is_active = True
        is_active = "false"
        if str(admin) == "true":
            is_active = ""

    company.delete()
    data = {
        "error": False,
        "response": "Company Deleted Successfully",
        "url": url,
        "is_active": is_active,
    }
    return HttpResponse(json.dumps(data))


@permission_required("activity_edit")
def enable_paid_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company_admin = get_object_or_404(User, company=company, is_admin=True)
    if company_admin.is_paid:
        company_admin.is_paid = False
    else:
        company_admin.is_paid = True
    company_admin.save()
    return HttpResponseRedirect(
        reverse("dashboard:companies", kwargs={"company_type": company.company_type})
    )




@permission_required("activity_edit", "activity_view")
def company_recruiters(request, company_id, status):
    company = get_object_or_404(Company, id=company_id)
    recruiters = company.get_company_recruiters()
    if str(status) == "active":
        recruiters = recruiters.filter(is_active=True)
    else:
        recruiters = recruiters.filter(is_active=False)
    items_per_page = 100
    no_pages = int(math.ceil(float(recruiters.count()) / items_per_page))
    page = request.GET.get("page")
    if page and bool(re.search(r"[0-9]", page)) and int(page) > 0:
        if int(page) > (no_pages + 2):
            return HttpResponseRedirect(reverse("dashboard:applicants"))
        page = int(page)
    else:
        page = 1

    recruiters = recruiters[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    return render(
        request,
        "dashboard/company/recruiters.html",
        {
            "recruiters": recruiters,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "company": company,
        },
    )


@permission_required("activity_edit", "activity_view")
def company_jobposts(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    job_posts = company.get_jobposts()
    items_per_page = 100
    no_pages = int(math.ceil(float(job_posts.count()) / items_per_page))
    page = request.GET.get("page")
    if page and bool(re.search(r"[0-9]", page)) and int(page) > 0:
        if int(page) > (no_pages + 2):
            return HttpResponseRedirect(reverse("dashboard:applicants"))
        page = int(page)
    else:
        page = 1

    job_posts = job_posts[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    return render(
        request,
        "dashboard/company/job_posts.html",
        {
            "company": company,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "job_posts": job_posts,
        },
    )


@permission_required("activity_edit", "activity_view")
def company_tickets(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    items_per_page = 100
    tickets = company.get_company_tickets()
    no_pages = int(math.ceil(float(tickets.count()) / items_per_page))
    page = request.GET.get("page")
    if page and bool(re.search(r"[0-9]", page)) and int(page) > 0:
        if int(page) > (no_pages + 2):
            return HttpResponseRedirect(reverse("dashboard:applicants"))
        page = int(page)
    else:
        page = 1

    tickets = tickets[(page - 1) * items_per_page : page * items_per_page]
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    return render(
        request,
        "dashboard/company/tickets.html",
        {
            "tickets": tickets,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "company": company,
        },
    )




@permission_required("activity_edit")
def edit_menu(request, menu_id, company_id):
    company = get_object_or_404(Company, id=company_id)
    menu = get_object_or_404(Menu, id=menu_id, company=company)
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



@permission_required("activity_edit")
def delete_menu(request, menu_id, company_id):
    company = get_object_or_404(Company, id=company_id)
    menu = Menu.objects.filter(id=menu_id, company=company)
    if menu:
        menu = menu[0]
        menu.delete()
        data = {"error": False, "response": "Menu Deleted Successfully"}
    else:
        data = {"error": True, "response": "Some Problem Occurs"}
    return HttpResponse(json.dumps(data))




@permission_required("activity_edit")
def menu_status(request, menu_id, company_id):
    company = get_object_or_404(Company, id=company_id)
    menu = Menu.objects.filter(id=menu_id, company=company)
    if menu:
        menu = menu[0]
        if menu.status:
            menu.status = False
        else:
            menu.status = True
        menu.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))



@permission_required("activity_edit")
def menu_order(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    menu = get_object_or_404(Menu, id=request.GET.get("menu_id"), company=company)
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
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))




@permission_required("activity_edit")
def enable_agency(request, agency_id):
    agency = get_object_or_404(User, id=agency_id)
    if agency.is_active:
        agency.is_active = False
    else:
        agency.is_active = True
    agency.save()
    page = request.GET.get("page")
    url = reverse("dashboard:companies", kwargs={"company_type": "consultant"})
    if request.GET.get("status") == "active":
        url = (
            reverse("dashboard:companies", kwargs={"company_type": "consultant"})
            + "?page="
            + page
            + "&active=true"
        )
    if request.GET.get("status") == "inactive":
        url = (
            reverse("dashboard:companies", kwargs={"company_type": "consultant"})
            + "?page="
            + page
            + "&active=false"
        )
    if request.GET.get("status") == "admin_active":
        url = (
            reverse("dashboard:companies", kwargs={"company_type": "consultant"})
            + "?page="
            + page
            + "&admin=true"
        )
    if request.GET.get("status") == "admin_inactive":
        url = (
            reverse("dashboard:companies", kwargs={"company_type": "consultant"})
            + "?page="
            + page
            + "&admin=false"
        )
    return HttpResponseRedirect(url)


@permission_required("activity_edit")
def removing_duplicate_companies(request):
    all_duplicate_companies = Company.objects.filter()
    if request.method == "POST":
        if request.POST.getlist("duplicate_companies"):
            duplicate_companies = request.POST.getlist("duplicate_companies")
            company_id = request.POST.get("company")
            all_company = Company.objects.filter(id__in=duplicate_companies)
            all_duplicate_companies = all_company.values_list("id", flat=True)
            each_company = Company.objects.filter(id=company_id)
            jobposts = JobPost.objects.filter(company_id__in=all_duplicate_companies)
            users = User.objects.filter(company_id__in=all_duplicate_companies)
            if each_company:
                company = each_company[0]
                jobposts.update(company=company)
                users.update(company=company)
            data = {"error": False, "response": "Company Jobposts updated successfully"}
        else:
            data = {"error": True, "response": "Please Select the duplicate companies"}
        return HttpResponse(json.dumps(data))

    return render(
        request,
        "dashboard/company/update_jobposts.html",
        {"all_duplicate_companies": all_duplicate_companies},
    )
