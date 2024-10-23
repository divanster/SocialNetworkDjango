import logging
from .models import Follow
from notifications.services import create_notification

logger = logging.getLogger(__name__)


def process_follow_event(data):
    """
    Processes a follow event to trigger notification logic.
    """
    follow_id = data.get('follow_id')
    try:
        follow = Follow.objects.get(id=follow_id)
        logger.info(f"[SERVICE] Processing follow event for Follow ID: {follow_id}")

        # Notify the followed user
        notify_user_about_follow(follow)

    except Follow.DoesNotExist:
        logger.error(f"[SERVICE] Follow with ID {follow_id} does not exist.")
    except Exception as e:
        logger.error(f"[SERVICE] Error processing follow event: {e}")


def notify_user_about_follow(follow):
    """
    Sends a notification to the followed user.
    """
    try:
        create_notification(
            sender_id=follow.follower.id,
            sender_username=follow.follower.username,
            receiver_id=follow.followed.id,
            receiver_username=follow.followed.username,
            notification_type='follow',
            text=f"{follow.follower.username} started following you."
        )
        logger.info(
            f"[NOTIFICATION] Notification created for user {follow.followed.id} about follow by {follow.follower.id}")

    except Exception as e:
        logger.error(
            f"[NOTIFICATION] Failed to notify user {follow.followed.id} about follow by {follow.follower.id}: {e}")
