from django import template
from search.forms import job_searchForm
from peeldb.models import JOB_TYPE
from peeldb.models import WALKIN_TYPE

register = template.Library()


@register.inclusion_tag("search/search_filter.html", takes_context=True)
def show_search_filter(context):
    search_form = job_searchForm()
    return {
        "request": context["request"],
        "search_form": search_form,
        "job_types": JOB_TYPE,
        "searched_skills": context.get("searched_skills"),
        "searched_edu": context.get("searched_edu"),
        "searched_locations": context.get("searched_locations"),
        "searched_states": context.get("searched_states"),
        "searched_experience": context.get("searched_experience"),
        "searched_job_type": context.get("searched_job_type"),
        "searched_text": context.get("searched_text"),
    }


@register.inclusion_tag("search/adv_search_filter.html", takes_context=True)
def show_adv_search_filter(context):
    search_form = job_searchForm()

    return {
        "request": context["request"],
        "search_form": search_form,
        "job_types": JOB_TYPE,
        "walkin_types": WALKIN_TYPE,
    }


@register.inclusion_tag("mobile/search/search_filter.html", takes_context=True)
def show_mobile_search_filter(context):
    search_form = job_searchForm()
    return {
        "request": context["request"],
        "search_form": search_form,
        "job_types": JOB_TYPE,
        "searched_skills": context.get("searched_skills"),
        "searched_locations": context.get("searched_locations"),
        "searched_job_type": context.get("searched_job_type"),
        "searched_edu": context.get("searched_edu"),
        "searched_industry": context.get("searched_industry"),
        "searched_experience": context.get("searched_experience"),
        "searched_states": context.get("searched_states"),
        "searched_functional_area": context.get("searched_functional_area"),
        # 'search_slug': context.get('search_slug')
    }
