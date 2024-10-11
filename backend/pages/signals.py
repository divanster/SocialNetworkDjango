# backend/pages/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Page
from kafka_app.producer import KafkaProducerClient
import logging

logger = logging.getLogger(__name__)

# Initialize Kafka producer
producer = KafkaProducerClient()


@receiver(post_save, sender=Page)
def page_saved(sender, instance, created, **kwargs):
    try:
        if created:
            message = {
                "page_id": instance.id,
                "title": instance.title,
                "content": instance.content,
                "created_at": str(instance.created_at),
                "event": "created"
            }
            producer.send_message('PAGE_EVENTS', message)
            logger.info(f"Sent Kafka message for new page: {message}")
            print(f'Page created: {instance}')
        else:
            message = {
                "page_id": instance.id,
                "title": instance.title,
                "content": instance.content,
                "updated_at": str(instance.updated_at),
                "event": "updated"
            }
            producer.send_message('PAGE_EVENTS', message)
            logger.info(f"Sent Kafka message for updated page: {message}")
            print(f'Page updated: {instance}')
    except Exception as e:
        logger.error(f"Error sending Kafka message for page saved: {e}")


@receiver(post_delete, sender=Page)
def page_deleted(sender, instance, **kwargs):
    try:
        message = {
            "page_id": instance.id,
            "event": "deleted"
        }
        producer.send_message('PAGE_EVENTS', message)
        logger.info(f"Sent Kafka message for deleted page: {message}")
        print(f'Page deleted: {instance}')
    except Exception as e:
        logger.error(f"Error sending Kafka message for page deleted: {e}")
