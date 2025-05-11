# backend/kafka_app/tasks/social_tasks.py

import logging

from celery import shared_task
from aiokafka.errors import KafkaTimeoutError, KafkaError

from core.task_utils import BaseTask
from kafka_app.services import KafkaService
from kafka_app.constants import SOCIAL_EVENTS, POST_CREATED, POST_UPDATED, POST_DELETED
from social.models import Post  # Ensure this is the correct import path

logger = logging.getLogger(__name__)


def _get_post_data(post):
    """
    Extract relevant data from the post instance.
    """
    return {
        'id': str(post.id),
        'content': post.content,
        'title': post.title,
        'user_id': str(post.user.id),
        'user_username': post.user.username,
        'visibility': post.visibility,
        'created_at': post.created_at.isoformat(),
        # Add other relevant fields as needed
    }


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def process_post_event_task(self, post_id, event_type):
    """
    Celery task to process post events and send messages to Kafka.
    """
    logger.debug(f"Received event_type: {event_type} for post {post_id}")

    # Allow shorthand event names and normalize
    if event_type in ('created', 'updated', 'deleted'):
        event_type = f"post_{event_type}"  # e.g. 'post_created'

    try:
        # Validate that we now have one of the constants
        valid_event_types = [POST_CREATED, POST_UPDATED, POST_DELETED]
        if event_type not in valid_event_types:
            logger.error(f"Invalid event_type '{event_type}' for post {post_id}")
            return  # Nothing to do

        post = Post.objects.get(pk=post_id)
        logger.debug(f"Fetched post with ID {post_id}: {post!r}")

        # (Optional) per‐event hooks could go here
        # if event_type == POST_CREATED: …

        # Build the Kafka message
        message = {
            'app': post._meta.app_label,
            'event_type': event_type,
            'model_name': 'Post',
            'id': str(post.id),
            'data': _get_post_data(post),
        }
        logger.debug(f"Kafka message: {message}")

        # Send it
        KafkaService().send_message(SOCIAL_EVENTS, message)
        logger.info(f"Successfully sent Kafka message for post event '{event_type}'.")

    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error for post {post_id}: {e}")
        # exponential back-off
        self.retry(exc=e,
                   countdown=60 * (2 ** self.request.retries),
                   max_retries=self.max_retries)
    except KafkaError as e:
        logger.error(f"Kafka error for post {post_id}: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)
    except Exception as e:
        logger.error(f"Unexpected error processing post {post_id}: {e}", exc_info=True)
        self.retry(exc=e, countdown=60)
