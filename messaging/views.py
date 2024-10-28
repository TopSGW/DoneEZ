# views.py
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MessageSerializer
from .services import TwilioService
import logging

logger = logging.getLogger(__name__)

class SendMessageView(APIView):
    permission_classes = []  # No authentication required for registration

    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            sound_config_name = serializer.validated_data['soundConfigName']
            message_content = serializer.validated_data['message']
            message_timestamp = serializer.validated_data['timeStamp']
            to_phone_number = serializer.validated_data['toPhoneNumber']
            
            # Construct a dictionary for template variables
            variables = {
                "1": sound_config_name,
                "2": message_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "3": message_content  
            }
            
            twilio_service = TwilioService()
            try:
                message_sid = twilio_service.send_whatsapp_message(
                    content_sid=settings.TWILIO_CONTENT_ID,  # Replace with your actual Content SID
                    content_variables=variables,
                    to="whatsapp:" + to_phone_number
                )
                logger.info(f"Sent WhatsApp message SID: {message_sid} to {to_phone_number}")
                return Response({'sid': message_sid}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Failed to send WhatsApp message to {to_phone_number}: {str(e)}")
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warning(f"Invalid serializer data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
