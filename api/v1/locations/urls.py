from django.urls import path
from .views import (
    CountryListView,
    StateListView,
    CityListView,
    CityDetailView
)

app_name = 'locations'

urlpatterns = [
    path('countries/', CountryListView.as_view(), name='countries'),
    path('states/', StateListView.as_view(), name='states'),
    path('cities/', CityListView.as_view(), name='cities'),
    path('cities/<int:city_id>/', CityDetailView.as_view(), name='city-detail'),
]
