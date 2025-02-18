# backend/reactions/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Reaction
from kafka_app.tasks.reaction_tasks import process_reaction_event_task  # Updated import
from notifications.models import Notification
import logging

from kafka_app.constants import (
    REACTION_CREATED,
    REACTION_DELETED,
    REACTION_EVENTS
)

logger = logging.getLogger(__name__)


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
        # Trigger the Celery task for Kafka event
        process_reaction_event_task.delay(str(instance.id), REACTION_CREATED)
        logger.info(
            f"Triggered Celery task for created reaction event with ID {instance.id}"
        )


@receiver(post_delete, sender=Reaction)
def delete_reaction_event(sender, instance, **kwargs):
    # Trigger the Celery task for Kafka event on deletion
    process_reaction_event_task.delay(str(instance.id), REACTION_DELETED)
    logger.info(
        f"Triggered Celery task for deleted reaction event with ID {instance.id}"
    )
