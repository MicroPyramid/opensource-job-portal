from rest_framework import serializers
from peeldb.models import Skill, TechnicalSkill


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for Skill model - master skill list"""

    class Meta:
        model = Skill
        fields = ['id', 'name', 'slug', 'skill_type', 'status']
        read_only_fields = fields


class TechnicalSkillSerializer(serializers.ModelSerializer):
    """Serializer for user's technical skills with proficiency"""
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.filter(status='Active'),
        source='skill',
        write_only=True
    )

    class Meta:
        model = TechnicalSkill
        fields = [
            'id', 'skill', 'skill_id', 'year', 'month',
            'last_used', 'version', 'proficiency', 'is_major'
        ]


class TechnicalSkillCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating technical skills"""

    class Meta:
        model = TechnicalSkill
        fields = [
            'skill', 'year', 'month', 'last_used',
            'version', 'proficiency', 'is_major'
        ]

    def validate_year(self, value):
        """Validate years of experience"""
        if value is not None and (value < 0 or value > 50):
            raise serializers.ValidationError("Years must be between 0 and 50")
        return value

    def validate_month(self, value):
        """Validate months of experience"""
        if value is not None and (value < 0 or value > 11):
            raise serializers.ValidationError("Months must be between 0 and 11")
        return value
