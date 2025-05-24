# backend/albums/services.py

import logging
from albums.models import Album  # Import from the correct file for the Album model
from notifications.services import create_notification  # Assuming this is to create notifications for users
from core.choices import VisibilityChoices  # Import visibility choices for checking visibility
from django.db import models

logger = logging.getLogger(__name__)


def process_album_event(data):
    """
    Processes an album event and triggers any needed notifications.
    Args:
        data (dict): Event data containing details about the album and the type of event.
    """
    album_id = data.get('album_id')
    try:
        # Use `.objects.get()` to retrieve the Album using Django ORM.
        album = Album.objects.get(pk=album_id)

        logger.info(f"[SERVICE] Processing album event for Album ID: {album_id}")

        # Trigger notification logic, e.g., notifying followers that a new album has
        # been posted
        if album.visibility != VisibilityChoices.PRIVATE:
            notify_followers_about_album(album)
        else:
            logger.info(f"[SERVICE] Album {album_id} is private. No notifications will be sent.")

    except Album.DoesNotExist:
        logger.error(f"[SERVICE] Album with ID {album_id} does not exist.")
    except Exception as e:
        logger.error(f"[SERVICE] Error processing album event for Album ID {album_id}: {e}")


def notify_followers_about_album(album):
    """
    Sends a notification to followers about a new album posted.
    Args:
        album (Album): Album instance for which to send notifications.
    """
    # Assuming there is a ManyToMany relationship or ForeignKey relationship set up for followers.
    user = album.user

    # Retrieve followers - adjust to match the actual follower model relationship
    followers = getattr(user, 'followers', None)

    if followers is not None:
        # Iterate through followers and send notifications for public or friends-only albums
        for follower in followers.all():  # Use `.all()` to iterate through followers in Django ORM.
            try:
                # Only send notification if the follower has access based on album visibility
                if album.visibility == VisibilityChoices.PUBLIC or (album.visibility == VisibilityChoices.FRIENDS and is_friend(user, follower)):
                    create_notification({
                        'sender_id': user.id,
                        'sender_username': user.username,
                        'receiver_id': follower.id,
                        'receiver_username': follower.username,
                        'notification_type': 'album_created',
                        'text': f"{user.username} created a new album: {album.title}"
                    })
                    logger.info(f"[NOTIFICATION] Notified follower {follower.id} about album {album.id}")
                else:
                    logger.info(f"[NOTIFICATION] Follower {follower.id} cannot view album {album.id} due to visibility settings.")

            except Exception as e:
                logger.error(f"[NOTIFICATION] Failed to notify follower {follower.id} about album {album.id}: {e}")
    else:
        logger.warning(f"[NOTIFICATION] No followers found for user {user.id}")


def is_friend(user1, user2):
    """
    Checks if two users are friends.
    Args:
        user1 (User): The first user.
        user2 (User): The second user.
    Returns:
        bool: True if user1 and user2 are friends, False otherwise.
    """
    from friends.models import Friendship

    # Check if a friendship exists between user1 and user2
    return Friendship.objects.filter(
        (models.Q(user1=user1) & models.Q(user2=user2)) |
        (models.Q(user1=user2) & models.Q(user2=user1))
    ).exists()
