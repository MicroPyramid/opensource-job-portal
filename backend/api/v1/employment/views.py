from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from peeldb.models import EmploymentHistory
from .serializers import (
    EmploymentHistorySerializer,
    EmploymentHistoryCreateUpdateSerializer
)


class UserEmploymentHistoryListView(APIView):
    """
    Get list of current user's employment history
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List user's employment history",
        description="Get list of all employment history for the authenticated user, ordered by date (most recent first)",
        responses={200: EmploymentHistorySerializer(many=True)},
        tags=["Employment History"]
    )
    def get(self, request):
        user = request.user
        if user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get employment history, ordered by from_date descending (most recent first)
        employment_history = user.employment_history.all().order_by('-from_date')
        serializer = EmploymentHistorySerializer(employment_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserEmploymentHistoryCreateView(APIView):
    """
    Add a new employment record to user's profile
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Add employment record",
        description="Add a new employment history record to the authenticated user's profile",
        request=EmploymentHistoryCreateUpdateSerializer,
        responses={201: EmploymentHistorySerializer},
        tags=["Employment History"]
    )
    def post(self, request):
        user = request.user
        if user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = EmploymentHistoryCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            # If this is marked as current job, unmark any existing current jobs
            if serializer.validated_data.get('current_job', False):
                user.employment_history.filter(current_job=True).update(current_job=False)

            # Create employment history
            employment = serializer.save()
            user.employment_history.add(employment)

            # Return full serialized data
            response_serializer = EmploymentHistorySerializer(employment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserEmploymentHistoryDetailView(APIView):
    """
    Retrieve, update, or delete a specific employment record
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, user, employment_id):
        """Get employment history if it belongs to the user"""
        try:
            return user.employment_history.get(id=employment_id)
        except EmploymentHistory.DoesNotExist:
            return None

    @extend_schema(
        summary="Get employment record details",
        description="Get details of a specific employment history record",
        responses={200: EmploymentHistorySerializer},
        tags=["Employment History"]
    )
    def get(self, request, employment_id):
        user = request.user
        if user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        employment = self.get_object(user, employment_id)
        if not employment:
            return Response(
                {'error': 'Employment record not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EmploymentHistorySerializer(employment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update employment record",
        description="Update a specific employment history record",
        request=EmploymentHistoryCreateUpdateSerializer,
        responses={200: EmploymentHistorySerializer},
        tags=["Employment History"]
    )
    def patch(self, request, employment_id):
        user = request.user
        if user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        employment = self.get_object(user, employment_id)
        if not employment:
            return Response(
                {'error': 'Employment record not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EmploymentHistoryCreateUpdateSerializer(
            employment,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            # If marking as current job, unmark any existing current jobs
            if serializer.validated_data.get('current_job', False):
                user.employment_history.filter(current_job=True).exclude(id=employment_id).update(current_job=False)

            serializer.save()
            response_serializer = EmploymentHistorySerializer(employment)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete employment record",
        description="Remove an employment history record from the user's profile",
        responses={204: None},
        tags=["Employment History"]
    )
    def delete(self, request, employment_id):
        user = request.user
        if user.user_type != 'JS':
            return Response(
                {'error': 'Only job seekers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        employment = self.get_object(user, employment_id)
        if not employment:
            return Response(
                {'error': 'Employment record not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        user.employment_history.remove(employment)
        employment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
