# backend/kafka_app/tasks/reaction_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from backend.core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_reaction_event_task(self, reaction_id, event_type):
    """
    Celery task to process reaction events and send them to Kafka.

    Args:
        self: Celery task instance.
        reaction_id (int): The ID of the reaction.
        event_type (str): Type of event (e.g., "created", "deleted").

    Returns:
        None
    """
    try:
        from reactions.models import Reaction  # Local import to avoid circular dependencies
        producer = KafkaProducerClient()

        if event_type == 'deleted':
            message = {
                "reaction_id": reaction_id,
                "action": "deleted"
            }
        else:
            reaction = Reaction.objects.select_related('user', 'content_object').get(id=reaction_id)
            message = {
                "reaction_id": reaction.id,
                "user_id": str(reaction.user.id),
                "post_id": str(reaction.content_object.id),
                "emoji": reaction.emoji,
                "created_at": reaction.created_at.isoformat(),
                "event": event_type,
            }

        kafka_topic = settings.KAFKA_TOPICS.get('REACTION_EVENTS', 'reaction-events')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for reaction {event_type}: {message}")

    except Reaction.DoesNotExist:
        logger.error(f"Reaction with ID {reaction_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending reaction {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)
