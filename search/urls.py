from django.conf.urls import url
from search.views import (
    skill_auto_search,
    city_auto_search,
    industry_auto_search,
    state_auto_search,
    functional_area_auto_search,
    custome_search,
    education_auto_search,
)

app_name = "search"

urlpatterns = [
    url(r"^skill-auto/$", skill_auto_search),
    url(r"^city-auto/$", city_auto_search),
    url(r"^industry-auto/$", industry_auto_search),
    url(r"^functional-area-auto/$", functional_area_auto_search),
    url(r"^education-auto/$", education_auto_search),
    url(r"^state-auto/$", state_auto_search),
    url(r"^(?P<slug>([-\w/0-9-])+)/$", custome_search),
]
