# backend/kafka_app/tasks/user_tasks.py

import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from aiokafka.errors import KafkaTimeoutError

from core.task_utils import BaseTask
from kafka_app.constants import (
    USER_EVENTS,
    USER_REGISTERED,
    WELCOME_EMAIL_SENT,
    PROFILE_UPDATE_NOTIFIED
)
from kafka_app.services import KafkaService
from users.models import CustomUser

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_user_event_task(self, user_id, event_type):
    """
    Celery task to process user events and send them to Kafka.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        data = {
            'id': str(user.id),           # Include 'id' within 'data'
            'user_id': str(user.id),
            'username': user.username,
            'email': user.email,
            'event_type': event_type,
            # Add other relevant fields as needed
        }
        message = {
            'app': 'users',
            'event_type': event_type,
            'model_name': 'CustomUser',
            'id': str(user_id),
            'data': data,
        }
        kafka_topic_key = USER_EVENTS  # Use constant from constants.py
        KafkaService().send_message(kafka_topic_key, message)  # Pass the key directly
        logger.info(f"[TASK] Sent Kafka message for user event: {message}")
    except CustomUser.DoesNotExist:
        logger.error(f"[TASK] User with ID {user_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"[TASK] Kafka timeout error while sending user event '{event_type}': {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    except Exception as e:
        logger.error(f"[TASK] Error sending Kafka message for user event: {e}")
        self.retry(exc=e, countdown=60)


@shared_task(bind=True, base=BaseTask, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id):
    """
    Celery task to send a welcome email to a new user.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        send_mail(
            'Welcome to Our Platform!',
            'Thank you for signing up.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"[TASK] Welcome email sent to user {user.username} ({user.id})")

        # Optional: Send Kafka message for welcome email event
        data = {
            'id': str(user.id),
            'user_id': str(user.id),
            'username': user.username,
            'email': user.email,
            'event_type': WELCOME_EMAIL_SENT,
        }
        message = {
            'app': 'users',
            'event_type': WELCOME_EMAIL_SENT,
            'model_name': 'CustomUser',
            'id': str(user.id),
            'data': data,
        }
        kafka_topic_key = USER_EVENTS  # Use constant from constants.py
        KafkaService().send_message(kafka_topic_key, message)
        logger.info(f"[TASK] Sent Kafka message for welcome email event: {message}")

    except CustomUser.DoesNotExist:
        logger.error(f"[TASK] User with ID {user_id} does not exist.")
        self.retry(exc=Exception("User does not exist"), countdown=60)
    except KafkaTimeoutError as e:
        logger.error(f"[TASK] Kafka timeout error while sending welcome email event: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    except Exception as e:
        logger.error(f"[TASK] Failed to send welcome email to user {user_id}: {e}")
        self.retry(exc=e, countdown=60)


@shared_task(bind=True, base=BaseTask, max_retries=3, default_retry_delay=60)
def send_profile_update_notification(self, user_id):
    """
    Celery task to send a notification email when a user's profile is updated.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        send_mail(
            'Your Profile Has Been Updated',
            'Your profile information has been successfully updated.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"[TASK] Profile update notification sent to user {user.username} ({user.id})")

        # Optional: Send Kafka message for profile update event
        data = {
            'id': str(user.id),
            'user_id': str(user.id),
            'username': user.username,
            'email': user.email,
            'event_type': PROFILE_UPDATE_NOTIFIED,
        }
        message = {
            'app': 'users',
            'event_type': PROFILE_UPDATE_NOTIFIED,
            'model_name': 'CustomUser',
            'id': str(user.id),
            'data': data,
        }
        kafka_topic_key = USER_EVENTS  # Use constant from constants.py
        KafkaService().send_message(kafka_topic_key, message)
        logger.info(f"[TASK] Sent Kafka message for profile update event: {message}")

    except CustomUser.DoesNotExist:
        logger.error(f"[TASK] User with ID {user_id} does not exist.")
        self.retry(exc=Exception("User does not exist"), countdown=60)
    except KafkaTimeoutError as e:
        logger.error(f"[TASK] Kafka timeout error while sending profile update event: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    except Exception as e:
        logger.error(f"[TASK] Failed to send profile update notification to user {user_id}: {e}")
        self.retry(exc=e, countdown=60)
