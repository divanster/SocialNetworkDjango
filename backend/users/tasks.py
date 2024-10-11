# backend/users/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from users.models import CustomUser
import logging

logger = logging.getLogger('users')

@shared_task
def send_welcome_email(user_id):
    """
    Task to send a welcome email to a newly registered user.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        subject = "Welcome to Our Platform!"
        message = f"Hello {user.username}, welcome to our social network!"
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"Welcome email sent to user {user.email}")
    except CustomUser.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist. Welcome email not sent.")
    except Exception as e:
        logger.error(f"An error occurred while sending the welcome email: {e}")

@shared_task
def send_profile_update_notification(user_id):
    """
    Task to send an email notification after a user updates their profile.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        subject = "Profile Update Successful"
        message = f"Hi {user.username}, your profile has been successfully updated."
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"Profile update notification email sent to user {user.email}")
    except CustomUser.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist. Profile update email not sent.")
    except Exception as e:
        logger.error(f"An error occurred while sending the profile update notification: {e}")
