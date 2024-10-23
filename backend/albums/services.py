import logging
from .models import Album
from notifications.services import create_notification  # Assuming this is to create notifications for users

logger = logging.getLogger(__name__)

def process_album_event(data):
    """
    Processes an album event and triggers any needed notifications.
    """
    album_id = data.get('album_id')
    try:
        album = Album.objects.get(id=album_id)
        logger.info(f"[SERVICE] Processing album event for Album ID: {album_id}")

        # Trigger notification logic, e.g., notifying followers that a new album has been posted
        notify_followers_about_album(album)

    except Album.DoesNotExist:
        logger.error(f"[SERVICE] Album with ID {album_id} does not exist.")
    except Exception as e:
        logger.error(f"[SERVICE] Error processing album event: {e}")


def notify_followers_about_album(album):
    """
    Sends a notification to followers about a new album posted.
    """
    # Assuming there is a relationship between album.user and followers
    followers = album.user.followers.all()

    for follower in followers:
        try:
            create_notification(
                sender_id=album.user.id,
                sender_username=album.user.username,
                receiver_id=follower.id,
                receiver_username=follower.username,
                notification_type='album_created',
                text=f"{album.user.username} created a new album: {album.title}"
            )
            logger.info(f"[NOTIFICATION] Notified follower {follower.id} about album {album.id}")

        except Exception as e:
            logger.error(
                f"[NOTIFICATION] Failed to notify follower {follower.id} about album {album.id}: {e}"
            )
