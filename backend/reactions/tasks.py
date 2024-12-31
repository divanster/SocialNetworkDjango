# backend/reactions/tasks.py

import logging
from celery import shared_task

from django.conf import settings

from backend.core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTask)
def send_reaction_event_to_kafka(self, reaction_id, event_type):
    """
    Celery task to send reaction events to Kafka.
    """
    try:
        from reactions.models import Reaction

        if event_type == 'deleted':
            message = {
                "reaction_id": reaction_id,
                "action": "deleted"
            }
        else:
            reaction = Reaction.objects.select_related('user', 'content_object').get(
                id=reaction_id)
            message = {
                "reaction_id": reaction.id,
                "user_id": str(reaction.user.id),
                "post_id": str(reaction.content_object.id),
                "emoji": reaction.emoji,
                "created_at": reaction.created_at.isoformat(),
                "event": event_type,
            }

        kafka_topic = settings.KAFKA_TOPICS.get('REACTION_EVENTS',
                                                'default-reaction-topic')
        KafkaProducerClient.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for reaction {event_type}: {message}")

    except Reaction.DoesNotExist:
        logger.error(f"Reaction with ID {reaction_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e)
