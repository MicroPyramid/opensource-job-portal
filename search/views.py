import json
import math
import re

from django.urls import reverse
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.db.models import Q, F
from haystack.query import SQ, SearchQuerySet
from django.http import QueryDict

# from haystack.views import SearchView

from mpcomp.views import (
    get_prev_after_pages_count,
    get_valid_locations_list,
    get_valid_skills_list,
    get_meta_data,
    get_404_meta,
)
from peeldb.models import (
    City,
    FunctionalArea,
    Industry,
    JobPost,
    Qualification,
    Skill,
    State,
)
from pjob.refine_search import refined_search
from pjob.views import get_page_number
from search.forms import job_searchForm
from dashboard.tasks import save_search_results


# class search_job(SearchView):

#     template_name = 'search/search_results.html'
#     queryset = SearchQuerySet()
#     form_class = job_searchForm

#     def get_queryset(self):
#         queryset = super(search_job, self).get_queryset()
#         return queryset

#     def get_context_data(self):
#         context = super(search_job, self).get_context_data()
#         return context

#     def get_results(self):
#         results = self.form.search()
#         return results

#     def build_page(self):
#         jobs_list = self.results
#         no_of_jobs = len(jobs_list)

#         items_per_page = 10
#         no_pages = int(math.ceil(float(jobs_list.count()) / items_per_page))

#         page = 1

#         jobs_list = jobs_list[
#             (page - 1) * items_per_page:page * items_per_page]

#         prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(page, no_pages)

#         return (aft_page, after_page, prev_page, previous_page, page, no_pages, no_of_jobs, jobs_list)

#     def create_response(self):
#         (aft_page, after_page, prev_page, previous_page,
#          page, no_pages, no_of_jobs) = self.build_page()
#         results = [r.object for r in self.results]
#         param = ""
#         param = ('&' + 'q=' + self.form.cleaned_data['q'] + '&location=' + self.form.cleaned_data['location'] +
#                  '&experience=' + str(self.form.cleaned_data['experience'] or "") + '&salary=' + str(self.form.cleaned_data['salary'] or "") +
#                  '&industry=' + str(self.form.cleaned_data['industry'] or "") + '&functional_area=' + str(self.form.cleaned_data['functional_area'] or ""))

#         context = {
#             'query': self.query,
#             'query_form': self.form,
#             'page': page,
#             'results': results,
#             'suggestion': None,
#             'param': param,
#             'aft_page': aft_page,
#             'after_page': after_page,
#             'prev_page': prev_page,
#             'previous_page': previous_page,
#             'current_page': page,
#             'last_page': no_pages,
#             'no_of_jobs': no_of_jobs,
#             'skill': self.form.cleaned_data['q'],
#             'location': self.form.cleaned_data['location'],
#         }
#         return render_to_response(self.template, context, context_instance=self.context_class(self.request))


def custom_search(data, request):
    form = job_searchForm(data)
    searched_locations = (
        searched_skills
    ) = searched_edu = searched_industry = searched_states = ""
    if request.POST.get("refine_search") == "True":
        (
            jobs_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(request.POST)
    else:
        jobs_list = form.search()
        jobs_list = JobPost.objects.filter(pk__in=[r.pk for r in jobs_list])
        searched_locations = City.objects.filter(name__in=data.get("location"))
        searched_skills = Skill.objects.filter(name__in=data.get("q"))
    jobs_list = jobs_list.filter(status="Live")
    job_type = (
        data.get("job_type")
        or request.POST.get("job_type")
        or request.GET.get("job_type")
    )
    if job_type:
        jobs_list = jobs_list.filter(job_type=job_type)
    if data.get("walk-in"):
        jobs_list = jobs_list.filter(job_type="walk-in")

    no_of_jobs = len(jobs_list)
    items_per_page = 20
    no_pages = int(math.ceil(float(jobs_list.count()) / items_per_page))
    page = request.POST.get("page") or data.get("page")
    if page and bool(re.search(r"[0-9]", page)) and int(page) > 0:
        if int(page) > (no_pages + 2):
            page = 1
        else:
            page = int(data.get("page"))
    else:
        page = 1
    jobs_list = (
        jobs_list.select_related("company", "user")
        .prefetch_related("location", "skills", "industry")
        .distinct()
    )

    jobs_list = jobs_list[(page - 1) * items_per_page : page * items_per_page]

    prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
        page, no_pages
    )

    if form.is_valid():
        context = {
            "results": form.search(),
            "query": form.query(),
            "searchform": form,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "no_of_jobs": no_of_jobs,
            "job_list": jobs_list,
            "skill": form.cleaned_data["q"],
            "location": form.cleaned_data["location"],
            "searched_skills": searched_skills,
            "searched_locations": searched_locations,
            "searched_industry": searched_industry,
            "searched_edu": searched_edu,
            "searched_experience": request.POST.get("experience"),
            "searched_job_type": request.POST.get("job_type"),
            "searched_functional_area": request.POST.get("functional_area"),
        }
        return context
    return {"job_list": []}


def custome_search(request, skill_name, city_name, **kwargs):
    current_url = reverse(
        "custome_search", kwargs={"skill_name": skill_name, "city_name": city_name}
    )
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(current_url, permanent=True)
    if "page" in request.GET:
        url = current_url + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    final_skill = get_valid_skills_list(skill_name)
    final_location = get_valid_locations_list(city_name)
    if request.POST:
        save_search_results.delay(
            request.META["REMOTE_ADDR"], request.POST, 0, request.user.id
        )
    if not final_location or not final_skill:
        template = "404.html"
        return render(
            request,
            template,
            {
                "message": "Unfortunately, we are unable to locate the jobs you are looking for",
                "data_empty": True,
                "job_search": True,
                "reason": "Only Valid Skills/Cities names are accepted in search",
                "searched_skills": final_skill or [skill_name],
                "searched_locations": final_location or [city_name],
            },
            status=404,
        )
    job_type = request.POST.get("job_type") or request.GET.get("job_type")
    if request.POST.get("refine_search") == "True":
        (
            job_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(request.POST)
    else:
        search_dict = QueryDict("", mutable=True)
        search_dict.setlist("refine_skill", final_skill)
        search_dict.setlist("refine_location", final_location)
        if job_type:
            search_dict.update({"job_type": job_type})
        if request.POST.get("experience"):
            search_dict.update(
                {"refine_experience_min": request.POST.get("experience")}
            )
        (
            job_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(search_dict)
    if job_list:
        no_of_jobs = job_list.count()
        items_per_page = 20
        no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
        page = get_page_number(request, kwargs, no_pages)
        if not page:
            return HttpResponseRedirect(current_url)
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        job_list = job_list[(page - 1) * items_per_page : page * items_per_page]
        meta_title, meta_description, h1_tag = get_meta_data(
            "skill_location_jobs",
            {
                "skills": searched_skills,
                "final_skill": final_skill,
                "page": page,
                "locations": searched_locations,
                "final_location": final_location,
            },
        )
        data = {
            "job_list": job_list,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "no_of_jobs": no_of_jobs,
            "is_job_list": False,
            "current_url": current_url,
            "searched_skills": searched_skills,
            "searched_states": searched_states,
            "searched_locations": searched_locations,
            "searched_industry": searched_industry,
            "searched_edu": searched_edu,
            "searched_experience": request.POST.get("experience"),
            "searched_job_type": job_type,
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
        }
        template = "jobs/jobs_list.html"
        return render(request, template, data)
    else:
        template = "404.html"
        meta_title, meta_description = get_404_meta(
            "skill_location_404", {"skill": final_skill, "city": final_location}
        )
        return render(
            request,
            template,
            {
                "message": "Unfortunately, we are unable to locate the jobs you are looking for",
                "reason": "Only Valid Skills/Cities names are accepted in search",
                "job_search": True,
                "searched_skills": searched_skills,
                "searched_locations": searched_locations,
                "meta_title": meta_title,
                "meta_description": meta_description,
            },
        )


def custom_walkins(request, skill_name, city_name, **kwargs):
    current_url = reverse(
        "custom_walkins", kwargs={"skill_name": skill_name, "city_name": city_name}
    )
    if kwargs.get("page_num") == "1" or request.GET.get("page") == "1":
        return redirect(current_url, permanent=True)
    if "page" in request.GET:
        url = current_url + request.GET.get("page") + "/"
        return redirect(url, permanent=True)
    final_skill = get_valid_skills_list(skill_name)
    final_location = get_valid_locations_list(city_name)
    if not final_location or not final_skill:
        if request.POST:
            save_search_results.delay(
                request.META["REMOTE_ADDR"], request.POST, 0, request.user.id
            )
        location = final_location or [city_name]
        skills = final_skill or [skill_name]
        template = "404.html"
        meta_title = meta_description = ""
        return render(
            request,
            template,
            {
                "message": "Unfortunately, we are unable to locate the jobs you are looking for",
                "searched_job_type": "walk-in",
                "reason": "Only Valid Skills/Cities names are accepted in search",
                "searched_skills": skills,
                "searched_locations": location,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "data_empty": True,
                "job_search": True,
            },
            status=404,
        )
    if request.POST.get("refine_search") == "True":
        (
            job_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(request.POST)
    else:
        search_dict = QueryDict("", mutable=True)
        search_dict.setlist("refine_skill", final_skill)
        search_dict.setlist("refine_location", final_location)
        search_dict.update({"job_type": "walk-in"})
        if request.POST.get("experience"):
            search_dict.update(
                {"refine_experience_min": request.POST.get("experience")}
            )
        (
            job_list,
            searched_skills,
            searched_locations,
            searched_industry,
            searched_edu,
            searched_states,
        ) = refined_search(search_dict)
    if job_list:
        no_of_jobs = job_list.count()
        items_per_page = 20
        no_pages = int(math.ceil(float(no_of_jobs) / items_per_page))
        page = get_page_number(request, kwargs, no_pages)
        if not page:
            return HttpResponseRedirect(current_url)
        prev_page, previous_page, aft_page, after_page = get_prev_after_pages_count(
            page, no_pages
        )
        job_list = job_list[(page - 1) * items_per_page : page * items_per_page]
        meta_title, meta_description, h1_tag = get_meta_data(
            "skill_location_walkin_jobs",
            {
                "skills": searched_skills,
                "final_skill": final_skill,
                "page": page,
                "locations": searched_locations,
                "final_location": final_location,
            },
        )
        data = {
            "job_list": job_list,
            "aft_page": aft_page,
            "after_page": after_page,
            "prev_page": prev_page,
            "previous_page": previous_page,
            "current_page": page,
            "last_page": no_pages,
            "no_of_jobs": no_of_jobs,
            "is_job_list": False,
            "current_url": current_url,
            "searched_skills": searched_skills,
            "searched_states": searched_states,
            "searched_locations": searched_locations,
            "searched_industry": searched_industry,
            "searched_edu": searched_edu,
            "searched_experience": request.POST.get("experience"),
            "searched_job_type": "walk-in",
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_tag": h1_tag,
            "walkin": True,
        }
        template = "jobs/jobs_list.html"
        return render(request, template, data)
    else:
        template = "404.html"
        meta_title, meta_description = get_404_meta(
            "skill_location_404", {"skill": final_skill, "city": final_location}
        )
        return render(
            request,
            template,
            {
                "message": "Unfortunately, we are unable to locate the jobs you are looking for",
                "reason": "Only Valid Skills/Cities names are accepted in search",
                "job_search": True,
                "searched_skills": searched_skills,
                "searched_locations": searched_locations,
                "meta_title": meta_title,
                "meta_description": meta_description,
            },
        )


def skill_auto_search(request):
    text = request.GET.get("text", "").split(", ")[:-1]
    search = request.GET.get("q", "")
    sqs = (
        SearchQuerySet()
        .models(Skill)
        .filter_and(SQ(skill_name__contains=search) | SQ(skill_slug__contains=search))
    )
    if text:
        sqs = sqs.exclude(skill_name__in=text)
    suggestions = [
        {
            "name": result.skill_name,
            "slug": result.skill_slug,
            "jobs_count": result.no_of_jobposts,
            "id": result.pk,
        }
        for result in sqs
    ]
    suggestions = sorted(suggestions, key=lambda k: len(k["name"]), reverse=False)
    if not request.GET.get("search") == "filter":
        deg = (
            SearchQuerySet()
            .models(Qualification)
            .filter_and(SQ(edu_name__contains=search) | SQ(edu_slug__contains=search))
        )
        if text:
            deg = deg.exclude(edu_name__in=text)
        degrees = [
            {"name": result.edu_name, "id": result.pk, "slug": result.edu_slug}
            for result in deg
        ]
        suggestions = suggestions + degrees
    # suggestions = sorted(suggestions, key=int(itemgetter('jobs_count'), reverse=True)
    the_data = json.dumps({"results": suggestions[:10]})
    return HttpResponse(the_data, content_type="application/json")


def city_auto_search(request):
    text = request.GET.get("text", "").split(", ")[:-1]
    search = request.GET.get("location", "")
    sqs = SearchQuerySet().models(City).filter(city_name__contains=search)
    if text:
        sqs = sqs.exclude(city_name__in=text)
    suggestions = [
        {"name": result.city_name, "jobs_count": result.no_of_jobposts, "id": result.pk}
        for result in sqs
    ]
    suggestions = sorted(suggestions, key=lambda k: len(k["name"]), reverse=False)
    if not request.GET.get("search") == "filter":
        state = (
            SearchQuerySet()
            .models(State)
            .filter_and(
                SQ(state_name__contains=search) | SQ(state_slug__contains=search)
            )
        )
        state = state.exclude(is_duplicate__in=[True])
        if text:
            state = state.exclude(state_name__in=text)
        states = [
            {"name": result.state_name, "id": result.pk, "slug": result.state_slug}
            for result in state
        ]
        suggestions = suggestions + states
    the_data = json.dumps({"results": suggestions[:10]})
    return HttpResponse(the_data, content_type="application/json")


def industry_auto_search(request):
    sqs = (
        SearchQuerySet()
        .models(Industry)
        .filter(industry_name__icontains=request.GET.get("industry", ""))
    )
    suggestions = [
        {
            "name": result.industry_name.split("/")[0],
            "jobs_count": result.no_of_jobposts,
            "id": result.pk,
            "slug": result.industry_slug,
        }
        for result in sqs
    ]
    # suggestions = sorted(suggestions, key=lambda k: int(k['jobs_count']), reverse=True)
    the_data = json.dumps({"results": suggestions[:10]})
    return HttpResponse(the_data, content_type="application/json")


def functional_area_auto_search(request):
    sqs = (
        SearchQuerySet()
        .models(FunctionalArea)
        .filter(functionalarea_name__contains=request.GET.get("functional_area", ""))[
            :10
        ]
    )
    suggestions = [
        {"name": result.functionalarea_name, "jobs_count": result.no_of_jobposts}
        for result in sqs
    ]
    suggestions = sorted(suggestions, key=lambda k: int(k["jobs_count"]), reverse=True)
    the_data = json.dumps({"results": suggestions})
    return HttpResponse(the_data, content_type="application/json")


def education_auto_search(request):
    degrees = (
        SearchQuerySet()
        .models(Qualification)
        .filter_and(
            SQ(edu_name__contains=request.GET.get("education", ""))
            | SQ(edu_slug__contains=request.GET.get("education", ""))
        )
    )
    suggestions = [
        {
            "name": result.edu_name,
            "id": result.pk,
            "slug": result.edu_slug,
            "jobs_count": result.no_of_jobposts or 0,
        }
        for result in degrees
    ]
    suggestions = sorted(suggestions, key=lambda k: int(k["jobs_count"]), reverse=True)
    the_data = json.dumps({"results": suggestions[:10]})
    return HttpResponse(the_data, content_type="application/json")


def state_auto_search(request):
    text = request.GET.get("text", "").split(", ")[:-1]
    states = (
        SearchQuerySet()
        .models(State)
        .filter_and(
            SQ(state_name__contains=request.GET.get("state", ""))
            | SQ(state_slug__contains=request.GET.get("state", ""))
        )
    )
    if text:
        states = states.exclude(state_name__in=text)
    suggestions = [
        {
            "name": result.state_name,
            "id": result.pk,
            "slug": result.state_slug,
            "jobs_count": result.no_of_jobposts or 0,
        }
        for result in states
    ]
    suggestions = sorted(suggestions, key=lambda k: int(k["jobs_count"]), reverse=True)
    the_data = json.dumps({"results": suggestions[:10]})
    return HttpResponse(the_data, content_type="application/json")


def search_slugs(request):
    searched = request.GET.get("q_slug", "").replace("jobs", "").replace("job", "")
    search_list = [i.strip() for i in searched.split(",") if i.strip()]
    slug = ""
    for search in search_list:
        skills = Skill.objects.filter(Q(slug__iexact=search) | Q(name__iexact=search))
        degrees = Qualification.objects.filter(
            Q(slug__iexact=search) | Q(name__iexact=search)
        )
        for skill in skills:
            slug += ("-" + skill.slug) if slug else skill.slug
        for degree in degrees:
            slug += ("-" + degree.slug) if slug else degree.slug
        if not skills and not degrees:
            slug += ("-" + slugify(search)) if slug else slugify(search)
    location = request.GET.get("location", "")
    location_slug = ""
    if location:
        search_list = [i.strip() for i in location.split(",") if i.strip()]
        for search in search_list:
            locations = City.objects.filter(
                Q(Q(slug__iexact=search) | Q(name__iexact=search))
                & ~Q(state__name=F("name"))
            )
            states = State.objects.filter(
                Q(slug__iexact=search) | Q(name__iexact=search)
            )
            for loc in locations:
                location_slug += ("-" + loc.slug) if location_slug else loc.slug
            for state in states:
                location_slug += ("-" + state.slug) if location_slug else state.slug
        if not location_slug:
            location_slug = slugify(location)
    the_data = json.dumps({"skill_slug": slug, "location_slug": location_slug})
    return HttpResponse(the_data, content_type="application/json")
