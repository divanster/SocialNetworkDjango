import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from users.models import UserProfile
from users.serializers import CustomUserSerializer

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User)
def handle_user_post_save(sender, instance, created, **kwargs):
    """
    Signal handler to create or update UserProfile and send user updates via channels.
    """
    # Ensure UserProfile creation or update
    if created:
        try:
            UserProfile.objects.create(user=instance)
            logger.info(f"UserProfile created for user: {instance.username}")
        except Exception as e:
            logger.error(
                f"Error creating UserProfile for user {instance.username}: {str(e)}")
    else:
        try:
            if hasattr(instance, 'profile'):
                instance.profile.save()
            else:
                UserProfile.objects.create(user=instance)
                logger.info(
                    f"UserProfile created for existing user: {instance.username}")
        except ObjectDoesNotExist:
            UserProfile.objects.create(user=instance)
            logger.warning(
                f"UserProfile was missing and created for user: {instance.username}")
        except Exception as e:
            logger.error(
                f"Error updating UserProfile for user {instance.username}: {str(e)}")

    # Send user update to channel group
    channel_layer = get_channel_layer()
    if channel_layer is not None:
        try:
            serializer = CustomUserSerializer(instance)
            user_data = serializer.data

            event_type = 'new_user' if created else 'update_user'

            async_to_sync(channel_layer.group_send)(
                'users',
                {
                    'type': event_type,
                    'user': user_data
                }
            )
            logger.info(f"Sent {event_type} event for user: {instance.username}")
        except Exception as e:
            logger.error(
                f"Error in sending user update for {instance.username}: {str(e)}")
    else:
        logger.warning("Channel layer is not available. Cannot send user update.")
