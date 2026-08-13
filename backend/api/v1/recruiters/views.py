"""
Recruiter directory for API v1

Replaces `pjob.views.recruiters` and `pjob.views.recruiter_profile`.

Public and crawler-facing — `recruiters` is one of the entries in
`psite.sitemaps.StaticPagesSitemap`. 5,351 recruiters currently have a live
job, which is a larger surface than the company pages.
"""

from django.db.models import Count, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from peeldb.models import User

from .serializers import RecruiterDetailSerializer, RecruiterListSerializer

# The legacy directory listed user_type in (RR, AR, AA) — company recruiter,
# agency recruiter, agency admin. Those were consolidated into a single "EM"
# (Employer) type (peeldb.models.USER_TYPE, "Simplified from RR, RA, AA, AR"),
# and every one of the 5,345 accounts with a live job now carries it. Matching
# on the old codes returns an empty directory.
RECRUITER_TYPES = ("EM",)


def visible_recruiters():
    """
    Recruiters the directory is allowed to show.

    Restricted to accounts with at least one *live* job. The legacy view listed
    every active recruiter and ordered by post count, which put thousands of
    zero-job profiles into the crawlable set — pages with no content on them.
    """
    return (
        User.objects.filter(user_type__in=RECRUITER_TYPES, is_active=True)
        .annotate(
            job_count=Count(
                "jobposts", filter=Q(jobposts__status="Live"), distinct=True
            )
        )
        .filter(job_count__gt=0)
        .select_related("company")
    )


class RecruiterPagination(PageNumberPagination):
    """Matches the legacy directory's 45 per page."""

    page_size = 45
    page_size_query_param = "page_size"
    max_page_size = 100


class RecruiterListView(generics.ListAPIView):
    """
    Public recruiter directory.

    `letter` reproduces the legacy A-Z filter, which was a POST
    (`alphabet_value`) against a full-page reload; here it is a query param so
    each letter is a crawlable URL.
    """

    serializer_class = RecruiterListSerializer
    pagination_class = RecruiterPagination

    @extend_schema(
        tags=["Recruiters"],
        summary="List recruiters",
        parameters=[
            OpenApiParameter(
                name="letter",
                description="Restrict to recruiters whose name starts with this letter",
                required=False,
                type=OpenApiTypes.STR,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = visible_recruiters()

        letter = (self.request.query_params.get("letter") or "").strip()
        if letter:
            # Match the displayed name, which falls back to `username` when the
            # account has no first name — otherwise a letter bucket can list a
            # recruiter whose visible name starts with something else.
            queryset = queryset.filter(
                Q(first_name__istartswith=letter)
                | Q(first_name="", username__istartswith=letter)
            )

        return queryset.order_by("-job_count", "username")


class RecruiterDetailView(generics.RetrieveAPIView):
    """
    One recruiter's public profile.

    Looked up by `username`, case-insensitively, because that is what the
    legacy `/recruiters/<recruiter_name>/` URLs used and what any existing
    inbound link will carry.
    """

    serializer_class = RecruiterDetailSerializer
    lookup_field = "username"

    def get_queryset(self):
        return visible_recruiters()

    def get_object(self):
        queryset = self.get_queryset()
        return generics.get_object_or_404(
            queryset, username__iexact=self.kwargs["username"]
        )

    @extend_schema(tags=["Recruiters"], summary="Recruiter profile")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
