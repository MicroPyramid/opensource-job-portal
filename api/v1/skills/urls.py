from django.urls import path
from .views import (
    SkillListView,
    UserTechnicalSkillListView,
    UserTechnicalSkillCreateView,
    UserTechnicalSkillDetailView
)

app_name = 'skills'

urlpatterns = [
    # Master skill list (public)
    path('', SkillListView.as_view(), name='skill-list'),

    # User's technical skills (authenticated)
    path('my-skills/', UserTechnicalSkillListView.as_view(), name='my-skills'),
    path('my-skills/add/', UserTechnicalSkillCreateView.as_view(), name='add-skill'),
    path('my-skills/<int:skill_id>/', UserTechnicalSkillDetailView.as_view(), name='skill-detail'),
]
