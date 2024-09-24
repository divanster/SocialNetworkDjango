from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging
from django.core.exceptions import ObjectDoesNotExist

# Initialize logger
logger = logging.getLogger(__name__)

@receiver(post_save, sender=CustomUser)
def handle_user_post_save(sender, instance, created, **kwargs):
    """
    Signal handler to create or update UserProfile and send user updates via channels.
    """
    # Ensure UserProfile creation or update
    if created:
        try:
            # Create the UserProfile when a new CustomUser instance is created
            UserProfile.objects.create(user=instance)
            logger.info(f"UserProfile created for user: {instance.username}")
        except Exception as e:
            logger.error(f"Error creating UserProfile for user {instance.username}: {str(e)}")
    else:
        try:
            # Save the existing profile if it exists, or create one if it doesn't
            if hasattr(instance, 'profile'):
                instance.profile.save()
            else:
                UserProfile.objects.create(user=instance)
                logger.info(f"UserProfile created for existing user: {instance.username}")
        except ObjectDoesNotExist:
            # Create the UserProfile if it doesn't exist
            UserProfile.objects.create(user=instance)
            logger.warning(f"UserProfile was missing and created for user: {instance.username}")
        except Exception as e:
            logger.error(f"Error updating UserProfile for user {instance.username}: {str(e)}")

    # Send user update to channel group
    channel_layer = get_channel_layer()
    if channel_layer is not None:
        try:
            user_data = {
                'id': instance.id,
                'username': instance.username,
                'email': instance.email,
                'first_name': instance.profile.first_name if hasattr(instance, 'profile') else '',
                'last_name': instance.profile.last_name if hasattr(instance, 'profile') else '',
                # Add more user fields as needed
            }

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
            logger.error(f"Error in sending user update for {instance.username}: {str(e)}")
    else:
        logger.warning("Channel layer is not available. Cannot send user update.")
