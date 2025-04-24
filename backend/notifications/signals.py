import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Notification
from .serializers import NotificationSerializer
from kafka_app.tasks.notification_tasks import process_notification_event_task
from kafka_app.constants import NOTIFICATION_CREATED, NOTIFICATION_UPDATED, NOTIFICATION_DELETED

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notification)
def notification_saved(sender, instance, created, **kwargs):
    """
    Signal to handle notification creation and updates.
    Triggers a Celery task to process the event, and on create also broadcasts
    the new Notification via Django Channels.
    """
    # 1) send to Kafka/Celery as you already do
    if instance.is_deleted:
        event_type = NOTIFICATION_DELETED
    else:
        event_type = NOTIFICATION_CREATED if created else NOTIFICATION_UPDATED

    try:
        process_notification_event_task.delay(str(instance.id), event_type)
        logger.debug(
            f"Triggered Celery task for notification {event_type} event with ID {instance.id}"
        )
    except Exception as e:
        logger.error(
            f"Failed to trigger Celery task for notification {event_type} event with ID {instance.id}: {e}"
        )

    # 2) ALSO broadcast via Channels on NEW notifications
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.receiver_id}",    # per-user group
            {
                "type":    "notify",           # invokes notify() in consumer
                "event":   "notification",     # client sees { type, data }
                "payload": NotificationSerializer(instance).data,
            },
        )


@receiver(post_delete, sender=Notification)
def notification_deleted(sender, instance, **kwargs):
    """
    Signal to handle notification deletions (if you care to push deletes).
    """
    try:
        process_notification_event_task.delay(str(instance.id), NOTIFICATION_DELETED)
        logger.debug(
            f"Triggered Celery task for notification deleted event with ID {instance.id}"
        )
    except Exception as e:
        logger.error(
            f"Failed to trigger Celery task for notification deleted event with ID {instance.id}: {e}"
        )
