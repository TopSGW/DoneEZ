from rest_framework import serializers
from django.core.validators import RegexValidator
from dateutil import parser
import pytz

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
        """
        Validate and normalize timestamp format to 12-hour clock with AM/PM in EST timezone
        """
        try:
            # Parse the input timestamp
            parsed_time = parser.isoparse(value)
            
            # Convert to EST timezone
            est_tz = pytz.timezone('America/New_York')
            if parsed_time.tzinfo is None:
                parsed_time = pytz.utc.localize(parsed_time)
            est_time = parsed_time.astimezone(est_tz)
            
            # Format to 12-hour clock with AM/PM
            return est_time.strftime("%Y-%m-%d %I:%M:%S %p")
        except ValueError as e:
            raise serializers.ValidationError(f"Invalid timestamp format: {str(e)}")