# backend/tagging/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from tagging.models import TaggedItem
from notifications.models import Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .tasks import send_tagging_event_to_kafka
from django.db.models.signals import pre_delete


import logging

logger = logging.getLogger(__name__)


# Helper function to send real-time notifications for tags
def send_tag_real_time_notification(user_id, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'tag_notifications_{user_id}',
        {
            'type': 'tag_notification',
            'message': message
        }
    )


@receiver(post_save, sender=TaggedItem)
def tagged_item_created(sender, instance, created, **kwargs):
    if created:
        # Create a notification for the tagged user
        Notification.objects.create(
            sender=instance.tagged_by,
            receiver=instance.tagged_user,
            notification_type='tag',
            text=f"You were tagged by {instance.tagged_by.username} in a post.",
            content_type=instance.content_type,
            object_id=instance.object_id
        )

        # Send a real-time notification
        send_tag_real_time_notification(
            instance.tagged_user.id,
            f"You were tagged by {instance.tagged_by.username} in a post."
        )

        # Trigger Celery task to send the tagging event to Kafka
        send_tagging_event_to_kafka.delay(instance.id, 'created')

        logger.info(f"TaggedItem created: {instance}")


@receiver(post_delete, sender=TaggedItem)
def tagged_item_deleted(sender, instance, **kwargs):
    # Notify the tagged user that the tag has been removed
    send_tag_real_time_notification(
        instance.tagged_user.id,
        f"You were untagged from a post by {instance.tagged_by.username}."
    )

    # Trigger Celery task to send the tagging event to Kafka
    send_tagging_event_to_kafka.delay(instance.id, 'deleted')

    logger.info(f"TaggedItem deleted: {instance}")


@receiver(pre_delete, sender=TaggedItem)
def handle_generic_foreign_key_delete(sender, instance, **kwargs):
    content_object = instance.content_object
    if content_object and hasattr(content_object, 'is_deleted') and content_object.is_deleted:
        instance.delete()


@receiver(post_delete, sender=TaggedItem)
def handle_orphaned_tags(sender, instance, **kwargs):
    # Remove tags where the related content is soft deleted or deleted
    if not instance.content_object:
        instance.delete()
