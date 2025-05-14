# backend/kafka_app/tasks/social_tasks.py
import logging
from celery import shared_task
from aiokafka.errors import KafkaTimeoutError, KafkaError

from core.task_utils import BaseTask
from kafka_app.services import KafkaService
from kafka_app.constants import SOCIAL_EVENTS
from social.models import Post  # ensure correct import path

logger = logging.getLogger(__name__)

@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_post_event_task(self, post_id, event_type):
    """
    Celery task to process post events and send messages to Kafka.
    """
    logger.debug(f"Received event_type: {event_type} for post {post_id}")

    # Normalize shorthand types
    if event_type in ('created', 'updated', 'deleted'):
        event_type = f"post_{event_type}"

    try:
        # Try to fetch post, if missing – bail out
        post = Post.objects.filter(id=post_id).first()
        if not post:
            logger.error(f"Post ID {post_id} not found for Kafka event")
            return

        # Build event data
        event_data = {
            'id': str(post.id),
            'content': post.content,
            'title': post.title,
            'user_id': str(post.user.id),
            'user_username': post.user.username,
            'visibility': post.visibility,
            'created_at': post.created_at.isoformat(),
        }

        # Final Kafka message
        kafka_event = {
            'app': post._meta.app_label,
            'event_type': event_type,
            'model_name': 'Post',
            'id': str(post.id),
            'data': event_data,
        }

        # Send it
        KafkaService().send_message(SOCIAL_EVENTS, kafka_event)
        logger.info(f"Sent Kafka message for post event '{event_type}' (ID: {post_id})")

    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout for post {post_id}: {e}")
        # exponential back-off
        self.retry(exc=e,
                   countdown=60 * (2 ** self.request.retries))
    except KafkaError as e:
        logger.error(f"Kafka error for post {post_id}: {e}")
        self.retry(exc=e, countdown=60)
    except Exception as e:
        logger.error(f"Unexpected error processing post {post_id}: {e}", exc_info=True)
        self.retry(exc=e, countdown=60)
