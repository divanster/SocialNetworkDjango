# backend/kafka_app/tasks/user_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient
from users.services import create_notification

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_user_event_task(self, user_id, event_type):
    """
    Celery task to process user events and send them to Kafka and WebSocket notifications.

    Args:
        self: Celery task instance.
        user_id (int): The ID of the user for which the event is being processed.
        event_type (str): The type of event ('new_user', 'profile_update', 'deleted_user').

    Returns:
        None
    """
    try:
        from users.models import CustomUser  # Local import to avoid circular dependencies
        producer = KafkaProducerClient()

        user = CustomUser.objects.get(id=user_id)

        # Construct the Kafka message
        message = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "event": event_type,
        }

        # Send to Kafka
        kafka_topic = settings.KAFKA_TOPICS.get('USER_EVENTS', 'user-events')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for user {event_type} event: {message}")

        # WebSocket notification
        send_user_websocket_notification(user, event_type)

    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist. User event not processed.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending user {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"An error occurred while processing the user event: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff


def send_user_websocket_notification(user, event_type):
    """
    Send WebSocket notification for a user event.

    Args:
        user (CustomUser): The user instance for which the notification is being sent.
        event_type (str): The type of event ('new_user', 'profile_update', 'deleted_user').
    """
    try:
        from utils.group_names import get_user_group_name  # Assuming you have a utility function
        user_group_name = get_user_group_name(user.id)  # Use utility function
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'user_notification',
                'message': f"User event '{event_type}' processed for {user.username}.",
                'event': event_type,
                'user_id': str(user.id),
                'username': user.username,
            }
        )
        logger.info(f"Real-time WebSocket notification sent for user {event_type} with ID {user.id}")

    except Exception as e:
        logger.error(f"Error sending WebSocket notification for user event {event_type}: {e}")


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def send_welcome_email(self, user_id):
    """
    Celery task to send a welcome email to a new user.

    Args:
        self: Celery task instance.
        user_id (int): The ID of the user to whom the email should be sent.

    Returns:
        None
    """
    try:
        from users.models import CustomUser  # Local import to avoid circular dependencies
        from django.core.mail import send_mail

        user = CustomUser.objects.get(id=user_id)

        # Prepare the email content
        subject = "Welcome to the Platform!"
        message = f"Hello {user.username},\n\nWelcome to our platform! We're glad to have you."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        # Send the email
        send_mail(subject, message, from_email, recipient_list)
        logger.info(f"[TASK] Sent welcome email to user: {user.email}")

    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist. Cannot send welcome email.")
    except Exception as e:
        logger.error(f"[TASK] Error sending welcome email to user {user_id}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def send_profile_update_notification(self, user_id):
    """
    Celery task to send a notification when a user's profile is updated.

    Args:
        self: Celery task instance.
        user_id (int): The ID of the user whose profile was updated.

    Returns:
        None
    """
    try:
        from users.models import CustomUser  # Local import to avoid circular dependencies

        user = CustomUser.objects.get(id=user_id)

        # Prepare the notification data for the profile update
        notification_data = {
            'sender_id': user.id,
            'sender_username': user.username,
            'receiver_id': user.id,
            'receiver_username': user.username,
            'notification_type': 'profile_update',
            'text': f"Hello {user.username}, your profile has been updated successfully.",
        }

        # Create a notification to inform the user about the profile update
        create_notification(notification_data)
        logger.info(f"[TASK] Sent profile update notification to user: {user.email}")

    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist. Cannot send profile update notification.")
    except Exception as e:
        logger.error(f"[TASK] Error sending profile update notification to user {user_id}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
