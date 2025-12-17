"""
Profile Views for Job Seekers - Core Profile Management
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from django.utils import timezone

from .serializers import ProfileSerializer, ProfileUpdateSerializer


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
