"""
Language Views for Job Seekers

Replaces `candidate.views.add_language` / `edit_language` / `delete_language`
and their three `-modal` twins.

`User.language` is a ManyToMany to `UserLanguage`, and a `UserLanguage` row is
owned by exactly one user — unlike `Project`, which uses the same M2M shape but
is treated as shareable. So `destroy` deletes the row rather than only
detaching it; leaving it behind would orphan a record nothing can ever reach
again.
"""

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from peeldb.models import Language, UserLanguage

from .serializers import LanguageSerializer, UserLanguageSerializer


class LanguageOptionsViewSet(viewsets.ReadOnlyModelViewSet):
    """The language catalogue a job seeker picks from."""

    permission_classes = [IsAuthenticated]
    serializer_class = LanguageSerializer
    queryset = Language.objects.all().order_by("name")
    pagination_class = None


class UserLanguageViewSet(viewsets.ModelViewSet):
    """
    Languages the authenticated job seeker speaks, with proficiency.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserLanguageSerializer
    # Schema-introspection only; get_queryset() below is what serves requests.
    queryset = UserLanguage.objects.none()
    pagination_class = None

    def get_queryset(self):
        return (
            self.request.user.language.all()
            .select_related("language")
            .order_by("language__name")
        )

    def _reject_non_seeker(self, request):
        if request.user.user_type != "JS":
            return Response(
                {"error": "Only job seekers can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    @extend_schema(
        summary="List languages",
        responses={
            200: OpenApiResponse(response=UserLanguageSerializer(many=True)),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Only job seekers can access"),
        },
        tags=["Languages"],
    )
    def list(self, request):
        denied = self._reject_non_seeker(request)
        if denied:
            return denied

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Add a language",
        request=UserLanguageSerializer,
        responses={
            201: OpenApiResponse(response=UserLanguageSerializer),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Only job seekers can access"),
        },
        tags=["Languages"],
    )
    def create(self, request):
        denied = self._reject_non_seeker(request)
        if denied:
            return denied

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # One row per language per user. Without this the legacy UI's
        # double-submit produces duplicates that the list then renders twice.
        language = serializer.validated_data["language"]
        if self.get_queryset().filter(language=language).exists():
            return Response(
                {"language": ["You have already added that language."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_language = serializer.save()
        request.user.language.add(user_language)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Delete a language",
        responses={
            204: OpenApiResponse(description="Deleted"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Only job seekers can access"),
            404: OpenApiResponse(description="Not one of your languages"),
        },
        tags=["Languages"],
    )
    def destroy(self, request, pk=None):
        denied = self._reject_non_seeker(request)
        if denied:
            return denied

        # get_queryset() is already scoped to the requesting user, so this
        # 404s rather than letting one user delete another's row.
        user_language = self.get_queryset().filter(pk=pk).first()
        if not user_language:
            return Response(status=status.HTTP_404_NOT_FOUND)

        request.user.language.remove(user_language)
        user_language.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
