# services.py
from twilio.rest import Client
from django.conf import settings
import logging
from typing import Dict, Optional
from datetime import datetime
from dateutil import parser
import json

logger = logging.getLogger(__name__)

class WhatsAppMessageError(Exception):
    """Custom exception for WhatsApp messaging errors"""
    pass

class TwilioService:
    """Service class for handling Twilio WhatsApp communication"""
    
    def __init__(self, account_sid: Optional[str] = None, auth_token: Optional[str] = None):
        self.client = Client(
            account_sid or settings.TWILIO_ACCOUNT_SID,
            auth_token or settings.TWILIO_AUTH_TOKEN
        )
        self.whatsapp_from = settings.TWILIO_WHATSAPP_FROM
        self.content_sid = settings.TWILIO_CONTENT_ID
        self.messaging_service_sid = settings.TWILIO_MESSAGE_SERVICE_ID
        
    def _format_whatsapp_number(self, phone_number: str) -> str:
        """Ensures phone number has whatsapp: prefix"""
        return f"whatsapp:{phone_number}" if not phone_number.startswith('whatsapp:') else phone_number
    
    def send_whatsapp_message(self, message: str, to: str) -> str:
        """
        Send a WhatsApp message using Twilio
        
        Args:
            message: The message text to send
            to: Recipient's phone number
            
        Returns:
            str: Message SID from Twilio
            
        Raises:
            WhatsAppMessageError: If message sending fails
        """
        try:
            logger.debug(f"Sending WhatsApp message to {to}: {message}")
            to_number = self._format_whatsapp_number(to)
            content_variables_json = json.dumps(message, ensure_ascii=False)

            try:
                json.loads(content_variables_json)
                print("JSON is valid.", content_variables_json)

            except json.JSONDecodeError as e:
                print("JSON decoding error:", e)
                # Handle the error as needed

            message = self.client.messages.create(
                from_=self.whatsapp_from,
                content_sid=self.content_sid,
                content_variables=content_variables_json,
                to=to_number,
                messaging_service_sid=self.messaging_service_sid
            )
            
            logger.info(f"Message sent successfully. SID: {message.sid}")
            return message.sid
            
        except Exception as e:
            error_msg = f"Failed to send WhatsApp message: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise WhatsAppMessageError(error_msg)