import logging
from .models import Friendship, FriendRequest
from notifications.services import create_notification

logger = logging.getLogger(__name__)


def process_friend_event(data):
    """
    Processes a friend event, which could be a new friend request, acceptance, or removal.
    """
    try:
        event_type = data.get('event')

        # Handle friend request created
        if event_type == 'friend_request_created':
            friend_request_id = data.get('friend_request_id')
            friend_request = FriendRequest.objects.get(id=friend_request_id)
            logger.info(
                f"[SERVICE] Processing friend request event for Friend Request ID: {friend_request_id}")

            notify_users_about_friend_request(friend_request)

        # Handle friend request accepted (creating friendship)
        elif event_type == 'friend_request_accepted':
            friendship_id = data.get('friendship_id')
            friendship = Friendship.objects.get(id=friendship_id)
            logger.info(
                f"[SERVICE] Processing friend request acceptance for Friendship ID: {friendship_id}")

            notify_users_about_friendship(friendship)

        # Handle friend removed
        elif event_type == 'friend_removed':
            friendship_id = data.get('friendship_id')
            friendship = Friendship.objects.get(id=friendship_id)
            logger.info(
                f"[SERVICE] Processing friend removal for Friendship ID: {friendship_id}")

            notify_users_about_friend_removal(friendship)

    except (FriendRequest.DoesNotExist, Friendship.DoesNotExist):
        logger.error(
            f"[SERVICE] Friend request or friendship does not exist for given ID.")
    except Exception as e:
        logger.error(f"[SERVICE] Error processing friend event: {e}")


def notify_users_about_friend_request(friend_request):
    """
    Notify the receiver about a new friend request.
    """
    try:
        # Notify receiver about friend request
        notification_data = {
            "sender_id": friend_request.sender_id,
            "sender_username": friend_request.sender_username,
            "receiver_id": friend_request.receiver_id,
            "receiver_username": friend_request.receiver_username,
            "notification_type": "friend_request",
            "text": f"{friend_request.sender_username} has sent you a friend request."
        }
        create_notification(notification_data)
    except Exception as e:
        logger.error(f"[NOTIFICATION] Error notifying user about friend request: {e}")


def notify_users_about_friendship(friendship):
    """
    Notify both users about the new friendship.
    """
    try:
        # Create notifications for both users
        notification_data_user1 = {
            "sender_id": friendship.user1_id,
            "sender_username": friendship.user1_username,
            "receiver_id": friendship.user2_id,
            "receiver_username": friendship.user2_username,
            "notification_type": "friend_added",
            "text": f"{friendship.user1_username} is now your friend!"
        }
        notification_data_user2 = {
            "sender_id": friendship.user2_id,
            "sender_username": friendship.user2_username,
            "receiver_id": friendship.user1_id,
            "receiver_username": friendship.user1_username,
            "notification_type": "friend_added",
            "text": f"{friendship.user2_username} is now your friend!"
        }
        create_notification(notification_data_user1)
        create_notification(notification_data_user2)
    except Exception as e:
        logger.error(f"[NOTIFICATION] Error notifying users about friendship: {e}")


def notify_users_about_friend_removal(friendship):
    """
    Notify users when a friendship is removed.
    """
    try:
        # Notify both users about friend removal
        notification_data_user1 = {
            "sender_id": friendship.user1_id,
            "sender_username": friendship.user1_username,
            "receiver_id": friendship.user2_id,
            "receiver_username": friendship.user2_username,
            "notification_type": "friend_removed",
            "text": f"You are no longer friends with {friendship.user2_username}."
        }
        notification_data_user2 = {
            "sender_id": friendship.user2_id,
            "sender_username": friendship.user2_username,
            "receiver_id": friendship.user1_id,
            "receiver_username": friendship.user1_username,
            "notification_type": "friend_removed",
            "text": f"You are no longer friends with {friendship.user1_username}."
        }
        create_notification(notification_data_user1)
        create_notification(notification_data_user2)
    except Exception as e:
        logger.error(f"[NOTIFICATION] Error notifying users about friend removal: {e}")
