from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MessageSerializer
from .services import TwilioService

class SendMessageView(APIView):
    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            sound_config_name = serializer.validated_data['soundConfigName']
            message_content = serializer.validated_data['message']
            body = f"Alert name: {sound_config_name} {message_content}"
            
            twilio_service = TwilioService()
            try:
                message_sid = twilio_service.send_whatsapp_message(body)
                return Response({'sid': message_sid}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
