# albums/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Album
from tagging.models import TaggedItem
from django.contrib.contenttypes.models import ContentType
from kafka_app.producer import KafkaProducerClient  # Import Kafka Producer
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Album)
def album_saved(sender, instance, created, **kwargs):
    producer = KafkaProducerClient()
    event_type = 'created' if created else 'updated'

    # Fetch tagged user IDs
    tagged_items = TaggedItem.objects.filter(
        content_type=ContentType.objects.get_for_model(Album),
        object_id=instance.id
    )
    tagged_user_ids = list(tagged_items.values_list('tagged_user_id', flat=True))

    message = {
        'event': event_type,
        'album': str(instance.id),
        'title': instance.title,
        'description': instance.description,
        'tagged_user_ids': [str(user_id) for user_id in tagged_user_ids],
    }

    try:
        producer.send_message('ALBUM_EVENTS', message)  # Send to Kafka
        logger.info(f"Sent Kafka message for album {event_type}: {message}")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")


@receiver(post_delete, sender=Album)
def album_deleted(sender, instance, **kwargs):
    producer = KafkaProducerClient()
    message = {
        'event': 'deleted',
        'album': str(instance.id),
        'title': instance.title,
        'description': instance.description,
        'tagged_user_ids': [],
    }

    try:
        producer.send_message('ALBUM_EVENTS', message)  # Send to Kafka
        logger.info(f"Sent Kafka message for deleted album: {message}")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
