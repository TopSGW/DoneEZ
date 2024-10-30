# services.py
from twilio.rest import Client
from django.conf import settings
import logging
from typing import Dict, Optional
from datetime import datetime
from dateutil import parser

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
            
            message = self.client.messages.create(
                from_=self.whatsapp_from,
                body=message,
                to=to_number
            )
            
            logger.info(f"Message sent successfully. SID: {message.sid}")
            return message.sid
            
        except Exception as e:
            error_msg = f"Failed to send WhatsApp message: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise WhatsAppMessageError(error_msg)