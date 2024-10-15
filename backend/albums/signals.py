from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Album, Photo
from albums.tasks import send_album_event_to_kafka, send_photo_event_to_kafka
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Album)
def album_saved(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    send_album_event_to_kafka.delay(instance.id, event_type)
    logger.info(f"[SIGNAL] Album {event_type}: {instance.id}")


@receiver(post_delete, sender=Album)
def album_deleted(sender, instance, **kwargs):
    send_album_event_to_kafka.delay(instance.id, 'deleted')
    logger.info(f"[SIGNAL] Album deleted: {instance.id}")


@receiver(post_save, sender=Photo)
def photo_saved(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    send_photo_event_to_kafka.delay(instance.id, event_type)
    logger.info(f"[SIGNAL] Photo {event_type}: {instance.id}")


@receiver(post_delete, sender=Photo)
def photo_deleted(sender, instance, **kwargs):
    send_photo_event_to_kafka.delay(instance.id, 'deleted')
    logger.info(f"[SIGNAL] Photo deleted: {instance.id}")
