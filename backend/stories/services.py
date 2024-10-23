# backend/stories/services.py
import logging
from .models import Story

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
            handle_story_creation(data)

        elif event_type == 'updated':
            # Handle story update event
            story = Story.objects.get(id=story_id)
            logger.info(f"[STORY] Story updated: {story_id}")
            update_story(story, data)

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

def handle_story_creation(data):
    """
    Handle additional business logic during story creation, like notifications.

    Args:
        data (dict): Event data containing details of the story.
    """
    # Placeholder for any custom logic when a story is created.
    logger.info(f"[STORY] Handling story creation for: {data}")
    # Add logic such as sending notifications or analytics tracking, etc.

def update_story(story, data):
    """
    Update the story object based on the data provided.

    Args:
        story (Story): The Story instance to be updated.
        data (dict): Event data containing the updated fields.
    """
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
