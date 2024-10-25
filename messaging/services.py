from twilio.rest import Client
from django.conf import settings

class TwilioService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    def send_whatsapp_message(self, body):
        message = self.client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            content_sid='HXab2232fa8673aca71ad3e618780e0118',
            content_variables='{"1":"dddd","2":"3pm", "3": "Hello How are you?"}',
            to=settings.TWILIO_WHATSAPP_TO
        )
        return message.sid
