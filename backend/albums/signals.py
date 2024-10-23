from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Album, Photo
from kafka_app.producer import KafkaProducerClient
import logging

logger = logging.getLogger(__name__)
producer = KafkaProducerClient()  # Centralized producer instance


@receiver(post_save, sender=Album)
def album_saved(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    message = {
        "event": event_type,
        "album_id": instance.id,
        "title": instance.title,
        "description": instance.description,
        "user_id": instance.user.id,
    }
    transaction.on_commit(lambda: producer.send_message('ALBUM_EVENTS', message))
    logger.info(f"[SIGNAL] Album {event_type}: {instance.id}")


@receiver(post_delete, sender=Album)
def album_deleted(sender, instance, **kwargs):
    message = {
        "event": "deleted",
        "album_id": instance.id,
        "user_id": instance.user.id,
    }
    transaction.on_commit(lambda: producer.send_message('ALBUM_EVENTS', message))
    logger.info(f"[SIGNAL] Album deleted: {instance.id}")


@receiver(post_save, sender=Photo)
def photo_saved(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    message = {
        "event": event_type,
        "photo_id": instance.id,
        "album_id": instance.album.id,
        "description": instance.description,
    }
    transaction.on_commit(lambda: producer.send_message('PHOTO_EVENTS', message))
    logger.info(f"[SIGNAL] Photo {event_type}: {instance.id}")


@receiver(post_delete, sender=Photo)
def photo_deleted(sender, instance, **kwargs):
    message = {
        "event": "deleted",
        "photo_id": instance.id,
        "album_id": instance.album.id,
    }
    transaction.on_commit(lambda: producer.send_message('PHOTO_EVENTS', message))
    logger.info(f"[SIGNAL] Photo deleted: {instance.id}")
