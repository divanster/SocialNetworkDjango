import logging
from .models import Comment
from notifications.services import create_notification

logger = logging.getLogger(__name__)


def process_comment_event(data):
    """
    Process the comment event and trigger appropriate business logic.
    """
    comment_id = data.get('comment_id')
    try:
        comment = Comment.objects.get(id=comment_id)
        logger.info(f"[SERVICE] Processing comment event for Comment ID: {comment_id}")

        # Notify the post author that a new comment has been posted
        notify_user_about_comment(comment.post_id, comment)

    except Comment.DoesNotExist:
        logger.error(f"[SERVICE] Comment with ID {comment_id} does not exist.")
    except Exception as e:
        logger.error(f"[SERVICE] Error processing comment event: {e}")


def notify_user_about_comment(post_id, comment):
    """
    Send a notification to the author of the post about a new comment.
    """
    try:
        post_author_id = comment.post.user_id
        create_notification(
            sender_id=comment.user_id,
            sender_username=comment.user_username,
            receiver_id=post_author_id,
            receiver_username=comment.post.user.username,
            notification_type='comment',
            text=f"{comment.user_username} commented on your post."
        )
    except Exception as e:
        logger.error(
            f"[NOTIFICATION] Failed to notify post author for comment {comment.id}: {e}")
