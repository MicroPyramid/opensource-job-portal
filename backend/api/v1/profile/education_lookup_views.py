"""
Education Lookup Views for Job Seekers - Read-only Education Reference Data
"""
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from peeldb.models import Qualification, Degree, EducationInstitue
from .serializers import (
    QualificationSerializer,
    DegreeSerializer,
    EducationInstituteSerializer
)


class QualificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for qualifications (degree types)
    Used for populating dropdowns in education forms
    """
    permission_classes = [IsAuthenticated]
    serializer_class = QualificationSerializer
    queryset = Qualification.objects.filter(status='Active').order_by('name')

    @extend_schema(
        summary="List qualifications",
        description="Get all active qualifications/degree types for education forms",
        responses={
            200: OpenApiResponse(
                response=QualificationSerializer(many=True),
                description="List of qualifications"
            )
        },
        tags=["Education Lookups"]
    )
    def list(self, request):
        """List all active qualifications"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DegreeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for degrees
    Supports filtering and searching
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DegreeSerializer
    queryset = Degree.objects.all()

    @extend_schema(
        summary="List degrees",
        description="Get all degrees with optional filtering by qualification and specialization",
        parameters=[
            OpenApiParameter(
                name='qualification_id',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Filter by qualification ID'
            ),
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Search by specialization'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=DegreeSerializer(many=True),
                description="List of degrees"
            )
        },
        tags=["Education Lookups"]
    )
    def list(self, request):
        """List degrees with optional filtering"""
        queryset = self.get_queryset()

        # Filter by qualification
        qualification_id = request.query_params.get('qualification_id')
        if qualification_id:
            queryset = queryset.filter(degree_name_id=qualification_id)

        # Search by specialization
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(specialization__icontains=search)

        queryset = queryset.select_related('degree_name').order_by('degree_name__name', 'specialization')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EducationInstituteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for education institutes
    Supports search functionality
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EducationInstituteSerializer
    queryset = EducationInstitue.objects.all()

    @extend_schema(
        summary="List/search education institutes",
        description="Get education institutes with optional search by name",
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Search institutes by name'
            ),
            OpenApiParameter(
                name='limit',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Limit number of results (default: 50)'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=EducationInstituteSerializer(many=True),
                description="List of education institutes"
            )
        },
        tags=["Education Lookups"]
    )
    def list(self, request):
        """List/search education institutes"""
        queryset = self.get_queryset()

        # Search by name
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        # Limit results
        limit = request.query_params.get('limit', 50)
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = 50

        queryset = queryset.select_related('city').order_by('name')[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
