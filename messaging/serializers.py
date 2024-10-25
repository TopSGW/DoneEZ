from rest_framework import serializers

class MessageSerializer(serializers.Serializer):
    soundConfigName = serializers.CharField(max_length=100)
    message = serializers.CharField(max_length=1000)
    timeStamp = serializers.DateTimeField()
    toPhoneNumber = serializers.CharField(max_length=15)  # Add this field