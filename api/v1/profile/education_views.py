"""
Education Views for Job Seekers - Education Management
"""
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from peeldb.models import EducationDetails
from .serializers import EducationDetailsSerializer


class EducationViewSet(viewsets.ModelViewSet):
    """
    Education Details CRUD for Job Seekers

    Allows job seekers to manage their educational qualifications:
    - List all education entries
    - Create new education entry
    - Update existing education
    - Delete education entry
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EducationDetailsSerializer

    def get_queryset(self):
        """Get education details for authenticated user only"""
        return self.request.user.education.all().order_by('-from_date')

    @extend_schema(
        summary="List education details",
        description="Get all education entries for the authenticated job seeker, sorted by most recent first",
        responses={
            200: OpenApiResponse(
                response=EducationDetailsSerializer(many=True),
                description="List of education details"
            ),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Only job seekers can access")
        },
        tags=["Education"]
    )
    def list(self, request):
        """List all education entries for user"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create education entry",
        description="Add a new education qualification to the job seeker's profile",
        request=EducationDetailsSerializer,
        responses={
            201: OpenApiResponse(
                response=EducationDetailsSerializer,
                description="Education entry created successfully"
            ),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Only job seekers can access")
        },
        tags=["Education"],
        examples=[
            OpenApiExample(
                name="Add education example",
                value={
                    "institute_id": 1,
                    "degree_id": 1,
                    "from_date": "2015-08-01",
                    "to_date": "2019-05-31",
                    "score": "8.5 GPA",
                    "current_education": False
                },
                request_only=True
            )
        ]
    )
    def create(self, request):
        """Create new education entry"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            education = serializer.save()
            # Add to user's education
            request.user.education.add(education)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Retrieve education entry",
        description="Get details of a specific education entry",
        responses={
            200: OpenApiResponse(
                response=EducationDetailsSerializer,
                description="Education entry details"
            ),
            403: OpenApiResponse(description="Not authorized to access this education entry"),
            404: OpenApiResponse(description="Education entry not found")
        },
        tags=["Education"]
    )
    def retrieve(self, request, pk=None):
        """Get specific education entry"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            education = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(education)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except EducationDetails.DoesNotExist:
            return Response(
                {'error': 'Education entry not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Update education entry",
        description="Update an existing education entry (full update)",
        request=EducationDetailsSerializer,
        responses={
            200: OpenApiResponse(
                response=EducationDetailsSerializer,
                description="Education entry updated successfully"
            ),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Not authorized"),
            404: OpenApiResponse(description="Education entry not found")
        },
        tags=["Education"]
    )
    def update(self, request, pk=None):
        """Full update of education entry"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            education = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(education, data=request.data, partial=False)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except EducationDetails.DoesNotExist:
            return Response(
                {'error': 'Education entry not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Partial update education entry",
        description="Partially update an existing education entry",
        request=EducationDetailsSerializer,
        responses={
            200: OpenApiResponse(
                response=EducationDetailsSerializer,
                description="Education entry updated successfully"
            ),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Not authorized"),
            404: OpenApiResponse(description="Education entry not found")
        },
        tags=["Education"]
    )
    def partial_update(self, request, pk=None):
        """Partial update of education entry"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            education = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(education, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except EducationDetails.DoesNotExist:
            return Response(
                {'error': 'Education entry not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Delete education entry",
        description="Remove an education entry from the job seeker's profile",
        responses={
            204: OpenApiResponse(description="Education entry deleted successfully"),
            403: OpenApiResponse(description="Not authorized"),
            404: OpenApiResponse(description="Education entry not found")
        },
        tags=["Education"]
    )
    def destroy(self, request, pk=None):
        """Delete education entry"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            education = self.get_queryset().get(pk=pk)
            # Remove from user's education
            request.user.education.remove(education)
            # Delete the education entry
            education.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except EducationDetails.DoesNotExist:
            return Response(
                {'error': 'Education entry not found'},
                status=status.HTTP_404_NOT_FOUND
            )
