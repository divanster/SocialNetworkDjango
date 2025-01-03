# backend/kafka_app/tasks/__init__.py

from .album_tasks import process_album_event_task, process_photo_event_task
from .comment_tasks import process_comment_event_task
from .follow_tasks import process_follow_event_task
from .friend_tasks import process_friend_event
from .messenger_tasks import process_message_event_task
from .newsfeed_tasks import send_newsfeed_event_task
from .reaction_tasks import process_reaction_event_task
from .social_tasks import process_post_event_task
from .stories_tasks import deactivate_expired_stories
from .tagging_tasks import send_tagging_event_to_kafka, consume_tagging_events
from .user_tasks import process_user_event_task, send_welcome_email, send_profile_update_notification
from .notification_tasks import process_notification_event_task

# Import worker shutdown signal handler
from celery.signals import worker_shutdown
from kafka_app.producer import KafkaProducerClient

import logging

logger = logging.getLogger(__name__)


@worker_shutdown.connect
def shutdown_kafka_producer(**kwargs):
    """
    Signal handler to close the Kafka producer gracefully when Celery worker shuts down.
    """
    try:
        producer = KafkaProducerClient()
        producer.close()
        logger.info("KafkaProducer closed gracefully on worker shutdown.")
    except Exception as e:
        logger.error(f"Failed to close Kafka producer on worker shutdown: {e}")
