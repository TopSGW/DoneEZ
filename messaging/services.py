from twilio.rest import Client
from django.conf import settings

class TwilioService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    def send_whatsapp_message(self, body):
        message = self.client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            body=body,
            to=settings.TWILIO_WHATSAPP_TO
        )
        return message.sid
