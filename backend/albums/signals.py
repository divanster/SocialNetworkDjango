# backend/albums/signals.py

import logging
from mongoengine import signals  # Import signals from mongoengine for MongoDB models
from .album_models import Album  # Correct import for the split models
from .photo_models import Photo  # Correct import for the split models
from .tasks import process_album_event_task, process_photo_event_task

logger = logging.getLogger(__name__)


# Signals for the Album model
def album_created_or_updated(sender, document, **kwargs):
    created = kwargs.get('created', False)
    event_type = 'created' if created else 'updated'
    process_album_event_task.delay(str(document.id), event_type)
    logger.info(
        f"[SIGNAL] Triggered Celery task for album {event_type} with ID {document.id}")


signals.post_save.connect(album_created_or_updated, sender=Album)


def album_deleted(sender, document, **kwargs):
    process_album_event_task.delay(str(document.id), 'deleted')
    logger.info(
        f"[SIGNAL] Triggered Celery task for album deleted with ID {document.id}")


signals.post_delete.connect(album_deleted, sender=Album)


# Signals for the Photo model
def photo_created_or_updated(sender, document, **kwargs):
    created = kwargs.get('created', False)
    event_type = 'created' if created else 'updated'
    process_photo_event_task.delay(str(document.id), event_type)
    logger.info(
        f"[SIGNAL] Triggered Celery task for photo {event_type} with ID {document.id}")


signals.post_save.connect(photo_created_or_updated, sender=Photo)


def photo_deleted(sender, document, **kwargs):
    process_photo_event_task.delay(str(document.id), 'deleted')
    logger.info(
        f"[SIGNAL] Triggered Celery task for photo deleted with ID {document.id}")


signals.post_delete.connect(photo_deleted, sender=Photo)
