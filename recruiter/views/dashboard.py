from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from peeldb.models import City, User, Company
from mpcomp.views import recruiter_login_required



@recruiter_login_required
def dashboard(request):
    # active_jobs = JobPost.objects.filter(user=request.user, status='Live')
    # return render(request, 'recruiter/dashboard.html', {'active_jobs':
    # active_jobs})
    return HttpResponseRedirect(reverse("recruiter:list"))


def post_job(request):
    return render(request, "recruiter_v2/post_job.html", {})


def how_it_works(request):
    return render(request, "recruiter/how_it_works.html", {})


def interview_location(request, location_count):
    location_count = int(location_count) + 1
    cities = City.objects.all()
    selected_locations = request.POST.get("selected_locations")
    return render(
        request,
        "recruiter/job/add_interview_location.html",
        {
            "selected_locations": selected_locations,
            "interview_location_count": location_count,
            "cities": cities,
        },
    )


def create_slug(tempslug):
    tempslug = tempslug.split("@")
    if tempslug[1] != "gmail.com":
        user = tempslug[1].split(".")[0] + "-" + tempslug[0]
        return user
    slugcount = 0
    tempslug = tempslug[0]
    while True:
        try:
            User.objects.get(username=tempslug)
            slugcount = slugcount + 1
            if isinstance(tempslug.split("-")[-1], int):
                tempslug = tempslug.split("-")[0] + str(tempslug.split("-")[-1] + 1)
            else:
                tempslug = tempslug + str(slugcount)
        except ObjectDoesNotExist:
            return tempslug


def get_autocomplete(request):
    companies = Company.objects.filter(
        name__icontains=request.GET.get("q"),
        company_type="Company",
        id__in=User.objects.filter(is_admin=False).values_list("company", flat=True),
    ).distinct()[:10]
    companies_names = []
    for each in companies:
        companies_names.append(each.name)
    if request.GET.get("register_name"):
        company = Company.objects.filter(name=request.GET.get("register_name")).first()
        if company:
            each_obj = {}
            each_obj["website"] = company.website
            each_obj["company_type"] = company.company_type
            each_obj["company_id"] = company.id
            each_obj["company_id"] = company.id
            each_obj["company_address"] = company.address
            each_obj["company_profile"] = company.profile
            data = {"company": each_obj}
            return data
    data = {"response": companies_names}
    return data

