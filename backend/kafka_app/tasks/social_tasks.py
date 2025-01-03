# backend/kafka_app/tasks/social_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings

from core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=10)
def process_post_event_task(self, post_id, event_type):
    """
    Celery task to send post events to Kafka, ensuring all UUID fields become strings.

    Args:
        self: Celery task instance.
        post_id (int): The ID of the post.
        event_type (str): Type of event (e.g., "created", "updated", "deleted").

    Returns:
        None
    """
    try:
        from social.models import Post  # Local import to avoid circular dependencies
        producer = KafkaProducerClient()

        if event_type == 'deleted':
            # Convert post_id (UUID) to str
            message = {
                "post_id": str(post_id),
                "event": "deleted",
            }
        else:
            post = Post.objects.select_related('user').get(id=post_id)
            # Convert both post.id and user.id (if they are UUID) to str
            message = {
                "post_id": str(post.id),
                "title": post.title,
                "content": post.content,
                "user_id": str(post.user.id),
                "user_username": post.user.username,
                "visibility": post.visibility,
                "created_at": str(post.created_at),
                "event": event_type,
            }

        kafka_topic = settings.KAFKA_TOPICS.get('SOCIAL_EVENTS', 'social-events')

        # Send message using send_message method
        producer.send_message(kafka_topic, message)
        producer.flush()
        logger.info(f"Sent Kafka message for post {event_type}: {message}")

    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    except AttributeError as e:
        logger.error(f"AttributeError: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending post {event_type}: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
    except Exception as e:
        logger.error(f"Error sending Kafka message for post {post_id}: {e}")
        self.retry(exc=e, countdown=60)
