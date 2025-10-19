"""
Main API URL routing
Versioned API structure for future compatibility
"""
from django.urls import path, include

app_name = "api"

urlpatterns = [
    path("v1/", include("api.v1.urls")),
    # Future versions:
    # path('v2/', include('api.v2.urls')),
]
