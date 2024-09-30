# backend/comments/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Comment
from kafka_app.producer import KafkaProducerClient
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Comment)
def comment_created(sender, instance, created, **kwargs):
    if created:
        producer = KafkaProducerClient()
        message = {
            "comment_id": instance.id,
            "content": instance.content,
            "user_id": instance.user_id,
            "post_id": instance.post_id,
            "created_at": str(instance.created_at),
        }
        try:
            producer.send_message('COMMENT_EVENTS', message)
            logger.info(f"Sent Kafka message for new comment: {message}")
        except Exception as e:
            logger.error(f"Error sending Kafka message: {e}")


@receiver(post_delete, sender=Comment)
def comment_deleted(sender, instance, **kwargs):
    producer = KafkaProducerClient()
    message = {
        "comment_id": instance.id,
        "action": "deleted"
    }
    try:
        producer.send_message('COMMENT_EVENTS', message)
        logger.info(f"Sent Kafka message for deleted comment: {message}")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
