from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from peeldb.models import Country, State, City
from .serializers import (
    CountrySerializer,
    StateSerializer,
    CitySerializer,
    CityListSerializer
)


class CountryListView(APIView):
    """
    Get list of all enabled countries
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="List all countries",
        description="Get list of all enabled countries",
        responses={200: CountrySerializer(many=True)},
        tags=["Locations"]
    )
    def get(self, request):
        countries = Country.objects.filter(status='Enabled').order_by('name')
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StateListView(APIView):
    """
    Get list of states, optionally filtered by country
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="List states",
        description="Get list of all enabled states, optionally filtered by country_id",
        parameters=[
            OpenApiParameter(
                name='country_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter states by country ID',
                required=False
            )
        ],
        responses={200: StateSerializer(many=True)},
        tags=["Locations"]
    )
    def get(self, request):
        country_id = request.query_params.get('country_id')

        states = State.objects.filter(status='Enabled')

        if country_id:
            states = states.filter(country_id=country_id)

        states = states.select_related('country').order_by('name')
        serializer = StateSerializer(states, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CityListView(APIView):
    """
    Get list of cities, optionally filtered by state or country
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="List cities",
        description="Get list of all enabled cities, optionally filtered by state_id or country_id",
        parameters=[
            OpenApiParameter(
                name='state_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter cities by state ID',
                required=False
            ),
            OpenApiParameter(
                name='country_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter cities by country ID',
                required=False
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search cities by name (case-insensitive)',
                required=False
            )
        ],
        responses={200: CityListSerializer(many=True)},
        tags=["Locations"]
    )
    def get(self, request):
        state_id = request.query_params.get('state_id')
        country_id = request.query_params.get('country_id')
        search = request.query_params.get('search')

        cities = City.objects.filter(status='Enabled')

        if state_id:
            cities = cities.filter(state_id=state_id)
        elif country_id:
            cities = cities.filter(state__country_id=country_id)

        if search:
            cities = cities.filter(name__icontains=search)

        cities = cities.select_related('state', 'state__country').order_by('name')[:100]  # Limit to 100 results
        serializer = CityListSerializer(cities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CityDetailView(APIView):
    """
    Get details of a specific city
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Get city details",
        description="Get detailed information about a specific city",
        responses={200: CitySerializer},
        tags=["Locations"]
    )
    def get(self, request, city_id):
        try:
            city = City.objects.select_related('state', 'state__country').get(
                id=city_id,
                status='Enabled'
            )
            serializer = CitySerializer(city)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except City.DoesNotExist:
            return Response(
                {'error': 'City not found'},
                status=status.HTTP_404_NOT_FOUND
            )
