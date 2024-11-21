# backend/social/services.py
import logging
from django.db.models import Q
from social.models import Post  # Import Post model if needed
from comments.models import Comment
from reactions.models import Reaction
from django.contrib.auth import get_user_model
from notifications.services import create_notification  # Importing notification service

User = get_user_model()
logger = logging.getLogger(__name__)

def process_social_event(data):
    """
    Processes a social action event for further business logic.
    Args:
        data (dict): A dictionary with the event data to process.
    """
    try:
        action_type = data.get('action_type')
        if action_type == 'post_created':
            process_post_created(data)
        elif action_type == 'comment_posted':
            process_comment_posted(data)
        elif action_type == 'reaction_added':
            process_reaction_added(data)
        else:
            logger.warning(f"[SERVICE] Unknown social action type: {action_type}")
    except Exception as e:
        logger.error(f"[SERVICE] Error processing social event: {e}")

def process_post_created(data):
    """
    Handles the creation of a post, including visibility handling and notifications.
    """
    try:
        post_id = data.get('post_id')
        post = Post.objects.get(id=post_id)
        logger.info(f"[SERVICE] Post Created: {post.title}")

        # If the post is public, notify everyone.
        if post.visibility == 'public':
            notify_users(post, User.objects.exclude(id=post.author.id))  # Notify everyone except the author

        # If the post is for friends, notify only friends.
        elif post.visibility == 'friends':
            friends = post.author.friends.all()  # Assuming `friends` is a related manager.
            notify_users(post, friends)

        # Private posts should not trigger notifications to others
        elif post.visibility == 'private':
            logger.info(f"[SERVICE] Private post created by user: {post.author.id} - No notifications sent.")

    except Post.DoesNotExist:
        logger.error(f"[SERVICE] Post with ID {data.get('post_id')} does not exist.")
    except Exception as e:
        logger.error(f"[SERVICE] Error processing post created event: {e}")

def process_comment_posted(data):
    """
    Handles the posting of a comment and any notifications needed.
    """
    try:
        comment_id = data.get('comment_id')
        comment = Comment.objects.get(id=comment_id)
        post = comment.post

        if post.visibility == 'public':
            # Notify post author
            if post.author != comment.user:
                notify_users(comment, [post.author])
            logger.info(f"[SERVICE] Public comment on post ID {post.id} by user {comment.user.id}")

        elif post.visibility == 'friends':
            # Only notify the post author if they are a friend
            if post.author != comment.user and post.author in comment.user.friends.all():
                notify_users(comment, [post.author])
            logger.info(f"[SERVICE] Friend's post commented by user {comment.user.id}")

        elif post.visibility == 'private':
            logger.info(f"[SERVICE] Comment added to private post - No notifications sent.")

    except Comment.DoesNotExist:
        logger.error(f"[SERVICE] Comment with ID {data.get('comment_id')} does not exist.")
    except Exception as e:
        logger.error(f"[SERVICE] Error processing comment posted event: {e}")

def process_reaction_added(data):
    """
    Handles the addition of a reaction to a post or comment.
    """
    try:
        reaction_id = data.get('reaction_id')
        reaction = Reaction.objects.get(id=reaction_id)
        reacted_item = reaction.reacted_item

        if reacted_item.visibility == 'public':
            # Notify the author of the reacted item
            if reacted_item.author != reaction.user:
                notify_users(reaction, [reacted_item.author])
            logger.info(f"[SERVICE] Reaction {reaction.emoji} added to public item ID {reacted_item.id}")

        elif reacted_item.visibility == 'friends':
            # Notify the author if they are a friend
            if reacted_item.author != reaction.user and reacted_item.author in reaction.user.friends.all():
                notify_users(reaction, [reacted_item.author])
            logger.info(f"[SERVICE] Reaction added by friend to item ID {reacted_item.id}")

        elif reacted_item.visibility == 'private':
            logger.info(f"[SERVICE] Reaction added to private item - No notifications "
                        f"sent.")

    except Reaction.DoesNotExist:
        logger.error(f"[SERVICE] Reaction with ID {data.get('reaction_id')} does not exist.")
    except Exception as e:
        logger.error(f"[SERVICE] Error processing reaction added event: {e}")

def notify_users(event_object, users):
    """
    Sends notifications to the list of users about a specific event.

    Args:
        event_object: The object (post/comment/reaction) related to the event.
        users (iterable): List of users to be notified.
    """
    sender = event_object.author if hasattr(event_object, 'author') else event_object.user

    for user in users:
        try:
            # Creating a notification for each user
            create_notification(
                sender_id=sender.id,
                sender_username=sender.username,
                receiver_id=user.id,
                receiver_username=user.username,
                notification_type='social_event',
                text=f"{sender.username} has added a new action on the post: {event_object.title if hasattr(event_object, 'title') else ''}"
            )
            logger.info(f"[NOTIFICATION] Notified user {user.id} about event on item ID {event_object.id}")

        except Exception as e:
            logger.error(f"[NOTIFICATION] Failed to notify user {user.id} about event: {e}")
