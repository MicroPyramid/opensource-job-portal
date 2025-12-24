"""
URL Configuration for Companies API v1
"""
from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('', views.CompanyListView.as_view(), name='company-list'),
    path('filter-options/', views.company_filter_options, name='filter-options'),
    path('<slug:slug>/', views.CompanyDetailView.as_view(), name='company-detail'),
]
