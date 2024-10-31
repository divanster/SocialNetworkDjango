import logging
from .models import Story
from notifications.services import create_notification  # Assuming notification is used here

logger = logging.getLogger(__name__)

def process_story_event(data):
    """
    Process a story-related event to handle updates, notifications, or any other business logic.

    Args:
        data (dict): Event data containing details of the story.
    """
    try:
        event_type = data.get('event_type')
        story_id = data.get('story_id')

        if event_type == 'created':
            # Handle story creation event
            logger.info(f"[STORY] Story created with data: {data}")
            handle_story_creation(data)  # This function should be defined below

        elif event_type == 'updated':
            # Handle story update event
            story = Story.objects.get(id=story_id)
            logger.info(f"[STORY] Story updated: {story_id}")
            update_story(story, data)  # This function should be defined below

        elif event_type == 'deleted':
            # Handle story deletion event
            story = Story.objects.get(id=story_id)
            story.delete()
            logger.info(f"[STORY] Story deleted: {story_id}")

        elif event_type == 'viewed':
            # Handle a view added to a story
            story = Story.objects.get(id=story_id)
            user_id = data.get('user_id')
            if user_id:
                story.add_view(user_id)
                logger.info(f"[STORY] Story viewed by user {user_id}: {story_id}")

        else:
            logger.warning(f"[STORY] Unknown event type: {event_type}")

    except Story.DoesNotExist:
        logger.error(f"[STORY] Story with ID {story_id} does not exist.")
    except Exception as e:
        logger.error(f"[STORY] Error processing story event: {e}")

# Define handle_story_creation
def handle_story_creation(data):
    """
    Handle additional business logic during story creation, like notifications.

    Args:
        data (dict): Event data containing details of the story.
    """
    try:
        # Placeholder for any custom logic when a story is created.
        logger.info(f"[STORY] Handling story creation for: {data}")
        # Example: Send a notification to followers
        story_id = data.get('story_id')
        story = Story.objects.get(id=story_id)
        create_notification(
            sender_id=story.user.id,
            receiver_ids=[friend.id for friend in get_friends(story.user)],
            notification_type='story_created',
            message=f"{story.user.username} created a new story: {story.content[:30]}"
        )
    except Story.DoesNotExist:
        logger.error(f"[STORY] Story with ID {story_id} not found for creation event.")
    except Exception as e:
        logger.error(f"[STORY] Error handling story creation: {e}")

# Define update_story
def update_story(story, data):
    """
    Update the story object based on the data provided.

    Args:
        story (Story): The Story instance to be updated.
        data (dict): Event data containing the updated fields.
    """
    try:
        # Update the fields if they exist in the data
        if 'content' in data:
            story.content = data['content']
        if 'media_type' in data:
            story.media_type = data['media_type']
        if 'media_url' in data:
            story.media_url = data['media_url']
        if 'is_active' in data:
            story.is_active = data['is_active']

        story.save()
        logger.info(f"[STORY] Story updated successfully with ID: {story.id}")

    except Exception as e:
        logger.error(f"[STORY] Error updating story with ID {story.id}: {e}")

# Helper function for getting friends
def get_friends(user):
    from core.utils import get_friends as get_user_friends
    return get_user_friends(user)
