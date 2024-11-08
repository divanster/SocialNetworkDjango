# backend/users/utils.py

from twilio.rest import Client  # pylint: disable=import-error
from django.conf import settings
import logging

logger = logging.getLogger('users')

def send_2fa_code(phone_number, code):
    """
    Sends a 2FA code via SMS using Twilio.
    """
    try:
        twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = twilio_client.messages.create(
            body=f"Your verification code is {code}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        logger.info(f"Sent 2FA code to {phone_number}")
    except Exception as e:
        logger.error(f"Failed to send 2FA code to {phone_number}: {str(e)}")
