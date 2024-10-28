import logging
from albums.models import Album  # Import from the correct file for the Album model
from notifications.services import create_notification  # Assuming this is to create notifications for users

logger = logging.getLogger(__name__)


def process_album_event(data):
    """
    Processes an album event and triggers any needed notifications.
    """
    album_id = data.get('album_id')
    try:
        # Use `.objects.get()` to retrieve the Album using Django ORM.
        album = Album.objects.get(pk=album_id)
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
    # Assuming that there is a relationship between album.user and followers.
    # Adjust to ensure that `user` has a related set of `followers`.
    user = album.user

    # Assuming there is a ManyToMany relationship or ForeignKey relationship set up for followers.
    followers = getattr(user, 'followers', None)

    if followers is not None:
        # Assuming followers is a related queryset-like iterable.
        for follower in followers.all():  # Use `.all()` to iterate through followers in Django ORM.
            try:
                create_notification(
                    sender_id=user.id,
                    sender_username=user.username,  # Adjusted field to work with Django ORM.
                    receiver_id=follower.id,
                    receiver_username=follower.username,
                    notification_type='album_created',
                    text=f"{user.username} created a new album: {album.title}"
                )
                logger.info(
                    f"[NOTIFICATION] Notified follower {follower.id} about album {album.id}")

            except Exception as e:
                logger.error(
                    f"[NOTIFICATION] Failed to notify follower {follower.id} about album {album.id}: {e}"
                )
    else:
        logger.warning(f"[NOTIFICATION] No followers found for user {user.id}")
