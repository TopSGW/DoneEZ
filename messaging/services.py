# services.py

from twilio.rest import Client
from django.conf import settings
import logging
import json  # For serializing variables

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    def send_whatsapp_message(self, content_sid: str, content_variables: dict, to: str) -> str:
        """
        Sends a WhatsApp message using a Twilio template.
        
        :param content_sid: The Content SID of the Twilio message template.
        :param content_variables: A dictionary mapping template variable indices to their values.
        :param to: The recipient's WhatsApp number (e.g., 'whatsapp:+1234567890').
        :return: The SID of the sent message.
        """
        if not to.startswith('whatsapp:'):
            to = f'whatsapp:{to}'
        
        try:
            # Serialize the variables to a JSON string as required by Twilio
            variables_json = json.dumps(content_variables)
            
            message = self.client.messages.create(
                from_=settings.TWILIO_WHATSAPP_FROM,  # Ensure this is in 'whatsapp:+1234567890' format
                content_sid=content_sid,
                content_variables=variables_json,
                to=to
            )
            logger.info(f"Message sent successfully. SID: {message.sid}")
            return message.sid
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            raise
