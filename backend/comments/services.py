import logging
from .models import Comment
from notifications.services import create_notification

logger = logging.getLogger(__name__)


def process_comment_event(data):
    """
    Process the comment event and trigger appropriate business logic.
    Handles creating notifications for the post author about new comments.

    Args:
        data (dict): Data containing comment information, including comment_id.
    """
    comment_id = data.get('comment_id')
    try:
        # Fetch the comment using Django's ORM, with related post details.
        comment = Comment.objects.select_related('post__user').get(id=comment_id)
        logger.info(f"[SERVICE] Processing comment event for Comment ID: {comment_id}")

        # Notify the post user about the new comment.
        notify_user_about_comment(comment)

    except Comment.DoesNotExist:
        logger.error(f"[SERVICE] Comment with ID {comment_id} does not exist.")
    except Exception as e:
        logger.error(f"[SERVICE] Error processing comment event: {e}")


def notify_user_about_comment(comment):
    """
    Send a notification to the user of the post about a new comment.

    Args:
        comment (Comment): The comment instance for which to send the notification.
    """
    try:
        # Access related fields to get the post and user details.
        post = comment.post
        post_user = post.user

        # Create a notification for the post user.
        notification_data = {
            'sender_id': comment.user.id,
            'sender_username': comment.user.username,
            'receiver_id': post_user.id,
            'receiver_username': post_user.username,
            'notification_type': 'comment',
            'text': f"{comment.user.username} commented on your post: '{comment.content[:30]}...'",
        }
        create_notification(notification_data)

        logger.info(
            f"[NOTIFICATION] Sent notification to post user {post_user.id} about comment {comment.id}"
        )

    except AttributeError as e:
        logger.error(
            f"[NOTIFICATION] AttributeError while accessing post/user related fields "
            f"for comment {comment.id}: {e}"
        )
    except Exception as e:
        logger.error(
            f"[NOTIFICATION] Failed to notify post user for comment {comment.id}: {e}"
        )
