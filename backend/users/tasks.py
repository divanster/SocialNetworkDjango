from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from notifications.services import create_notification
import logging
from django.conf import settings

logger = logging.getLogger('users')


@shared_task
def process_user_event_task(user_id, event_type):
    """
    Celery task to process user events and send them to Kafka.

    Args:
        user_id (int): The ID of the user for which the event is being processed.
        event_type (str): The type of event ('new_user', 'profile_update', 'deleted_user').
    """
    producer = KafkaProducerClient()

    try:
        # Import models dynamically to avoid AppRegistryNotReady errors
        from users.models import CustomUser

        user = CustomUser.objects.get(id=user_id)
        if event_type == 'new_user':
            # Handle user registration logic
            handle_user_registration(user)

        elif event_type == 'profile_update':
            # Handle profile update logic
            handle_profile_update(user)

        elif event_type == 'deleted_user':
            # Handle user deletion logic
            handle_user_deletion(user)

        else:
            logger.warning(f"[USER] Unknown event type: {event_type}")
            return

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

    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist. User event not processed.")
    except Exception as e:
        logger.error(f"An error occurred while processing the user event: {e}")
    finally:
        producer.close()  # Close the Kafka producer properly


def handle_user_registration(user):
    """
    Handles logic related to new user registration.

    Args:
        user (CustomUser): The user object.
    """
    try:
        # Import models dynamically to avoid AppRegistryNotReady errors
        from users.models import UserProfile

        # Create UserProfile automatically when a new user registers
        UserProfile.objects.create(user=user)
        logger.info(f"[USER] UserProfile created for user: {user.email}")

        # Optionally, trigger a notification to welcome the user
        notification_data = {
            'sender_id': user.id,
            'sender_username': user.username,
            'receiver_id': user.id,
            'receiver_username': user.username,
            'notification_type': 'welcome',
            'text': f"Welcome to the platform, {user.username}!",
        }
        create_notification(notification_data)

    except Exception as e:
        logger.error(f"[USER] Error handling user registration for {user.email}: {e}")


def handle_profile_update(user):
    """
    Handles logic related to user profile updates.

    Args:
        user (CustomUser): The user object.
    """
    try:
        # Import models dynamically to avoid AppRegistryNotReady errors
        from users.models import UserProfile

        if hasattr(user, 'profile'):
            user.profile.save()
            logger.info(f"[USER] Profile updated for user: {user.email}")

            # Optionally, notify the user about the profile update
            notification_data = {
                'sender_id': user.id,
                'sender_username': user.username,
                'receiver_id': user.id,
                'receiver_username': user.username,
                'notification_type': 'profile_update',
                'text': f"{user.username} has updated their profile.",
            }
            create_notification(notification_data)

    except Exception as e:
        logger.error(f"[USER] Error handling profile update for {user.email}: {e}")


def handle_user_deletion(user):
    """
    Handles logic related to user deletion.

    Args:
        user (CustomUser): The user object.
    """
    try:
        logger.info(f"[USER] Handling deletion for user: {user.email}")

        # Import models dynamically to avoid AppRegistryNotReady errors
        from users.models import UserProfile

        # Delete the UserProfile explicitly
        user.profile.delete()
        user.delete()
        logger.info(f"[USER] Deleted user and associated profile for: {user.email}")

    except Exception as e:
        logger.error(f"[USER] Error handling user deletion for {user.email}: {e}")
