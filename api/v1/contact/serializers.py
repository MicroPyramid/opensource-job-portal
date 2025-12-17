"""
Serializers for Contact API
"""
from rest_framework import serializers
from peeldb.models import simplecontact, ENQUERY_TYPES


class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for contact form submissions
    """
    # Make category match the frontend naming
    category = serializers.ChoiceField(
        choices=ENQUERY_TYPES,
        source='enquery_type',
        help_text="Type of inquiry"
    )

    class Meta:
        model = simplecontact
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'category', 'subject', 'comment', 'contacted_on']
        read_only_fields = ['id', 'contacted_on']
        extra_kwargs = {
            'first_name': {'required': True, 'help_text': 'First name'},
            'last_name': {'required': False, 'help_text': 'Last name (optional)'},
            'email': {'required': True, 'help_text': 'Email address'},
            'phone': {'required': False, 'help_text': 'Phone number (optional)'},
            'subject': {'required': True, 'help_text': 'Subject of inquiry'},
            'comment': {'required': True, 'help_text': 'Message/comment', 'min_length': 10},
        }

    def validate_comment(self, value):
        """Validate comment length"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long")
        return value.strip()


class ContactResponseSerializer(serializers.Serializer):
    """
    Response serializer for successful contact form submission
    """
    id = serializers.IntegerField(help_text="Contact inquiry ID")
    message = serializers.CharField(help_text="Success message")
