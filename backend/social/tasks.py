# backend/social/tasks.py

import logging
from celery import shared_task

from social.models import Post
from core.utils import get_kafka_producer
from django.conf import settings

import json

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5, default_retry_delay=10)
def send_post_event_to_kafka(self, post_id, event_type):
    """
    Celery task to send post events to Kafka, ensuring all UUID fields become strings.
    """
    producer = get_kafka_producer()
    logger.info(f"Producer instance type: {type(producer)}")
    logger.info("Obtained KafkaProducerClient instance.")

    try:
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

        kafka_topic = settings.KAFKA_TOPICS.get('POST_EVENTS', 'default-post-topic')

        # Send message using send_message method
        producer.send_message(kafka_topic, message)
        producer.flush()
        logger.info(f"Sent Kafka message for post {event_type}: {message}")

    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    except AttributeError as e:
        logger.error(f"AttributeError: {e}")
        self.retry(exc=e)
    except Exception as e:
        logger.error(f"Error sending Kafka message for post {post_id}: {e}")
        self.retry(exc=e)
    # Do not close the producer to maintain Singleton instance

# Removed the consume_post_events task as consumers should run independently
