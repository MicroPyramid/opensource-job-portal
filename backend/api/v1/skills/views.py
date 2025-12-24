from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from peeldb.models import Skill, TechnicalSkill
from .serializers import (
    SkillSerializer,
    TechnicalSkillSerializer,
    TechnicalSkillCreateUpdateSerializer
)


class SkillListView(APIView):
    """
    Get list of all available skills with optional search
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="List all skills",
        description="Get list of all active skills, optionally filtered by search query or skill type",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search skills by name (case-insensitive)',
                required=False
            ),
            OpenApiParameter(
                name='skill_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by skill type (it, non_it, etc.)',
                required=False
            )
        ],
        responses={200: SkillSerializer(many=True)},
        tags=["Skills"]
    )
    def get(self, request):
        search = request.query_params.get('search')
        skill_type = request.query_params.get('skill_type')

        skills = Skill.objects.filter(status='Active')

        if search:
            skills = skills.filter(name__icontains=search)

        if skill_type:
            skills = skills.filter(skill_type=skill_type)

        skills = skills.order_by('name')[:100]  # Limit to 100 results
        serializer = SkillSerializer(skills, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserTechnicalSkillListView(APIView):
    """
    Get list of current user's technical skills
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List user's technical skills",
        description="Get list of all technical skills for the authenticated user",
        responses={200: TechnicalSkillSerializer(many=True)},
        tags=["Skills"]
    )
    def get(self, request):
        user = request.user
        if user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        technical_skills = user.skills.all().select_related('skill')
        serializer = TechnicalSkillSerializer(technical_skills, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserTechnicalSkillCreateView(APIView):
    """
    Add a new technical skill to user's profile
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Add technical skill",
        description="Add a new technical skill to the authenticated user's profile",
        request=TechnicalSkillCreateUpdateSerializer,
        responses={201: TechnicalSkillSerializer},
        tags=["Skills"]
    )
    def post(self, request):
        user = request.user
        if user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TechnicalSkillCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            # Check if skill already exists for user
            skill = serializer.validated_data['skill']
            if user.skills.filter(skill=skill).exists():
                return Response(
                    {'error': 'This skill already exists in your profile'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create technical skill
            technical_skill = serializer.save()
            user.skills.add(technical_skill)

            # Return full serialized data
            response_serializer = TechnicalSkillSerializer(technical_skill)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserTechnicalSkillDetailView(APIView):
    """
    Retrieve, update, or delete a specific technical skill
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, user, skill_id):
        """Get technical skill if it belongs to the user"""
        try:
            return user.skills.select_related('skill').get(id=skill_id)
        except TechnicalSkill.DoesNotExist:
            return None

    @extend_schema(
        summary="Get technical skill details",
        description="Get details of a specific technical skill",
        responses={200: TechnicalSkillSerializer},
        tags=["Skills"]
    )
    def get(self, request, skill_id):
        user = request.user
        if user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        technical_skill = self.get_object(user, skill_id)
        if not technical_skill:
            return Response(
                {'error': 'Technical skill not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TechnicalSkillSerializer(technical_skill)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update technical skill",
        description="Update a specific technical skill",
        request=TechnicalSkillCreateUpdateSerializer,
        responses={200: TechnicalSkillSerializer},
        tags=["Skills"]
    )
    def patch(self, request, skill_id):
        user = request.user
        if user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        technical_skill = self.get_object(user, skill_id)
        if not technical_skill:
            return Response(
                {'error': 'Technical skill not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TechnicalSkillCreateUpdateSerializer(
            technical_skill,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            # If skill is being changed, check for duplicates
            if 'skill' in serializer.validated_data:
                new_skill = serializer.validated_data['skill']
                if user.skills.filter(skill=new_skill).exclude(id=skill_id).exists():
                    return Response(
                        {'error': 'This skill already exists in your profile'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer.save()
            response_serializer = TechnicalSkillSerializer(technical_skill)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete technical skill",
        description="Remove a technical skill from the user's profile",
        responses={204: None},
        tags=["Skills"]
    )
    def delete(self, request, skill_id):
        user = request.user
        if user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        technical_skill = self.get_object(user, skill_id)
        if not technical_skill:
            return Response(
                {'error': 'Technical skill not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        user.skills.remove(technical_skill)
        technical_skill.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
