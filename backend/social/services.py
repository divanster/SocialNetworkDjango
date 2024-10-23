# backend/social/services.py
import logging
from social.models import Post  # Import Post model if you need it
from comments.models import Comment
from reactions.models import Reaction

logger = logging.getLogger(__name__)

def process_social_event(data):
    """
    Processes a social action event for further business logic.
    """
    try:
        action_type = data.get('action_type')
        if action_type == 'post_created':
            # Example of processing a post creation
            post_id = data.get('post_id')
            post = Post.objects.get(id=post_id)
            logger.info(f"[SERVICE] Post Created: {post.title}")
        elif action_type == 'comment_posted':
            comment_id = data.get('comment_id')
            comment = Comment.objects.get(id=comment_id)
            logger.info(f"[SERVICE] Comment Posted: {comment.content}")
        elif action_type == 'reaction_added':
            reaction_id = data.get('reaction_id')
            reaction = Reaction.objects.get(id=reaction_id)
            logger.info(f"[SERVICE] Reaction Added: {reaction.emoji} to item {reaction.reacted_item_type}")
        else:
            logger.warning(f"[SERVICE] Unknown social action type: {action_type}")
    except Exception as e:
        logger.error(f"[SERVICE] Error processing social event: {e}")
