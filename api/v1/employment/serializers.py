from rest_framework import serializers
from peeldb.models import EmploymentHistory
from datetime import date


class EmploymentHistorySerializer(serializers.ModelSerializer):
    """Serializer for employment history"""
    duration = serializers.SerializerMethodField()

    class Meta:
        model = EmploymentHistory
        fields = [
            'id', 'company', 'designation', 'from_date',
            'to_date', 'current_job', 'job_profile', 'duration'
        ]

    def get_duration(self, obj):
        """Calculate duration in months"""
        if not obj.from_date:
            return None

        end_date = obj.to_date if obj.to_date else date.today()
        start_date = obj.from_date

        # Calculate months
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        years = months // 12
        remaining_months = months % 12

        if years > 0 and remaining_months > 0:
            return f"{years}y {remaining_months}m"
        elif years > 0:
            return f"{years}y"
        elif remaining_months > 0:
            return f"{remaining_months}m"
        else:
            return "Less than a month"


class EmploymentHistoryCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating employment history"""

    class Meta:
        model = EmploymentHistory
        fields = [
            'company', 'designation', 'from_date',
            'to_date', 'current_job', 'job_profile'
        ]

    def validate(self, data):
        """Validate employment dates"""
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        current_job = data.get('current_job', False)

        # If current job, to_date should be None
        if current_job and to_date:
            raise serializers.ValidationError({
                'to_date': 'Current job should not have an end date'
            })

        # If not current job, to_date is required
        if not current_job and not to_date:
            raise serializers.ValidationError({
                'to_date': 'End date is required for past jobs'
            })

        # Validate date order
        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError({
                'to_date': 'End date must be after start date'
            })

        # Validate dates are not in future
        today = date.today()
        if from_date and from_date > today:
            raise serializers.ValidationError({
                'from_date': 'Start date cannot be in the future'
            })

        if to_date and to_date > today:
            raise serializers.ValidationError({
                'to_date': 'End date cannot be in the future'
            })

        return data
