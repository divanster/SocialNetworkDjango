# backend/users/services.py

import logging
from .models import CustomUser, UserProfile
from notifications.services import create_notification

logger = logging.getLogger(__name__)


def process_user_event(data):
    """
    Processes user events to handle user profile updates, registrations, etc.

    Args:
        data (dict): Event data containing user-related information.
    """
    try:
        event_type = data.get('event_type')
        user_id = data.get('user_id')

        if event_type == 'user_registered':
            # Logic for handling new user registration
            logger.info(f"[USER] New user registered with ID: {user_id}")
            handle_user_registration(user_id)

        elif event_type == 'profile_updated':
            # Logic for handling profile updates
            logger.info(f"[USER] Profile updated for user with ID: {user_id}")
            handle_profile_update(user_id)

        elif event_type == 'user_deleted':
            # Logic for handling user deletion
            logger.info(f"[USER] User deleted with ID: {user_id}")
            handle_user_deletion(user_id)

        else:
            logger.warning(f"[USER] Unknown event type: {event_type}")

    except CustomUser.DoesNotExist:
        logger.error(f"[USER] User with ID {user_id} does not exist.")
    except Exception as e:
        logger.error(f"[USER] Error processing user event: {e}")


def handle_user_registration(user_id):
    """
    Handles logic related to new user registration.

    Args:
        user_id: ID of the newly registered user.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        logger.info(f"[USER] Handling registration for user: {user.email}")

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

    except CustomUser.DoesNotExist:
        logger.error(
            f"[USER] Cannot create UserProfile, user with ID {user_id} does not exist.")
    except Exception as e:
        logger.error(f"[USER] Error handling user registration: {e}")


def handle_profile_update(user_id):
    """
    Handles logic related to user profile updates.

    Args:
        user_id: ID of the user whose profile was updated.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        profile = user.profile
        logger.info(f"[USER] Profile updated for user: {user.email}")

        # Optionally, notify followers about profile updates (if needed)
        notification_data = {
            'sender_id': user.id,
            'sender_username': user.username,
            'receiver_id': user.id,
            'receiver_username': user.username,
            'notification_type': 'profile_update',
            'text': f"{user.username} has updated their profile.",
        }
        create_notification(notification_data)

    except CustomUser.DoesNotExist:
        logger.error(f"[USER] User with ID {user_id} does not exist.")
    except Exception as e:
        logger.error(f"[USER] Error processing profile update for user {user_id}: {e}")


def handle_user_deletion(user_id):
    """
    Handles logic related to user deletion.

    Args:
        user_id: ID of the user being deleted.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        logger.info(f"[USER] Handling deletion for user: {user.email}")

        # Delete the UserProfile (cascade delete handles this usually, but doing it explicitly for logic clarity)
        user.profile.delete()
        user.delete()
        logger.info(f"[USER] Deleted user and associated profile for: {user.email}")

    except CustomUser.DoesNotExist:
        logger.error(f"[USER] User with ID {user_id} does not exist.")
    except Exception as e:
        logger.error(f"[USER] Error handling user deletion for user {user_id}: {e}")
