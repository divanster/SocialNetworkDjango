# backend/tagging/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from tagging.models import TaggedItem
from notifications.models import Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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
        print(f'TaggedItem created: {instance}')

@receiver(post_delete, sender=TaggedItem)
def tagged_item_deleted(sender, instance, **kwargs):
    # Notify the tagged user that the tag has been removed
    send_tag_real_time_notification(
        instance.tagged_user.id,
        f"You were untagged from a post by {instance.tagged_by.username}."
    )
    print(f'TaggedItem deleted: {instance}')
