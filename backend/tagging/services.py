# backend/tagging/services.py
import logging
from .models import TaggedItem
from notifications.services import create_notification

logger = logging.getLogger(__name__)


def process_tagging_event(data):
    """
    Processes a tagging-related event to handle tag creation, updates, or deletions.

    Args:
        data (dict): Event data containing details of the tagging event.
    """
    try:
        event_type = data.get('event_type')
        tagged_item_id = data.get('tagged_item_id')
        tagged_user_id = data.get('tagged_user_id')

        if event_type == 'created':
            # Handle tag creation event
            tagged_item = TaggedItem.objects.create(
                tagged_item_type=data.get('tagged_item_type'),
                tagged_item_id=tagged_item_id,
                tagged_user_id=tagged_user_id,
                tagged_user_username=data.get('tagged_user_username'),
                tagged_by_id=data.get('tagged_by_id'),
                tagged_by_username=data.get('tagged_by_username'),
            )
            logger.info(f"[TAGGING] Created tag: {tagged_item}")

            # Optionally trigger a notification for the user being tagged
            send_tag_notification(tagged_item)

        elif event_type == 'updated':
            # Handle tag update event (although in tagging, updates are less common)
            tagged_item = TaggedItem.objects.get(
                tagged_item_type=data.get('tagged_item_type'),
                tagged_item_id=tagged_item_id,
                tagged_user_id=tagged_user_id
            )
            tagged_item.tagged_by_id = data.get('tagged_by_id')
            tagged_item.tagged_by_username = data.get('tagged_by_username')
            tagged_item.save()
            logger.info(f"[TAGGING] Updated tag: {tagged_item}")

        elif event_type == 'deleted':
            # Handle tag deletion event
            TaggedItem.objects.filter(
                tagged_item_type=data.get('tagged_item_type'),
                tagged_item_id=tagged_item_id,
                tagged_user_id=tagged_user_id
            ).delete()
            logger.info(
                f"[TAGGING] Deleted tag on item {tagged_item_id} for user {tagged_user_id}")

        else:
            logger.warning(f"[TAGGING] Unknown event type: {event_type}")

    except TaggedItem.DoesNotExist:
        logger.error(f"[TAGGING] Tagged item does not exist with ID: {tagged_item_id}")
    except Exception as e:
        logger.error(f"[TAGGING] Error processing tagging event: {e}")


def send_tag_notification(tagged_item):
    """
    Sends a notification to the tagged user when they are tagged in a post/comment.

    Args:
        tagged_item (TaggedItem): Instance of the TaggedItem model for the newly created tag.
    """
    try:
        notification_data = {
            'sender_id': tagged_item.tagged_by_id,
            'sender_username': tagged_item.tagged_by_username,
            'receiver_id': tagged_item.tagged_user_id,
            'receiver_username': tagged_item.tagged_user_username,
            'notification_type': 'tag',
            'text': f"{tagged_item.tagged_by_username} tagged you in {tagged_item.tagged_item_type}.",
            'content_type': tagged_item.tagged_item_type,
            'object_id': tagged_item.tagged_item_id,
        }

        # Call the notification processing service
        create_notification(notification_data)
        logger.info(
            f"[TAGGING] Sent notification for tag on {tagged_item.tagged_item_type} {tagged_item.tagged_item_id}")

    except Exception as e:
        logger.error(
            f"[TAGGING] Failed to send tag notification for {tagged_item}: {e}")
