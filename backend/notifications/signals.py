# backend/notifications/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Notification
from .tasks import send_notification_event_to_kafka  # Import the Celery task


@receiver(post_save, sender=Notification)
def notification_saved(sender, instance, created, **kwargs):
    if created:
        send_notification_event_to_kafka.delay(instance.id, 'created')
    else:
        send_notification_event_to_kafka.delay(instance.id, 'updated')


@receiver(post_delete, sender=Notification)
def notification_deleted(sender, instance, **kwargs):
    send_notification_event_to_kafka.delay(instance.id, 'deleted')
