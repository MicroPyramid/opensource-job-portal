"""
Contact API URL routing
"""
from django.urls import path
from . import views

app_name = "contact"

urlpatterns = [
    path("submit/", views.submit_contact_form, name="submit"),
]
