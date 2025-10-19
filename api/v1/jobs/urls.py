"""
Jobs API URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'jobs'

router = DefaultRouter()
router.register(r'', views.JobViewSet, basename='job')

urlpatterns = [
    path('filter-options/', views.JobFilterOptionsView.as_view(), name='filter-options'),
    path('', include(router.urls)),
]
