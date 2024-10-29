import logging
from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def create_notification(data):
    """
    Processes a notification event.
    This function is used to handle the creation of notifications for various event types.
    Args:
        data (dict): A dictionary containing event data, such as sender, receiver, notification type, etc.
    """
    try:
        # Extract required fields from the data dictionary
        sender_id = data.get('sender_id')
        sender_username = data.get('sender_username')
        receiver_id = data.get('receiver_id')
        receiver_username = data.get('receiver_username')
        notification_type = data.get('notification_type')
        text = data.get('text', '')
        content_type = data.get('content_type')
        object_id = data.get('object_id')

        # Ensure all required fields are present
        if not sender_id or not receiver_id or not notification_type:
            logger.warning(
                "[NOTIFICATION] Missing required fields for notification creation."
            )
            return

        # Prevent self-notification
        if sender_id == receiver_id:
            logger.info(
                f"[NOTIFICATION] Skipping notification creation since sender and "
                f"receiver are the same: {sender_id}"
            )
            return

        # Optionally, check if a similar notification already exists This is useful
        # to avoid creating duplicate notifications for repetitive actions.
        existing_notification = Notification.objects.filter(
            sender_id=sender_id,
            receiver_id=receiver_id,
            notification_type=notification_type,
            content_type=content_type,
            object_id=object_id,
            is_read=False  # Only check unread notifications
        ).exists()

        if existing_notification:
            logger.info(
                f"[NOTIFICATION] Duplicate notification detected for receiver {receiver_id}, type {notification_type}. Skipping creation."
            )
            return

        # Create a new notification object
        notification = Notification.objects.create(
            sender_id=sender_id,
            sender_username=sender_username,
            receiver_id=receiver_id,
            receiver_username=receiver_username,
            notification_type=notification_type,
            text=text,
            content_type=content_type,
            object_id=object_id,
        )

        logger.info(
            f"[NOTIFICATION] Created notification for user {receiver_id} about {notification_type} event."
        )

        # Optionally, send a push notification to the user's mobile device or
        # frontend app
        send_push_notification(
            user_id=receiver_id,
            title="New Notification",
            message=text,
            data={'notification_id': str(notification.id)}
        )

    except Exception as e:
        logger.error(f"[NOTIFICATION] Error creating notification: {e}")


def send_push_notification(user_id, title, message, data=None):
    """
    Sends a push notification to the user.
    In a real-world implementation, this would integrate with a push notification service.
    Args:
        user_id (int): ID of the user to send the push notification to.
        title (str): Title of the notification.
        message (str): Message body of the notification.
        data (dict, optional): Additional data to send with the notification.
    """
    try:
        # Here we would normally integrate with a push notification service like
        # Firebase Cloud Messaging (FCM) or Apple Push Notification Service (APNS).
        # For now, we will just log this action.

        # Example: push_service.send_notification(user_id=user_id, title=title,
        # message=message, data=data)

        logger.info(
            f"[PUSH NOTIFICATION] Sent push notification to user {user_id} with title '{title}' and message '{message}'."
        )
    except Exception as e:
        logger.error(
            f"[PUSH NOTIFICATION] Failed to send push notification to user {user_id}: {e}"
        )
