import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from users.models import CustomUser, UserProfile
from .tasks import process_user_event_task  # Import the Celery task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from websocket.consumers import \
    GeneralKafkaConsumer  # Import for generating group names

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a UserProfile when a CustomUser is first created,
    or send update events if the user is updated.
    """
    if created:
        # User was just created
        profile, profile_created = UserProfile.objects.get_or_create(user=instance)
        if profile_created:
            logger.info(f"UserProfile created for new user with ID {instance.id}")
        else:
            logger.info(f"UserProfile already existed for user with ID {instance.id}")

        # Trigger a Celery task for user creation
        process_user_event_task.delay(instance.id, 'created')

        # Send WebSocket notification for the new user
        user_group_name = GeneralKafkaConsumer.generate_group_name(instance.id)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'user_notification',
                'message': f"Welcome to the platform, {instance.username}!",
                'event': 'created',
                'user_id': str(instance.id),
                'username': instance.username,
            }
        )
        logger.info(
            f"Real-time WebSocket notification sent for user created with ID {instance.id}"
        )
    else:
        # Ensure the profile exists (create if missing)
        profile, profile_created = UserProfile.objects.get_or_create(user=instance)
        if profile_created:
            logger.info(f"UserProfile was missing and created for user ID {instance.id}")

        # Trigger Celery task for user update
        process_user_event_task.delay(instance.id, 'updated')
        logger.info(f"UserProfile updated for user ID {instance.id}")


@receiver(post_delete, sender=CustomUser)
def delete_user_profile(sender, instance, **kwargs):
    """
    Signal to delete the UserProfile when a CustomUser instance is deleted,
    and send the deletion event details to Kafka.
    """
    if hasattr(instance, 'profile'):
        instance.profile.delete()
        logger.info(f"UserProfile deleted for user with ID {instance.id}")

    # Trigger Celery task to handle the user deletion event
    process_user_event_task.delay(instance.id, 'deleted_user')

    # Send WebSocket notification for user deletion
    user_group_name = GeneralKafkaConsumer.generate_group_name(instance.id)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        user_group_name,
        {
            'type': 'user_notification',
            'message': "Your account has been successfully deleted.",
            'event': 'deleted_user',
            'user_id': str(instance.id),
            'username': instance.username,
        }
    )
    logger.info(
        f"Real-time WebSocket notification sent for user deletion with ID {instance.id}"
    )
