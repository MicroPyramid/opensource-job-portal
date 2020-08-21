from peeldb.models import JobPost, City, Skill, Qualification, Industry, State, Country
from haystack.query import SQ, SearchQuerySet


valid_time_formats = ["%Y-%m-%d 00:00:00"]


def refined_search(data):
    searched_skills = (
        searched_locations
    ) = searched_industry = searched_edu = state = Skill.objects.none()
    sqs = SearchQuerySet().models(JobPost).filter_and(status="Live")
    if "refine_skill" in data and data.getlist("refine_skill"):
        term = data.getlist("refine_skill")
        sqs = sqs.filter_and(
            SQ(title__in=term)
            | SQ(skills__in=term)
            | SQ(description__in=term)
            | SQ(designation__in=term)
            | SQ(edu_qualification__in=term)
        )
        searched_skills = Skill.objects.filter(name__in=term)

    location = data.getlist("refine_location") if "refine_location" in data else []
    searched_locations = City.objects.filter(name__in=location)
    if "Across India" in location:
        india = Country.objects.filter(name="India")
        sqs = sqs.filter_and(
            SQ(location__in=india.values_list("state__state__name", flat=True))
        )
    elif location:
        other_cities = searched_locations.values_list("parent_city__name", flat=True)
        sqs = sqs.filter_and(SQ(location__in=location) | SQ(location__in=other_cities))

    if "refine_state" in data and data.getlist("refine_state"):
        state = State.objects.filter(name__in=data.getlist("refine_state"))
        sqs = sqs.filter_and(location__in=state.values_list("state__name", flat=True))

    if data.get("job_type"):
        if data["job_type"] == "Fresher":
            sqs = sqs.filter_and(min_year__lte=int(0))
        else:
            sqs = sqs.filter_and(job_type__in=[data["job_type"]])

    if "refine_industry" in data and data.getlist("refine_industry"):
        term = data.getlist("refine_industry")
        sqs = sqs.filter_and(industry__in=term)
        searched_industry = Industry.objects.filter(name__in=term)

    if "refine_education" in data and data.getlist("refine_education"):
        term = data.getlist("refine_education")
        sqs = sqs.filter_and(edu_qualification__in=term)
        searched_edu = Qualification.objects.filter(name__in=term)

    if "functional_area" in data and data.getlist("functional_area"):
        term = data.getlist("functional_area")
        sqs = sqs.filter_or(functional_area__in=term)

    if data.get("refine_experience_min") or data.get("refine_experience_min") == 0:
        sqs = sqs.filter_and(min_year__lte=int(data["refine_experience_min"]))

    if data.get("refine_experience_max") or data.get("refine_experience_max") == 0:
        sqs = sqs.filter_and(max_year__lte=int(data["refine_experience_max"]))

    # TODO: this line is taking 500ms, nikhila has to look into it.
    # job_list = JobPost.objects.filter(status='Live', pk__in=results).select_related(
    #     'company', 'user').prefetch_related('location', 'skills', 'industry')
    sqs = sqs.load_all().order_by("-published_on")
    return (
        sqs,
        searched_skills,
        searched_locations,
        searched_industry,
        searched_edu,
        state,
    )
