"""
Portfolio Views for Job Seekers - Projects and Certifications Management
"""
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from peeldb.models import Project, Certification
from .serializers import ProjectSerializer, CertificationSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    Project Portfolio CRUD for Job Seekers

    Allows job seekers to manage their project portfolio:
    - List all projects
    - Create new project
    - Update existing project
    - Delete project
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """Get projects for authenticated user only"""
        return self.request.user.project.all().prefetch_related('skills').select_related('location').order_by('-from_date')

    @extend_schema(
        summary="List projects",
        description="Get all projects for the authenticated job seeker, sorted by most recent first",
        responses={
            200: OpenApiResponse(
                response=ProjectSerializer(many=True),
                description="List of projects"
            ),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Only job seekers can access")
        },
        tags=["Projects"]
    )
    def list(self, request):
        """List all projects for user"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create project",
        description="Add a new project to the job seeker's portfolio",
        request=ProjectSerializer,
        responses={
            201: OpenApiResponse(
                response=ProjectSerializer,
                description="Project created successfully"
            ),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Only job seekers can access")
        },
        tags=["Projects"],
        examples=[
            OpenApiExample(
                name="Add project example",
                value={
                    "name": "E-commerce Platform",
                    "from_date": "2023-01-01",
                    "to_date": "2023-06-30",
                    "skill_ids": [1, 2, 3],
                    "description": "Developed a full-stack e-commerce platform using React and Django",
                    "location_id": 1,
                    "role": "Full Stack Developer",
                    "size": 4
                },
                request_only=True
            )
        ]
    )
    def create(self, request):
        """Create new project"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            # Add to user's projects
            request.user.project.add(project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Retrieve project",
        description="Get details of a specific project",
        responses={
            200: OpenApiResponse(
                response=ProjectSerializer,
                description="Project details"
            ),
            403: OpenApiResponse(description="Not authorized to access this project"),
            404: OpenApiResponse(description="Project not found")
        },
        tags=["Projects"]
    )
    def retrieve(self, request, pk=None):
        """Get specific project"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            project = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(project)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Update project",
        description="Update an existing project (full update)",
        request=ProjectSerializer,
        responses={
            200: OpenApiResponse(
                response=ProjectSerializer,
                description="Project updated successfully"
            ),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Not authorized"),
            404: OpenApiResponse(description="Project not found")
        },
        tags=["Projects"]
    )
    def update(self, request, pk=None):
        """Full update of project"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            project = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(project, data=request.data, partial=False)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Partial update project",
        description="Partially update an existing project",
        request=ProjectSerializer,
        responses={
            200: OpenApiResponse(
                response=ProjectSerializer,
                description="Project updated successfully"
            ),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Not authorized"),
            404: OpenApiResponse(description="Project not found")
        },
        tags=["Projects"]
    )
    def partial_update(self, request, pk=None):
        """Partial update of project"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            project = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Delete project",
        description="Remove a project from the job seeker's portfolio",
        responses={
            204: OpenApiResponse(description="Project deleted successfully"),
            403: OpenApiResponse(description="Not authorized"),
            404: OpenApiResponse(description="Project not found")
        },
        tags=["Projects"]
    )
    def destroy(self, request, pk=None):
        """Delete project"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            project = self.get_queryset().get(pk=pk)
            # Remove from user's projects
            request.user.project.remove(project)
            # Delete the project
            project.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CertificationViewSet(viewsets.ModelViewSet):
    """
    Certifications CRUD for Job Seekers

    Allows job seekers to manage their professional certifications:
    - List all certifications
    - Create new certification
    - Update existing certification
    - Delete certification
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CertificationSerializer

    def get_queryset(self):
        """Get certifications for authenticated user only"""
        return self.request.user.user_certifications.all().order_by('-issued_date', '-created_at')

    @extend_schema(
        summary="List certifications",
        description="Get all certifications for the authenticated job seeker, sorted by most recent first",
        responses={
            200: OpenApiResponse(
                response=CertificationSerializer(many=True),
                description="List of certifications"
            ),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Only job seekers can access")
        },
        tags=["Certifications"]
    )
    def list(self, request):
        """List all certifications for user"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create certification",
        description="Add a new professional certification to the job seeker's profile",
        request=CertificationSerializer,
        responses={
            201: OpenApiResponse(
                response=CertificationSerializer,
                description="Certification created successfully"
            ),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Only job seekers can access")
        },
        tags=["Certifications"],
        examples=[
            OpenApiExample(
                name="Add certification example",
                value={
                    "name": "AWS Certified Solutions Architect",
                    "organization": "Amazon Web Services",
                    "credential_id": "AWS-CSA-12345",
                    "credential_url": "https://aws.amazon.com/verification",
                    "issued_date": "2023-06-15",
                    "expiry_date": "2026-06-15",
                    "does_not_expire": False,
                    "description": "Professional certification for AWS cloud architecture"
                },
                request_only=True
            )
        ]
    )
    def create(self, request):
        """Create new certification"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Automatically set user to current user
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Retrieve certification",
        description="Get details of a specific certification",
        responses={
            200: OpenApiResponse(
                response=CertificationSerializer,
                description="Certification details"
            ),
            403: OpenApiResponse(description="Not authorized to access this certification"),
            404: OpenApiResponse(description="Certification not found")
        },
        tags=["Certifications"]
    )
    def retrieve(self, request, pk=None):
        """Get specific certification"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            certification = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(certification)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Certification.DoesNotExist:
            return Response(
                {'error': 'Certification not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Update certification",
        description="Update an existing certification (full update)",
        request=CertificationSerializer,
        responses={
            200: OpenApiResponse(
                response=CertificationSerializer,
                description="Certification updated successfully"
            ),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Not authorized"),
            404: OpenApiResponse(description="Certification not found")
        },
        tags=["Certifications"]
    )
    def update(self, request, pk=None):
        """Full update of certification"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            certification = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(certification, data=request.data, partial=False)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Certification.DoesNotExist:
            return Response(
                {'error': 'Certification not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Partial update certification",
        description="Partially update an existing certification",
        request=CertificationSerializer,
        responses={
            200: OpenApiResponse(
                response=CertificationSerializer,
                description="Certification updated successfully"
            ),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Not authorized"),
            404: OpenApiResponse(description="Certification not found")
        },
        tags=["Certifications"]
    )
    def partial_update(self, request, pk=None):
        """Partial update of certification"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            certification = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(certification, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Certification.DoesNotExist:
            return Response(
                {'error': 'Certification not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Delete certification",
        description="Remove a certification from the job seeker's profile",
        responses={
            204: OpenApiResponse(description="Certification deleted successfully"),
            403: OpenApiResponse(description="Not authorized"),
            404: OpenApiResponse(description="Certification not found")
        },
        tags=["Certifications"]
    )
    def destroy(self, request, pk=None):
        """Delete certification"""
        if request.user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            certification = self.get_queryset().get(pk=pk)
            certification.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Certification.DoesNotExist:
            return Response(
                {'error': 'Certification not found'},
                status=status.HTTP_404_NOT_FOUND
            )
