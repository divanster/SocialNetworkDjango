# backend/newsfeed/services.py

import logging
from social.models import Post
from comments.models import Comment
from reactions.models import Reaction

logger = logging.getLogger(__name__)


def process_newsfeed_event(data):
    """
    Update the newsfeed based on incoming events.
    """
    try:
        event_type = data.get('event_type')
        if event_type == 'post_created':
            # Example: Add new post to the user's feed
            post = Post.objects.get(id=data.get('id'))
            # Logic to add post to feed
            logger.info(f"[NEWSFEED] Added new post to feed: {post.id}")
        elif event_type == 'comment_posted':
            comment = Comment.objects.get(id=data.get('id'))
            # Logic to add comment to feed
            logger.info(f"[NEWSFEED] Added new comment to feed: {comment.id}")
        elif event_type == 'reaction_added':
            reaction = Reaction.objects.get(id=data.get('id'))
            # Logic to add reaction to feed
            logger.info(f"[NEWSFEED] Added new reaction to feed: {reaction.id}")
        else:
            logger.warning(f"[NEWSFEED] Unknown event type: {event_type}")
    except Post.DoesNotExist:
        logger.error(f"[NEWSFEED] Post with ID {data.get('id')} does not exist.")
    except Comment.DoesNotExist:
        logger.error(f"[NEWSFEED] Comment with ID {data.get('id')} does not exist.")
    except Reaction.DoesNotExist:
        logger.error(f"[NEWSFEED] Reaction with ID {data.get('id')} does not exist.")
    except Exception as e:
        logger.error(f"[NEWSFEED] Error updating newsfeed: {e}")
