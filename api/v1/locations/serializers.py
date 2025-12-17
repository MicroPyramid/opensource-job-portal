from rest_framework import serializers
from peeldb.models import Country, State, City


class CountrySerializer(serializers.ModelSerializer):
    """Serializer for Country model"""

    class Meta:
        model = Country
        fields = ['id', 'name', 'slug', 'status']


class StateSerializer(serializers.ModelSerializer):
    """Serializer for State model"""
    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.filter(status='Enabled'),
        source='country',
        write_only=True,
        required=False
    )

    class Meta:
        model = State
        fields = ['id', 'name', 'slug', 'status', 'country', 'country_id']


class CitySerializer(serializers.ModelSerializer):
    """Serializer for City model"""
    state = StateSerializer(read_only=True)
    state_id = serializers.PrimaryKeyRelatedField(
        queryset=State.objects.filter(status='Enabled'),
        source='state',
        write_only=True,
        required=False
    )
    country_name = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = [
            'id', 'name', 'slug', 'status',
            'state', 'state_id', 'country_name'
        ]
        read_only_fields = ['id', 'name', 'slug', 'status', 'state', 'country_name']

    def get_country_name(self, obj):
        """Get country name from state"""
        if obj.state and obj.state.country:
            return obj.state.country.name
        return None

    def validate(self, attrs):
        """
        Prevent city creation via API.
        Added as part of location cleanup initiative (LOCATION_CLEANUP_PLAN.md Phase 1)
        """
        if self.instance is None:  # Creating new city
            raise serializers.ValidationError({
                'detail': 'Creating new cities via API is not allowed. '
                         'Please select from existing cities or contact admin to add new locations.'
            })
        return attrs


class CityListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for city listings"""
    state_name = serializers.CharField(source='state.name', read_only=True)
    country_name = serializers.CharField(source='state.country.name', read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name', 'state_name', 'country_name']
