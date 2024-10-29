import logging
from .models import Page
from notifications.services import create_notification

logger = logging.getLogger(__name__)


def process_page_event(data):
    """
    Processes a page event for further business logic.
    This can include updating information, triggering notifications, etc.

    Args:
        data (dict): Event data containing information related to the page.
    """
    page_id = data.get('page_id')
    event_type = data.get('event_type')

    try:
        # Depending on the event type, handle the page event accordingly
        if event_type == 'created':
            handle_page_created(data)
        elif event_type == 'updated':
            handle_page_updated(page_id, data)
        elif event_type == 'deleted':
            handle_page_deleted(page_id)
        else:
            logger.warning(f"[PAGE SERVICE] Unknown event type: {event_type}")

    except Page.DoesNotExist:
        logger.error(f"[PAGE SERVICE] Page with ID {page_id} does not exist.")
    except Exception as e:
        logger.error(f"[PAGE SERVICE] Error processing page event: {e}")


def handle_page_created(data):
    """
    Handles page creation event.

    Args:
        data (dict): Event data containing information about the page.
    """
    try:
        # Create the Page object
        page = Page.objects.create(
            id=data['page_id'],
            title=data['title'],
            content=data.get('content', ''),
            author_id=data['created_by_user_id']
        )
        logger.info(f"[PAGE SERVICE] Created Page with ID {page.id}")

        # Notify followers or other users about the new page
        notification_data = {
            'sender_id': data['created_by_user_id'],
            'sender_username': data['created_by_user_username'],
            'receiver_id': data['target_user_id'],
            # Assuming that there's a target user who will get notified
            'receiver_username': data['target_user_username'],
            'notification_type': 'page_created',
            'text': f"New page '{data['title']}' has been created by {data['created_by_user_username']}.",
            'content_type': 'page',
            'object_id': data['page_id']
        }
        create_notification(notification_data)

    except Exception as e:
        logger.error(f"[PAGE SERVICE] Error creating page: {e}")


def handle_page_updated(page_id, data):
    """
    Handles page update event.

    Args:
        page_id (str): The ID of the page being updated.
        data (dict): Event data containing information about the page update.
    """
    try:
        page = Page.objects.get(id=page_id)
        page.title = data.get('title', page.title)
        page.content = data.get('content', page.content)
        page.save()
        logger.info(f"[PAGE SERVICE] Updated Page with ID {page_id}")

        # Notify followers or other users about the page update (if needed)
        notification_data = {
            'sender_id': data['updated_by_user_id'],
            'sender_username': data['updated_by_user_username'],
            'receiver_id': data['target_user_id'],
            # Assuming there's a user that gets notified
            'receiver_username': data['target_user_username'],
            'notification_type': 'page_updated',
            'text': f"Page '{data['title']}' has been updated by {data['updated_by_user_username']}.",
            'content_type': 'page',
            'object_id': page_id
        }
        create_notification(notification_data)

    except Page.DoesNotExist:
        logger.error(
            f"[PAGE SERVICE] Page with ID {page_id} does not exist for update.")
    except Exception as e:
        logger.error(f"[PAGE SERVICE] Error updating page with ID {page_id}: {e}")


def handle_page_deleted(page_id):
    """
    Handles page deletion event.

    Args:
        page_id (str): The ID of the page being deleted.
    """
    try:
        page = Page.objects.get(id=page_id)
        page.delete()
        logger.info(f"[PAGE SERVICE] Deleted Page with ID {page_id}")

        # Notify users about the page deletion (if needed)
        notification_data = {
            'sender_id': 'system',  # System could be the sender since it’s deleted
            'sender_username': 'System',
            'receiver_id': page.author_id,  # Assuming notifying the creator
            'receiver_username': page.author.username,
            'notification_type': 'page_deleted',
            'text': f"Page '{page.title}' has been deleted.",
            'content_type': 'page',
            'object_id': page_id
        }
        create_notification(notification_data)

    except Page.DoesNotExist:
        logger.error(
            f"[PAGE SERVICE] Page with ID {page_id} does not exist for deletion.")
    except Exception as e:
        logger.error(f"[PAGE SERVICE] Error deleting page with ID {page_id}: {e}")
