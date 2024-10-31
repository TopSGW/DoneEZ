# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import logging
from .serializers import MessageSerializer
from .services import TwilioService, WhatsAppMessageError

logger = logging.getLogger(__name__)

class SendMessageView(APIView):
    permission_classes = []
    """API endpoint for sending WhatsApp messages"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.twilio_service = TwilioService()

    def _format_message(self, data: dict) -> dict:
        """Format the message text with all required information"""
        return { 
            "1" : data['soundConfigName'],
            "2": data['timeStamp'],
            "3" : data['message']
        }

    def post(self, request):
        """Handle POST request to send WhatsApp message"""
        logger.debug(f"Received message request with data: {request.data}")
        
        serializer = MessageSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(f"Invalid request data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            message_text = self._format_message(serializer.validated_data)
            logger.debug(f"Formatted message: {message_text}")
            
            message_sid = self.twilio_service.send_whatsapp_message(
                message=message_text,
                to=serializer.validated_data['toPhoneNumber']
            )
            
            logger.info(f"Message sent successfully. SID: {message_sid}")
            return Response({'sid': message_sid}, status=status.HTTP_200_OK)
            
        except WhatsAppMessageError as e:
            logger.error(f"WhatsApp message error: {str(e)}")
            return Response(
                {'error': 'Failed to send message', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
