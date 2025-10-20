"""
Profile Views for Job Seekers
"""
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter
from django.utils import timezone
from django.db import models as django_models
from django.db.models import Q, Sum

from peeldb.models import (
    User, EducationDetails, Degree, Qualification, EducationInstitue, Project, Certification
)
from .serializers import (
    ProfileSerializer, ProfileUpdateSerializer,
    EducationDetailsSerializer, DegreeSerializer,
    QualificationSerializer, EducationInstituteSerializer,
    ProjectSerializer, CertificationSerializer
)


class ProfileView(APIView):
    """
    Job Seeker Profile Management

    GET: Retrieve authenticated user's complete profile
    PUT: Update authenticated user's profile (full update)
    PATCH: Partially update authenticated user's profile
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @extend_schema(
        summary="Get user profile",
        description="Retrieve the authenticated job seeker's complete profile including personal info, skills, experience, education, projects, and certifications",
        responses={
            200: OpenApiResponse(
                response=ProfileSerializer,
                description="User profile retrieved successfully"
            ),
            401: OpenApiResponse(description="Authentication credentials were not provided")
        },
        tags=["Profile"]
    )
    def get(self, request):
        """Get authenticated user's profile"""
        user = request.user

        # Ensure only job seekers can access this endpoint
        if user.user_type != 'JS':
            return Response(
                {
                    'error': 'Only job seekers can access this endpoint',
                    'detail': f'Your user type is "{user.user_type}" ({user.get_user_type_display()}). Expected "JS" (Job Seeker).',
                    'user_email': user.email,
                    'current_user_type': user.user_type
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProfileSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update user profile (full)",
        description="Update the authenticated job seeker's profile. This is a full update - all fields should be provided.",
        request=ProfileSerializer,
        responses={
            200: OpenApiResponse(
                response=ProfileSerializer,
                description="Profile updated successfully"
            ),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication credentials were not provided"),
            403: OpenApiResponse(description="Only job seekers can access this endpoint")
        },
        tags=["Profile"],
        examples=[
            OpenApiExample(
                name="Update profile example",
                value={
                    "first_name": "John",
                    "last_name": "Doe",
                    "mobile": "+919876543210",
                    "gender": "M",
                    "dob": "1995-05-15",
                    "marital_status": "Single",
                    "job_role": "Full Stack Developer",
                    "profile_description": "Experienced full stack developer with 5 years of experience in Python and JavaScript",
                    "year": "5",
                    "month": "6",
                    "current_salary": "800000",
                    "expected_salary": "1200000",
                    "notice_period": "30 days",
                    "relocation": True,
                    "is_looking_for_job": True,
                    "is_open_to_offers": True,
                    "current_city_id": 1,
                    "preferred_city_ids": [1, 2, 3],
                    "email_notifications": True,
                    "show_email": False
                },
                request_only=True
            )
        ]
    )
    def put(self, request):
        """Full update of user profile"""
        user = request.user

        # Ensure only job seekers can access this endpoint
        if user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProfileSerializer(
            user,
            data=request.data,
            context={'request': request},
            partial=False  # Full update
        )

        if serializer.is_valid():
            serializer.save()
            # Update profile_updated timestamp
            user.profile_updated = timezone.now()
            user.save(update_fields=['profile_updated'])

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update user profile (partial)",
        description="Partially update the authenticated job seeker's profile. Only provided fields will be updated.",
        request=ProfileUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=ProfileSerializer,
                description="Profile updated successfully"
            ),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication credentials were not provided"),
            403: OpenApiResponse(description="Only job seekers can access this endpoint")
        },
        tags=["Profile"],
        examples=[
            OpenApiExample(
                name="Partial update example",
                value={
                    "first_name": "John",
                    "mobile": "+919876543210",
                    "is_looking_for_job": True
                },
                request_only=True
            )
        ]
    )
    def patch(self, request):
        """Partial update of user profile"""
        user = request.user

        # Ensure only job seekers can access this endpoint
        if user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProfileUpdateSerializer(
            user,
            data=request.data,
            context={'request': request},
            partial=True  # Partial update
        )

        if serializer.is_valid():
            serializer.save()
            # Update profile_updated timestamp
            user.profile_updated = timezone.now()
            user.save(update_fields=['profile_updated'])

            # Return full profile after update
            full_serializer = ProfileSerializer(user, context={'request': request})
            return Response(full_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileUploadView(APIView):
    """
    Handle file uploads for profile (profile picture and resume)
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Upload profile picture",
        description="Upload or update the user's profile picture",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'profile_pic': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Profile picture file (JPG, PNG, max 5MB)'
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Profile picture uploaded successfully"),
            400: OpenApiResponse(description="Invalid file or file too large"),
            401: OpenApiResponse(description="Authentication required")
        },
        tags=["Profile"]
    )
    def post(self, request):
        """Upload profile picture or resume"""
        user = request.user

        # Ensure only job seekers can access this endpoint
        if user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        file_type = request.data.get('file_type', 'profile_pic')  # 'profile_pic' or 'resume'

        if file_type == 'profile_pic':
            file = request.FILES.get('profile_pic')
            if not file:
                return Response(
                    {'error': 'No profile picture file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate file size (5MB max)
            if file.size > 5 * 1024 * 1024:
                return Response(
                    {'error': 'Profile picture size must not exceed 5MB'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
            if file.content_type not in allowed_types:
                return Response(
                    {'error': 'Only JPG, JPEG, and PNG files are allowed'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.profile_pic = file
            user.save()

            return Response(
                {
                    'message': 'Profile picture uploaded successfully',
                    'profile_pic_url': request.build_absolute_uri(user.profile_pic.url)
                },
                status=status.HTTP_200_OK
            )

        elif file_type == 'resume':
            file = request.FILES.get('resume')
            if not file:
                return Response(
                    {'error': 'No resume file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate file size (1MB max as per model help_text)
            if file.size > 1 * 1024 * 1024:
                return Response(
                    {'error': 'Resume size must not exceed 1MB'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate file type
            allowed_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/rtf',
                'application/vnd.oasis.opendocument.text'
            ]
            if file.content_type not in allowed_types:
                return Response(
                    {'error': 'Only PDF, DOC, DOCX, RTF, and ODT files are allowed'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.resume = file
            user.save()

            return Response(
                {
                    'message': 'Resume uploaded successfully',
                    'resume_url': request.build_absolute_uri(user.resume.url)
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {'error': 'Invalid file_type. Must be "profile_pic" or "resume"'},
            status=status.HTTP_400_BAD_REQUEST
        )


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


class ResumeDeleteView(APIView):
    """
    Delete user's resume
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Delete resume",
        description="Delete the authenticated user's resume file",
        responses={
            200: OpenApiResponse(description="Resume deleted successfully"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Only job seekers can access"),
            404: OpenApiResponse(description="No resume found")
        },
        tags=["Profile"]
    )
    def delete(self, request):
        """Delete user's resume"""
        user = request.user

        # Ensure only job seekers can access this endpoint
        if user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.resume:
            return Response(
                {'error': 'No resume found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Delete the file
        user.resume.delete(save=False)
        user.resume = None
        user.resume_title = ''
        user.resume_text = ''
        user.save()

        return Response(
            {'message': 'Resume deleted successfully'},
            status=status.HTTP_200_OK
        )
