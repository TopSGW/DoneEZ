# serializers.py
from rest_framework import serializers
from dateutil import parser
from django.core.validators import RegexValidator


class MessageSerializer(serializers.Serializer):
    soundConfigName = serializers.CharField(max_length=100)
    message = serializers.CharField(max_length=1000)
    timeStamp = serializers.CharField(max_length=100)
    toPhoneNumber = serializers.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in E.164 format: +1234567890"
            )
        ]
    )

    def validate_timeStamp(self, value):
        """Validate and normalize timestamp format"""
        try:
            return parser.isoparse(value).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            raise serializers.ValidationError(f"Invalid timestamp format: {str(e)}")