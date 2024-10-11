from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Reaction
from .tasks import send_reaction_event_to_kafka
from notifications.models import Notification


@receiver(post_save, sender=Reaction)
def create_reaction_notification(sender, instance, created, **kwargs):
    if created:
        # Only create a notification if the reactor is not the author of the content
        if instance.user != instance.content_object.author:
            Notification.objects.create(
                sender=instance.user,
                receiver=instance.content_object.author,
                notification_type='reaction',
                text=f"{instance.user.username} reacted with {instance.emoji} on your post.",
                content_type=instance.content_type,
                object_id=instance.object_id
            )
        # Send Kafka event
        send_reaction_event_to_kafka.delay(instance.id, 'created')


@receiver(post_delete, sender=Reaction)
def delete_reaction_event(sender, instance, **kwargs):
    # Send Kafka event for reaction deletion
    send_reaction_event_to_kafka.delay(instance.id, 'deleted')
