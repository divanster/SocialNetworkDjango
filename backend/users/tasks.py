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
            'sender_username': 'System',  # You could use a system sender
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
        send_welcome_email.delay(user.id)  # Trigger the welcome email task

    except Exception as e:
        logger.error(f"[USER] Error handling user registration for {user.email}: {e}")


def handle_profile_update(user):
    """
    Handles logic related to user profile updates.

    Args:
        user (CustomUser): The user object.
    """
    try:
        if hasattr(user, 'profile'):
            user.profile.save()
            logger.info(f"[USER] Profile updated for user: {user.email}")

            # Optionally, trigger a notification to inform about the profile update
            send_profile_update_notification.delay(user.id)  # Trigger the profile update notification task

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
