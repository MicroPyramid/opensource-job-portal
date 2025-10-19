from django.urls import path
from .views import (
    UserEmploymentHistoryListView,
    UserEmploymentHistoryCreateView,
    UserEmploymentHistoryDetailView
)

app_name = 'employment'

urlpatterns = [
    # User's employment history (authenticated)
    path('my-history/', UserEmploymentHistoryListView.as_view(), name='my-history'),
    path('my-history/add/', UserEmploymentHistoryCreateView.as_view(), name='add-employment'),
    path('my-history/<int:employment_id>/', UserEmploymentHistoryDetailView.as_view(), name='employment-detail'),
]
