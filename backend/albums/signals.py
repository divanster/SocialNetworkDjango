# backend/albums/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Album, Photo
from albums.tasks import send_album_event_to_kafka, send_photo_event_to_kafka


@receiver(post_save, sender=Album)
def album_saved(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    # Dispatch Celery task instead of directly triggering Kafka
    send_album_event_to_kafka.delay(instance.id, event_type)


@receiver(post_delete, sender=Album)
def album_deleted(sender, instance, **kwargs):
    # Dispatch Celery task instead of directly triggering Kafka
    send_album_event_to_kafka.delay(instance.id, 'deleted')


@receiver(post_save, sender=Photo)
def photo_saved(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    # Dispatch Celery task instead of directly triggering Kafka
    send_photo_event_to_kafka.delay(instance.id, event_type)


@receiver(post_delete, sender=Photo)
def photo_deleted(sender, instance, **kwargs):
    # Dispatch Celery task instead of directly triggering Kafka
    send_photo_event_to_kafka.delay(instance.id, 'deleted')
