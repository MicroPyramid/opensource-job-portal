"""
Profile API URL routing
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .education_lookup_views import (
    DegreeViewSet,
    EducationInstituteViewSet,
    QualificationViewSet,
)
from .education_views import EducationViewSet
from .language_views import LanguageOptionsViewSet, UserLanguageViewSet
from .portfolio_views import CertificationViewSet, ProjectViewSet

# Import from split view modules
from .profile_views import ProfileUploadView, ProfileView, ResumeDeleteView

app_name = "profile"

# Create router for viewsets
router = DefaultRouter()
router.register(r"education", EducationViewSet, basename="education")
router.register(
    r"education-lookups/qualifications", QualificationViewSet, basename="qualification"
)
router.register(r"education-lookups/degrees", DegreeViewSet, basename="degree")
router.register(
    r"education-lookups/institutes", EducationInstituteViewSet, basename="institute"
)
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"certifications", CertificationViewSet, basename="certification")
router.register(r"languages", UserLanguageViewSet, basename="language")
router.register(r"language-options", LanguageOptionsViewSet, basename="language-option")

urlpatterns = [
    path("", ProfileView.as_view(), name="profile"),
    path("upload/", ProfileUploadView.as_view(), name="profile-upload"),
    path("resume/delete/", ResumeDeleteView.as_view(), name="resume-delete"),
    # Include router URLs
    path("", include(router.urls)),
]
