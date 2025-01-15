# backend/kafka_app/tasks/reaction_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from core.task_utils import BaseTask
from kafka_app.services import KafkaService
from reactions.models import Reaction  # Ensure correct model import

logger = logging.getLogger(__name__)


def _get_reaction_data(reaction):
    """
    Extract relevant data from the reaction instance.
    """
    return {
        'type': reaction.type,
        'user_id': str(reaction.user.id),
        'user_username': reaction.user.username,
        'post_id': str(reaction.post.id),
        'created_at': reaction.created_at.isoformat(),
        # Add other relevant fields as needed
    }


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_reaction_event_task(self, reaction_id, event_type):
    """
    Celery task to process reaction events and send messages to Kafka.

    Args:
        self: Celery task instance.
        reaction_id (UUID): The ID of the reaction.
        event_type (str): Type of event to be processed (e.g., "created", "deleted").

    Returns:
        None
    """
    try:
        reaction = Reaction.objects.get(id=reaction_id)

        # Construct the standardized Kafka message
        message = {
            'app': reaction._meta.app_label,
            'event_type': event_type,
            'model_name': 'Reaction',
            'id': str(reaction.id),
            'data': _get_reaction_data(reaction),
        }

        # Send message to Kafka using KafkaService
        kafka_topic_key = 'REACTION_EVENTS'  # Ensure this key exists in settings.KAFKA_TOPICS
        KafkaService().send_message(kafka_topic_key, message)
        logger.info(f"Sent Kafka message for reaction {event_type}: {message}")

    except Reaction.DoesNotExist:
        logger.error(f"Reaction with ID {reaction_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending reaction {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e, countdown=60)
