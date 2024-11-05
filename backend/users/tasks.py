from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from notifications.services import create_notification
import logging
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from websocket.consumers import GeneralKafkaConsumer  # Import for generating group names

logger = logging.getLogger('users')

@shared_task
def process_user_event_task(user_id, event_type):
    """
    Celery task to process user events and send them to Kafka and WebSocket notifications.

    Args:
        user_id (int): The ID of the user for which the event is being processed.
        event_type (str): The type of event ('new_user', 'profile_update', 'deleted_user').
    """
    producer = KafkaProducerClient()

    try:
        # Import models dynamically to avoid AppRegistryNotReady errors
        from users.models import CustomUser

        user = CustomUser.objects.get(id=user_id)

        # Construct the Kafka message
        message = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "event": event_type,
        }

        # Send to Kafka
        kafka_topic = settings.KAFKA_TOPICS.get('USER_EVENTS', 'default-user-topic')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for user {event_type} event: {message}")

        # WebSocket notification
        send_user_websocket_notification(user, event_type)

    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist. User event not processed.")
    except Exception as e:
        logger.error(f"An error occurred while processing the user event: {e}")
    finally:
        producer.close()  # Close the Kafka producer properly


def send_user_websocket_notification(user, event_type):
    """
    Send WebSocket notification for a user event.

    Args:
        user (CustomUser): The user instance for which the notification is being sent.
        event_type (str): The type of event ('new_user', 'profile_update', 'deleted_user').
    """
    try:
        user_group_name = GeneralKafkaConsumer.generate_group_name(user.id)
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


@shared_task
def send_welcome_email(user_id):
    """
    Celery task to send a welcome email to a new user.

    Args:
        user_id (int): The ID of the user to whom the email should be sent.
    """
    try:
        # Import models dynamically to avoid AppRegistryNotReady errors
        from users.models import CustomUser

        user = CustomUser.objects.get(id=user_id)

        # Prepare the notification data for the welcome email
        notification_data = {
            'sender_id': user.id,
            'sender_username': 'System',  # System user for notifications
            'receiver_id': user.id,
            'receiver_username': user.username,
            'notification_type': 'welcome',
            'text': f"Welcome to the platform, {user.username}!",
        }

        # Create a notification to trigger the welcome email
        create_notification(notification_data)
        logger.info(f"[TASK] Sent welcome email to user: {user.email}")

    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist. Cannot send welcome email.")
    except Exception as e:
        logger.error(f"[TASK] Error sending welcome email to user {user_id}: {e}")


@shared_task
def send_profile_update_notification(user_id):
    """
    Celery task to send a notification when a user's profile is updated.

    Args:
        user_id (int): The ID of the user whose profile was updated.
    """
    try:
        # Import models dynamically to avoid AppRegistryNotReady errors
        from users.models import CustomUser

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
