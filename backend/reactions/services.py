# backend/reactions/services.py
import logging
from .models import Reaction
from notifications.services import create_notification

logger = logging.getLogger(__name__)


def process_reaction_event(data):
    """
    Processes a reaction event for further business logic.
    """
    reaction_id = data.get('reaction_id')
    try:
        reaction = Reaction.objects.get(id=reaction_id)
        logger.info(
            f"[SERVICE] Processing reaction event for Reaction ID: {reaction_id}")

        # Notify the user who owns the content about the reaction
        if reaction.content_object:
            notify_user_about_reaction(reaction)

    except Reaction.DoesNotExist:
        logger.error(f"[SERVICE] Reaction with ID {reaction_id} does not exist.")
    except Exception as e:
        logger.error(f"[SERVICE] Error processing reaction event: {e}")


def notify_user_about_reaction(reaction):
    """
    Notify the user about the new reaction.
    """
    try:
        notification_data = {
            "sender_id": reaction.user.id,
            "sender_username": reaction.user.username,
            "receiver_id": reaction.content_object.user.id,
            "receiver_username": reaction.content_object.user.username,
            "notification_type": "reaction",
            "text": f"{reaction.user.username} reacted to your post."
        }
        create_notification(notification_data)
    except Exception as e:
        logger.error(f"[NOTIFICATION] Error notifying user about reaction: {e}")
