import json
import math
import re
import json

from django.urls import reverse
from django.db.models import Count, Q
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from mpcomp.views import (
    get_aws_file_path,
    get_prev_after_pages_count,
    permission_required,
)
from mpcomp.aws import AWS
from peeldb.models import (
    City,
    Country,
    FunctionalArea,
    Industry,
    JobPost,
    Language,
    Qualification,
    Skill,
    State,
    SKILL_TYPE,
    User,
)
from dashboard.forms import CityForm

from ..forms import (
    CityForm,
    CountryForm,
    FunctionalAreaForm,
    IndustryForm,
    LanguageForm,
    QualificationForm,
    SkillForm,
    StateForm,
)


# Functions to move here from main views.py:

@permission_required("activity_view", "activity_edit")
def country(request):
    if request.method == "GET":
        countries = Country.objects.all().order_by("name")
        states = State.objects.all().order_by("name")
        cities = City.objects.filter(status="Enabled").order_by(
            "name"
        )
        return render(
            request,
            "dashboard/base_data/country.html",
            {"countries": countries, "states": states, "cities": cities},
        )
    if request.user.is_staff or request.user.has_perm("activity_edit"):
        if request.POST.get("mode") == "add_country":
            new_country = CountryForm(request.POST)
            if new_country.is_valid():
                country = new_country.save()
                country.slug = slugify(country.name)
                country.save()
                data = {"error": False, "message": "Country Added Successfully"}
            else:
                data = {"error": True, "message": new_country.errors["name"]}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "edit_country":
            country = Country.objects.get(id=request.POST.get("id"))
            new_country = CountryForm(request.POST, instance=country)
            if new_country.is_valid():
                new_country.save()
                data = {"error": False, "message": "Country Updated Successfully"}
            else:
                data = {"error": True, "message": new_country.errors}
            return HttpResponse(json.dumps(data))
        if request.POST.get("mode") == "remove_country":
            country = Country.objects.filter(id=request.POST.get("id"))
            if country:
                country[0].delete()
                data = {"error": False, "message": "Country Removed Successfully"}
            else:
                data = {"error": True, "message": "Country Not found"}
            return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "message": "Only Admin Can create/edit country"}
        return HttpResponse(json.dumps(data))

    if request.POST.get("mode") == "get_states":
        country = Country.objects.filter(id=request.POST.get("c_id")).first()
        if not country:
            data = {"html": "", "slug": ""}
            return HttpResponse(json.dumps(data))
        states = State.objects.filter(country=country).order_by("name")
        slist = ""
        for s in states:
            if s.status == "Enabled":
                slist = (
                    slist
                    + '<div class="ticket"><a class="name_ticket" id="'
                    + s.status
                    + ' " href="'
                    + str(s.id)
                    + '">'
                    + s.name
                    + "</a>("
                    + str(s.get_no_of_jobposts().count())
                    + ')<div class="remove_ticket remove_states"><a class="delete" href="'
                    + str(s.id)
                    + ' " countryId="'
                    + str(s.country.id)
                    + ' " id="'
                    + s.status
                    + ' "><i class="fa fa-trash-o"></i></a></div>'
                    + '<div class="actions_ticket"><a href="'
                    + str(s.id)
                    + '" countryId="'
                    + str(s.country.id)
                    + ' " id="'
                    + s.status
                    + ' "><i class="fa fa-toggle-off"></i></a>'
                )
            else:
                temp = "disabled_ticket"
                slist = (
                    slist
                    + '<div class="ticket '
                    + temp
                    + ' "><a class="name_ticket" id="'
                    + s.status
                    + ' " href="'
                    + str(s.id)
                    + '">'
                    + s.name
                    + "</a>("
                    + str(s.get_no_of_jobposts().count())
                    + ')<div class="remove_ticket remove_states"><a class="delete" href="'
                    + str(s.id)
                    + ' " countryId="'
                    + str(s.country.id)
                    + ' " id="'
                    + s.status
                    + ' "><i class="fa fa-trash-o"></i></a></div>'
                    + '<div class="actions_ticket"><a class="edit" href="'
                    + str(s.id)
                    + ' " countryId="'
                    + str(s.country.id)
                    + ' " id="'
                    + s.status
                    + ' "><i class="fa fa-toggle-on"></i></a>'
                )
            slist = slist + '</div><div class="clearfix"></div></div>'
        data = {"html": slist, "slug": country.slug}
        return HttpResponse(json.dumps(data))

    if request.user.is_staff or request.user.has_perm("activity_edit"):
        if request.POST.get("mode") == "add_state":
            new_state = StateForm(request.POST)
            if new_state.is_valid():
                s = new_state.save()
                s.slug = slugify(s.name)
                s.save()
                data = {
                    "error": False,
                    "message": "State Added Successfully",
                    "id": s.id,
                    "status": s.status,
                    "name": s.name,
                }
            else:
                data = {"error": True, "message": new_state.errors}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "edit_state":
            state = State.objects.get(id=request.POST.get("id"))
            new_state = StateForm(request.POST, instance=state)
            if new_state.is_valid():
                new_state.save()
                data = {"error": False, "message": "State Updated Successfully"}
            else:
                data = {"error": True, "message": new_state.errors}
            return HttpResponse(json.dumps(data))
        if request.POST.get("mode") == "remove_state":
            state = State.objects.filter(id=request.POST.get("id"))
            if state:
                state[0].delete()
                data = {"error": False, "message": "State Removed Successfully"}
            else:
                data = {"error": True, "message": "State Not found"}
            return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "message": "Only Admin Can create/edit country"}
        return HttpResponse(json.dumps(data))

    if request.POST.get("mode") == "get_cities":
        state = State.objects.filter(id=request.POST.get("s_id")).first()
        if not state:
            data = {"html": "", "country": "", "state_slug": ""}
            return HttpResponse(json.dumps(data))
        country = state.country.id
        cities = City.objects.filter(state=state).order_by("name")
        clist = ""
        for c in cities:
            if c.status == "Enabled":
                clist = (
                    clist
                    + '<div class="ticket"><a class="name_ticket" id="'
                    + c.status
                    + ' " href="'
                    + str(c.id)
                    + '">'
                    + c.name
                    + "</a>("
                    + str(c.get_no_of_jobposts().count())
                    + ')<div class="remove_ticket remove_city"><a class="delete" href="'
                    + str(c.id)
                    + ' " id="'
                    + c.status
                    + '"><i class="fa fa-trash-o"></i></a></div>'
                    + '<div class="actions_ticket"><a href="'
                    + str(c.id)
                    + ' " stateId="'
                    + str(c.state.id)
                    + ' " id="'
                    + c.status
                    + ' "><i class="fa fa-toggle-off"></i></a></div><a href="'
                    + reverse("job_locations", kwargs={"location": c.slug})
                    + '" target="_blank"><i class="fa fa-eye"></i></a><a class="add_other_city" title="Add Other City" id="'
                    + str(c.id)
                    + '" data-state="'
                    + str(c.state.id)
                    + '"><i class="fa fa-plus"></i></a>'
                )
            else:
                temp = "disabled_ticket"
                clist = (
                    clist
                    + '<div class="ticket '
                    + temp
                    + ' "><a class="name_ticket" id="'
                    + c.status
                    + ' " href="'
                    + str(c.id)
                    + '">'
                    + c.name
                    + "</a>("
                    + str(c.get_no_of_jobposts().count())
                    + ')<div class="remove_ticket remove_city"><a class="delete" href="'
                    + str(c.id)
                    + ' " id="'
                    + c.status
                    + '"><i class="fa fa-trash-o"></i></a></div>'
                    + '<div class="actions_ticket"><a class="edit" href="'
                    + str(c.id)
                    + ' " stateId="'
                    + str(c.state.id)
                    + ' " id="'
                    + c.status
                    + ' "><i class="fa fa-toggle-on"></i></a></div>'
                )
            clist = (
                clist
                + '<span class="meta_title meta_data">'
                + str(c.meta_title)
                + "</span>"
                + '<span class="meta_description meta_data">'
                + str(c.meta_description)
                + "</span>"
                + '<span class="internship_meta_title meta_data">'
                + str(c.internship_meta_title)
                + "</span>"
                + '<span class="internship_meta_description meta_data">'
                + str(c.internship_meta_description)
                + "</span>"
            )
            clist = clist + '</div><div class="clearfix"></div></div>'
        data = {"html": clist, "country": country, "state_slug": state.slug}
        return HttpResponse(json.dumps(data))
    if request.POST.get("mode") == "get_city_info":
        city = City.objects.filter(id=request.POST.get("city")).first()
        if city:
            data = {
                "city": city.id,
                "country": city.state.country.id,
                "state": city.state.id,
                "slug": city.slug,
            }
            return HttpResponse(json.dumps(data))
        else:
            data = {}
            return HttpResponse(json.dumps(data))

    if request.user.is_staff or request.user.has_perm("activity_edit"):
        if request.POST.get("mode") == "add_city":
            new_city = CityForm(request.POST)
            if new_city.is_valid():
                c = new_city.save()
                c.slug = slugify(c.name)
                c.save()
                data = {
                    "error": False,
                    "message": "City Added Successfully",
                    "id": c.id,
                    "status": c.status,
                    "name": c.name,
                }
            else:
                data = {"error": True, "message": new_city.errors["name"]}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "add_other_city":
            new_city = CityForm(request.POST)
            if new_city.is_valid():
                c = new_city.save()
                c.slug = slugify(c.name)
                c.save()
                data = {
                    "error": False,
                    "message": "City Added Successfully",
                    "id": c.id,
                    "status": c.status,
                    "name": c.name,
                }
            else:
                data = {"error": True, "message": new_city.errors["name"]}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "edit_city":
            city = City.objects.get(id=request.POST.get("id"))
            new_city = CityForm(request.POST, instance=city)
            if new_city.is_valid():
                new_city.save()
                if State.objects.filter(id=request.POST.get("state")):
                    city.state = State.objects.filter(id=request.POST.get("state"))[0]
                if request.POST.get("meta_title"):
                    city.meta_title = request.POST.get("meta_title")
                if request.POST.get("meta_description"):
                    city.meta_description = request.POST.get("meta_description")
                if request.POST.get("internship_meta_title"):
                    city.internship_meta_title = request.POST.get(
                        "internship_meta_title"
                    )
                if request.POST.get("internship_meta_description"):
                    city.internship_meta_description = request.POST.get(
                        "internship_meta_description"
                    )
                if request.POST.get("page_content"):
                    city.page_content = request.POST.get("page_content")
                city.save()
                data = {"error": False, "message": "City Updated Successfully"}
            else:
                data = {"error": True, "message": new_city.errors}
            return HttpResponse(json.dumps(data))
        if request.POST.get("mode") == "remove_city":
            city = City.objects.filter(id=request.POST.get("id"))
            if city:
                city[0].delete()
                data = {"error": False, "message": "City Removed Successfully"}
            else:
                data = {"error": True, "message": "City Not Found"}
            return HttpResponse(json.dumps(data))
    else:
        data = {"error": True, "message": "Only Admin Can create/edit country"}
        return HttpResponse(json.dumps(data))

    if request.POST.get("mode") == "country_status":
        country = Country.objects.filter(id=request.POST.get("id")).first()
        if not country:
            data = {"error": True, "message": "Country Not Found"}
            return HttpResponse(json.dumps(data))
        if request.user.is_staff or request.user.has_perm("activity_edit"):
            if country.status == "Enabled":
                country.status = "Disabled"
                country.save()
                states = State.objects.filter(country_id=country.id)
                if states:
                    State.objects.filter(country_id=country.id).update(
                        status="Disabled"
                    )
                    City.objects.filter(state_id__in=states).update(status="Disabled")

                data = {"error": False, "message": "Country Disabled Successfully"}
                return HttpResponse(json.dumps(data))
            else:
                country.status = "Enabled"
                country.save()
                states = State.objects.filter(country_id=country.id)
                if states:
                    State.objects.filter(country_id=country.id).update(status="Enabled")
                    City.objects.filter(state_id__in=states).update(status="Enabled")

                data = {"error": False, "message": "Country Enabled Successfully"}
                return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "message": "Only Admin Can edit country status"}
            return HttpResponse(json.dumps(data))

    if request.POST.get("mode") == "state_status":
        country_status = False
        state = State.objects.filter(id=request.POST.get("id")).first()
        if not state:
            data = {"error": True, "message": "State Not Found"}
            return HttpResponse(json.dumps(data))
        if request.user.is_staff or request.user.has_perm("activity_edit"):
            if state.status == "Enabled":
                state.status = "Disabled"
                state.save()
                cities = state.state.all()
                if cities:
                    cities.update(status="Disabled")

                if not State.objects.filter(country=state.country, status="Enabled"):
                    if state.country.status != "Disabled":
                        state.country.status = "Disabled"
                        country_status = True
                        state.country.save()

                data = {
                    "error": False,
                    "message": "State Disabled Successfully",
                    "country_status": country_status,
                    "country_id": state.country.id,
                }
            else:
                state.status = "Enabled"
                state.save()
                state.country.status = "Enabled"
                state.country.save()
                cities = state.state.all()
                if cities:
                    cities.update(status="Enabled")

                data = {
                    "error": False,
                    "message": "State Enabled Successfully",
                    "country_status": country_status,
                    "country_id": state.country.id,
                }
            return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "message": "Only Admin Can create/edit country"}
            return HttpResponse(json.dumps(data))

    if request.POST.get("mode") == "city_status":
        state_status = False
        country_status = False
        city = City.objects.filter(id=request.POST.get("id")).first()
        if not city:
            data = {"error": True, "message": "City Not Found"}
            return HttpResponse(json.dumps(data))
        if request.user.is_staff or request.user.has_perm("activity_edit"):
            if city.status == "Enabled":
                city.status = "Disabled"
                city.save()

                if not City.objects.filter(state=city.state, status="Enabled"):
                    if city.state.status != "Disabled":
                        city.state.status = "Disabled"
                        state_status = True
                        city.state.save()

                    if not State.objects.filter(
                        country=city.state.country, status="Enabled"
                    ):
                        if city.state.country.status != "Disabled":
                            city.state.country.status = "Disabled"
                            country_status = True
                            city.state.country.save()

                data = {
                    "error": False,
                    "message": "City Disabled Successfully",
                    "state_status": state_status,
                    "country_status": country_status,
                    "state_id": city.state.id,
                    "country_id": city.state.country.id,
                }
                return HttpResponse(json.dumps(data))
            else:
                city.status = "Enabled"
                city.save()
                city.state.status = "Enabled"
                city.state.save()
                if city.state.country.status == "Disabled":
                    city.state.country.status = "Enabled"
                    city.state.country.save()
                data = {
                    "error": False,
                    "message": "City Enabled Successfully",
                    "state_status": state_status,
                    "country_status": country_status,
                    "state_id": city.state.id,
                    "country_id": city.state.country.id,
                }
                return HttpResponse(json.dumps(data))
        else:
            data = {"error": True, "message": "Only Admin Can create/edit country"}
            return HttpResponse(json.dumps(data))



@permission_required("activity_view", "activity_edit")
def locations(request, status):
    # Get base queryset based on status
    if status == "active":
        locations_qs = (
            City.objects.filter(status="Enabled")
            .annotate(num_posts=Count("locations"))
            .prefetch_related("state", "state__country")
        )
    else:
        locations_qs = (
            City.objects.filter(status="Disabled")
            .annotate(num_posts=Count("locations"))
            .prefetch_related("state", "state__country")
        )
    
    # Handle search from both GET and POST
    search_term = ""
    sort_by = request.GET.get("sort", "name")  # Default sort by name
    
    if request.method == "POST":
        if request.POST.get("mode") == "remove_city":
            if request.user.is_staff or request.user.has_perm("activity_edit"):
                city_id = request.POST.get("id")
                if city_id:
                    city = City.objects.filter(id=city_id).first()
                    if city:
                        # Check for active job posts using this city
                        active_job_count = JobPost.objects.filter(
                            location=city, 
                            status__in=["Live", "Published"]
                        ).count()
                        
                        if active_job_count > 0:
                            data = {
                                "error": True, 
                                "message": f"Cannot delete city. {active_job_count} active job post(s) are using this location. Please reassign or deactivate these jobs first."
                            }
                        else:
                            city.delete()
                            data = {"error": False, "message": "City Removed Successfully"}
                    else:
                        data = {"error": True, "message": "City Not Found"}
                else:
                    data = {"error": True, "message": "Invalid city ID"}
            else:
                data = {"error": True, "message": "Permission denied"}
            return HttpResponse(json.dumps(data))
            
        elif request.POST.get("mode") == "edit":
            if request.user.is_staff or request.user.has_perm("activity_edit"):
                city_id = request.POST.get("id")
                if not city_id:
                    data = {"error": True, "message": "City ID is required"}
                    return HttpResponse(json.dumps(data))
                
                city = City.objects.filter(id=int(city_id)).first()
                if not city:
                    data = {"error": True, "message": "City Not Found"}
                    return HttpResponse(json.dumps(data))
                
                form = CityForm(request.POST, instance=city)
                is_valid = True
                
                # Validate JSON meta field if provided
                if request.POST.get("meta"):
                    try:
                        json.loads(request.POST.get("meta"))
                    except (json.JSONDecodeError, ValueError) as e:
                        form.add_error("meta", f"Enter Valid JSON Format - {str(e)}")
                        is_valid = False
                
                if form.is_valid() and is_valid:
                    # Check if state change is valid
                    if request.POST.get("state"):
                        try:
                            new_state = State.objects.get(id=request.POST.get("state"), status="Enabled")
                            city.state = new_state
                        except State.DoesNotExist:
                            data = {"error": True, "message": "Invalid state selected", "id": city_id}
                            return HttpResponse(json.dumps(data))
                    
                    form.save()
                    
                    # Update additional fields
                    if request.POST.get("page_content"):
                        city.page_content = request.POST.get("page_content")
                    if request.POST.get("internship_page_content"):
                        city.internship_page_content = request.POST.get("internship_page_content")
                    if request.POST.get("meta"):
                        city.meta = json.loads(request.POST.get("meta"))
                    
                    city.save()
                    data = {"error": False, "message": "City Updated Successfully"}
                else:
                    data = {
                        "error": True,
                        "message": form.errors,
                        "id": city_id,
                    }
            else:
                data = {"error": True, "message": "Permission denied"}
            return HttpResponse(json.dumps(data))
        
        elif request.POST.get("mode") == "move_jobs":
            if request.user.is_staff or request.user.has_perm("activity_edit"):
                from_city_id = request.POST.get("from_city_id")
                to_city_id = request.POST.get("to_city_id")

                try:
                    from_city = City.objects.get(id=from_city_id)
                    to_city = City.objects.get(id=to_city_id)

                    # Get all job posts that have the source city
                    job_posts = JobPost.objects.filter(location=from_city)
                    moved_count = 0

                    for job_post in job_posts:
                        # Remove the old city and add the new one
                        job_post.location.remove(from_city)
                        job_post.location.add(to_city)
                        moved_count += 1

                    data = {
                        "error": False,
                        "message": f"Successfully moved {moved_count} jobs from '{from_city.name}' to '{to_city.name}'",
                        "moved_count": moved_count,
                    }
                except City.DoesNotExist:
                    data = {
                        "error": True,
                        "message": "Invalid city selected",
                    }
                except Exception as e:
                    data = {
                        "error": True,
                        "message": f"Error moving jobs: {str(e)}",
                    }
            else:
                data = {"error": True, "message": "Permission denied"}
            return HttpResponse(json.dumps(data))
        
        # Handle search via POST
        elif request.POST.get("search"):
            search_term = request.POST.get("search").strip()
    
    # Handle search via GET (for pagination links)
    if not search_term:
        search_term = request.GET.get("search", "").strip()
    
    # Apply search filter
    if search_term:
        locations_qs = locations_qs.filter(name__icontains=search_term)
    
    # Apply sorting
    if sort_by == "name":
        locations_qs = locations_qs.order_by("name")
    elif sort_by == "job_posts_asc":
        locations_qs = locations_qs.order_by("num_posts", "name")
    elif sort_by == "job_posts_desc":
        locations_qs = locations_qs.order_by("-num_posts", "name")
    else:
        locations_qs = locations_qs.order_by("name")
    
    # Pagination
    items_per_page = 100
    paginator = Paginator(locations_qs, items_per_page)
    page_number = request.GET.get("page", 1)
    
    try:
        page_obj = paginator.get_page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.get_page(1)
    
    # Get pagination context
    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page_obj.number, paginator.num_pages
    )
    
    # Get enabled cities for dropdown
    cities = City.objects.filter(status="Enabled").prefetch_related("state", "state__country").order_by("name")
    
    # Get all states for the state dropdown in edit form
    states = State.objects.filter(status="Enabled").prefetch_related("country").order_by("country__name", "name")
    
    context = {
        "locations": page_obj,
        "cities": cities,
        "states": states,
        "aft_page": aft_page,
        "after_page": after_page,
        "prev_page": prev_page,
        "previous_page": previous_page,
        "current_page": page_obj.number,
        "last_page": paginator.num_pages,
        "status": status,
        "search_term": search_term,
        "search_value": search_term,  # For backward compatibility
        "sort_by": sort_by,
    }
    
    return render(request, "dashboard/locations.html", context)



@permission_required("activity_view", "activity_edit")
def tech_skills(request):
    if request.method == "GET":
        skills = Skill.objects.all().order_by("name")

        if request.GET.get("search"):
            skills = Skill.objects.filter(name__icontains=request.GET.get("search"))
        status = request.GET.get("status")
        if status:
            if status == "active":
                skills = skills.filter(status="Active")
            elif status == "inactive":
                skills = skills.filter(status="InActive")
            else:
                skills = skills.filter(skill_type=status)

        items_per_page = 20
        no_pages = int(math.ceil(float(skills.count()) / items_per_page))

        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                return HttpResponseRedirect(reverse("dashboard:tech_skills"))
            else:
                page = int(request.GET.get("page"))
        else:
            page = 1

        skills = skills[(page - 1) * items_per_page : page * items_per_page]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        return render(
            request,
            "dashboard/base_data/technical_skills.html",
            {
                "search": request.GET.get("search"),
                "status": status,
                "skills": skills,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
                "skill_types": SKILL_TYPE,
            },
        )
    else:
        if request.user.is_staff == "Admin" or request.user.has_perm("activity_edit"):
            if request.POST.get("mode") == "add_skill":
                new_skill = SkillForm(request.POST, request.FILES)
                if new_skill.is_valid():
                    new_skill = new_skill.save(commit=False)
                    if request.FILES and request.FILES.get("icon"):
                        file_path = get_aws_file_path(
                            request.FILES.get("icon"),
                            "technology/icons/",
                            slugify(request.POST.get("name")),
                        )
                        new_skill.icon = file_path
                    new_skill.status = "InActive"
                    new_skill.skill_type = request.POST.get("skill_type")
                    new_skill.save()
                    data = {"error": False, "message": "Skill Added Successfully"}
                else:
                    data = {"error": True, "message": new_skill.errors}
                return HttpResponse(json.dumps(data))
            if request.POST.get("mode") == "edit_skill":
                skill = Skill.objects.filter(id=request.POST.get("id")).first()
                if skill:
                    new_skill = SkillForm(request.POST, request.FILES, instance=skill)
                    try:
                        if request.POST.get("meta"):
                            json.loads(request.POST.get("meta"))
                        valid = True
                    except BaseException as e:
                        new_skill.errors["meta"] = "Enter Valid Json Format - " + str(e)
                        valid = False
                    if new_skill.is_valid() and valid:
                        edit_tech_skills(skill, request)
                        data = {"error": False, "message": "Skill Updated Successfully"}
                        return HttpResponse(json.dumps(data))
                    else:
                        data = {"error": True, "response": new_skill.errors}
                    return HttpResponse(json.dumps(data))
                else:
                    data = {
                        "error": True,
                        "message": "Skill Not Found",
                        "page": (
                            request.POST.get("page") if request.POST.get("page") else 1
                        ),
                    }
                    return HttpResponse(json.dumps(data))
        else:
            data = {
                "error": True,
                "message": "Only Admin can add/edit Technical Skill",
                "page": request.POST.get("page") if request.POST.get("page") else 1,
            }
            return HttpResponse(json.dumps(data))



def edit_tech_skills(skill, request):
    if request.FILES.get("icon"):
        if skill.icon:
            url = str(skill.icon).split("cdn.peeljobs.com")[-1:]
            AWS().cloudfront_invalidate(paths=url)
        file_path = get_aws_file_path(
            request.FILES.get("icon"),
            "technology/icons/",
            slugify(request.POST.get("name")),
        )
        skill.icon = file_path
    skill.name = request.POST.get("name")
    if request.POST.get("slug"):
        skill.slug = request.POST.get("slug")
    if request.POST.get("skill_type"):
        skill.skill_type = request.POST.get("skill_type")
    if request.POST.get("page_content"):
        skill.page_content = request.POST.get("page_content")
    if request.POST.get("meta"):
        skill.meta = json.loads(request.POST.get("meta"))
    skill.save()



@permission_required("activity_edit")
def delete_skill(request, skill_id):
    skill = Skill.objects.filter(id=skill_id)
    if skill:
        skill.delete()
        data = {
            "error": False,
            "message": "Skill Removed Successfully",
            "path": request.path,
        }
    else:
        data = {"error": True, "message": "Skill Not Found", "path": request.path}
    return HttpResponse(json.dumps(data))



@permission_required("activity_edit")
def skill_status(request, skill_id):
    skill = Skill.objects.filter(id=skill_id).first()
    if skill:
        skill.status = "InActive" if skill.status == "Active" else "Active"
        skill.save()
        data = {"error": False, "response": "Skill Status Changed Successfully"}
    else:
        data = {"error": True, "response": "skill not exists"}
    return HttpResponse(json.dumps(data))




@permission_required("activity_view", "activity_edit")
def languages(request):
    if request.method == "GET":
        languages = Language.objects.all().order_by("name")
        if request.GET.get("search"):
            languages = languages.filter(name__icontains=request.GET.get("search"))
        items_per_page = 10
        no_pages = int(math.ceil(float(languages.count()) / items_per_page))

        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                return HttpResponseRedirect(reverse("dashboard:languages"))
            else:
                page = int(request.GET.get("page"))
        else:
            page = 1

        languages = languages[(page - 1) * items_per_page : page * items_per_page]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        search_value = request.GET.get("search") if request.GET.get("search") else None
        return render(
            request,
            "dashboard/base_data/languages.html",
            {
                "search_value": search_value,
                "languages": languages,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
            },
        )

    if request.user.user_type == "Admin" or request.user.has_perm("activity_edit"):

        if request.POST.get("mode") == "add_language":
            new_language = LanguageForm(request.POST)
            if new_language.is_valid():
                new_language.save()
                data = {"error": False, "message": "Language Added Successfully"}
            else:
                data = {"error": True, "message": new_language.errors["name"]}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "edit_language":
            language = Language.objects.get(id=request.POST.get("id"))
            new_language = LanguageForm(request.POST, instance=language)
            if new_language.is_valid():
                new_language.save()
                data = {
                    "error": False,
                    "message": "Language Updated Successfully",
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            else:
                data = {
                    "error": True,
                    "message": new_language.errors["name"],
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            return HttpResponse(json.dumps(data))
    else:
        data = {
            "error": True,
            "message": "Only Admin can add/edit Qualification",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
        return HttpResponse(json.dumps(data))



@permission_required("activity_edit")
def delete_language(request, language_id):
    Language.objects.get(id=language_id).delete()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))



@permission_required("activity_view", "activity_edit")
def qualifications(request):
    if request.method == "GET":
        qualifications = Qualification.objects.all().order_by("name")
        if request.GET.get("search"):
            qualifications = qualifications.filter(
                name__icontains=request.GET.get("search")
            )
        if request.GET.get("status") == "Active":
            qualifications = qualifications.filter(status="Active")
        elif request.GET.get("status") == "InActive":
            qualifications = qualifications.filter(status="InActive")

        items_per_page = 10
        no_pages = int(math.ceil(float(qualifications.count()) / items_per_page))

        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                return HttpResponseRedirect(reverse("dashboard:qualifications"))
            page = int(request.GET.get("page"))
        else:
            page = 1

        qualifications = qualifications[
            (page - 1) * items_per_page : page * items_per_page
        ]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        status = request.GET.get("status") if request.GET.get("status") else None
        search = request.GET.get("search") if request.GET.get("search") else None
        return render(
            request,
            "dashboard/base_data/qualifications.html",
            {
                "status": status,
                "qualifications": qualifications,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
                "search": search,
            },
        )
    if request.user.is_staff or request.user.has_perm("activity_edit"):
        if request.POST.get("mode") == "add_qualification":
            new_qualification = QualificationForm(request.POST)
            if new_qualification.is_valid():
                new_qualification.save()
                data = {"error": False, "message": "Qualification Added Successfully"}
            else:
                data = {"error": True, "message": new_qualification.errors["name"]}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "edit_qualification":
            qualification = Qualification.objects.get(id=request.POST.get("id"))
            new_qualification = QualificationForm(request.POST, instance=qualification)
            if new_qualification.is_valid():
                new_qualification.save()
                data = {
                    "error": False,
                    "message": "Qualification Updated Successfully",
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            else:
                data = {
                    "error": True,
                    "message": new_qualification.errors["name"],
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            return HttpResponse(json.dumps(data))
    else:
        data = {
            "error": True,
            "message": "Only Admin can add/edit Qualification",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
        return HttpResponse(json.dumps(data))



@permission_required("activity_edit")
def delete_qualification(request, qualification_id):
    Qualification.objects.get(id=qualification_id).delete()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))



@permission_required("activity_edit")
def qualification_status(request, qualification_id):
    qualification = Qualification.objects.filter(id=qualification_id).first()
    if qualification:
        qualification.status = (
            "InActive" if qualification.status == "Active" else "Active"
        )
        qualification.save()
        data = {
            "error": False,
            "response": "Qualification Status Changed Successfully",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
    else:
        data = {
            "error": True,
            "response": "Qualification not exists",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
    return HttpResponse(json.dumps(data))



@permission_required("activity_view", "activity_edit")
def industries(request):
    if request.method == "GET":
        industries = Industry.objects.all().order_by("name")
        if request.GET.get("search"):
            industries = industries.filter(name__icontains=request.GET.get("search"))
        if request.GET.get("status") == "active":
            industries = industries.filter(status="Active")
        elif request.GET.get("status") == "inactive":
            industries = industries.filter(status="InActive")

        items_per_page = 15
        no_pages = int(math.ceil(float(industries.count()) / items_per_page))

        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                return HttpResponseRedirect(reverse("dashboard:industries"))
            page = int(request.GET.get("page"))
        else:
            page = 1

        industries = industries[(page - 1) * items_per_page : page * items_per_page]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        status = request.GET.get("status") if request.GET.get("status") else None
        search = request.GET.get("search") if request.GET.get("search") else None

        # Get all active industries for the transfer dropdown
        all_active_industries = Industry.objects.filter(status="Active").order_by("name")

        return render(
            request,
            "dashboard/base_data/industry.html",
            {
                "status": status,
                "search": search,
                "industries": industries,
                "all_active_industries": all_active_industries,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
            },
        )

    if request.user.is_staff or request.user.has_perm("activity_edit"):
        if request.POST.get("mode") == "add_industry":
            new_industry = IndustryForm(request.POST)
            if new_industry.is_valid():
                new_industry.save()
                data = {"error": False, "message": "Industry Added Successfully"}
            else:
                data = {"error": True, "message": new_industry.errors["name"]}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "edit_industry":
            industry = Industry.objects.get(id=request.POST.get("id"))
            new_industry = IndustryForm(request.POST, instance=industry)
            if new_industry.is_valid():
                new_industry.save()
                if request.POST.get("meta_title"):
                    industry.meta_title = request.POST.get("meta_title")
                if request.POST.get("meta_description"):
                    industry.meta_description = request.POST.get("meta_description")
                if request.POST.get("page_content"):
                    industry.page_content = request.POST.get("page_content")
                industry.save()
                data = {
                    "error": False,
                    "message": "Industry Updated Successfully",
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            else:
                data = {
                    "error": True,
                    "message": new_industry.errors,
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            return HttpResponse(json.dumps(data))
        if request.POST.get("mode") == "move_jobs":
            from_industry_id = request.POST.get("from_industry_id")
            to_industry_id = request.POST.get("to_industry_id")

            try:
                from_industry = Industry.objects.get(id=from_industry_id)
                to_industry = Industry.objects.get(id=to_industry_id)

                # Get all job posts that have the source industry
                job_posts = JobPost.objects.filter(industry=from_industry)
                moved_count = 0

                for job_post in job_posts:
                    # Remove the old industry and add the new one
                    job_post.industry.remove(from_industry)
                    job_post.industry.add(to_industry)
                    moved_count += 1

                data = {
                    "error": False,
                    "message": f"Successfully moved {moved_count} jobs from '{from_industry.name}' to '{to_industry.name}'",
                    "moved_count": moved_count,
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            except Industry.DoesNotExist:
                data = {
                    "error": True,
                    "message": "Invalid industry selected",
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            except Exception as e:
                data = {
                    "error": True,
                    "message": f"Error moving jobs: {str(e)}",
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            return HttpResponse(json.dumps(data))
    else:
        data = {
            "error": True,
            "message": "Only Admin can add/edit Industry",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
        return HttpResponse(json.dumps(data))



@permission_required("activity_edit")
def delete_industry(request, industry_id):
    Industry.objects.get(id=industry_id).delete()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))




@permission_required("activity_edit")
def industry_status(request, industry_id):
    industry = Industry.objects.filter(id=industry_id).first()
    if industry:
        industry.status = "InActive" if industry.status == "Active" else "Active"
        industry.save()
        data = {
            "error": False,
            "response": "Industry Status Changed Successfully",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
    else:
        data = {
            "error": True,
            "response": "Industry not exists",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
    return HttpResponse(json.dumps(data))



@permission_required("activity_view", "activity_edit")
def functional_area(request):
    if request.method == "GET":
        functional_areas = FunctionalArea.objects.all().order_by("name")
        if request.GET.get("search"):
            functional_areas = functional_areas.filter(
                name__icontains=request.GET.get("search")
            )
        if request.GET.get("status") == "active":
            functional_areas = functional_areas.filter(status="Active")
        elif request.GET.get("status") == "inactive":
            functional_areas = functional_areas.filter(status="InActive")

        items_per_page = 10
        no_pages = int(math.ceil(float(functional_areas.count()) / items_per_page))

        if (
            "page" in request.GET
            and bool(re.search(r"[0-9]", request.GET.get("page")))
            and int(request.GET.get("page")) > 0
        ):
            if int(request.GET.get("page")) > (no_pages + 2):
                return HttpResponseRedirect(reverse("dashboard:functional_areas"))
            page = int(request.GET.get("page"))
        else:
            page = 1

        functional_areas = functional_areas[
            (page - 1) * items_per_page : page * items_per_page
        ]
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        status = request.GET.get("status") if request.GET.get("status") else None
        search = request.GET.get("search") if request.GET.get("search") else None
        return render(
            request,
            "dashboard/base_data/functional_area.html",
            {
                "status": status,
                "search": search,
                "functional_areas": functional_areas,
                "aft_page": aft_page,
                "after_page": after_page,
                "prev_page": prev_page,
                "previous_page": previous_page,
                "current_page": page,
                "last_page": no_pages,
            },
        )

    if request.user.is_staff or request.user.has_perm("activity_edit"):
        if request.POST.get("mode") == "add_functional_area":
            new_functional_area = FunctionalAreaForm(request.POST)
            if new_functional_area.is_valid():
                new_functional_area.save()
                data = {"error": False, "message": "Functional Area Added Successfully"}
            else:
                data = {"error": True, "message": new_functional_area.errors["name"]}
            return HttpResponse(json.dumps(data))

        if request.POST.get("mode") == "edit_functional_area":
            functional_area = FunctionalArea.objects.get(id=request.POST.get("id"))
            new_functional_area = FunctionalAreaForm(
                request.POST, instance=functional_area
            )
            if new_functional_area.is_valid():
                new_functional_area.save()
                data = {
                    "error": False,
                    "message": "Industry Updated Successfully",
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            else:
                data = {
                    "error": True,
                    "message": new_functional_area.errors["name"],
                    "page": request.POST.get("page") if request.POST.get("page") else 1,
                }
            return HttpResponse(json.dumps(data))
    data = {
        "error": True,
        "message": "Only Admin can add/edit FunctionalArea",
        "page": request.POST.get("page") if request.POST.get("page") else 1,
    }
    return HttpResponse(json.dumps(data))



@permission_required("activity_edit")
def delete_functional_area(request, functional_area_id):
    FunctionalArea.objects.get(id=functional_area_id).delete()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))



@permission_required("activity_edit")
def functional_area_status(request, functional_area_id):
    functional_area = FunctionalArea.objects.filter(id=functional_area_id).first()
    if functional_area:
        functional_area.status = (
            "InActive" if functional_area.status == "Active" else "Active"
        )
        functional_area.save()
        data = {
            "error": False,
            "response": "Functional Area Status Changed Successfully",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
    else:
        data = {
            "error": True,
            "response": "Functional Area not exists",
            "page": request.POST.get("page") if request.POST.get("page") else 1,
        }
    return HttpResponse(json.dumps(data))
