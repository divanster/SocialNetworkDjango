# backend/kafka_app/tasks.py

from celery import shared_task
from .producer import KafkaProducerClient
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging
import json
from social.models import Post  # Import Post model from the social app
from core.utils import get_friends  # Assuming this utility function exists
from celery.signals import worker_shutdown

logger = logging.getLogger(__name__)


@shared_task
def send_post_event_to_kafka(post_id, event_type, tagged_user_ids=None):
    """
    Celery task to send post creation, update, deletion, tagging, or untagging events to Kafka.

    Args:
        post_id (int): ID of the post.
        event_type (str): Type of event ('post_created', 'post_updated', 'post_deleted', 'tagged', 'untagged').
        tagged_user_ids (list, optional): List of tagged user IDs for tagging events.
    """
    producer = KafkaProducerClient()
    try:
        post = Post.objects.get(id=post_id)

        message = {
            'event_type': event_type,
            'data': {
                'post_id': str(post.id),
                'title': post.title,
                'content': post.content,
                'author_id': str(post.author.id),
                'visibility': post.visibility,
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat(),
            }
        }

        # Include 'tagged_user_ids' for tagging events
        if event_type in ['tagged', 'untagged'] and tagged_user_ids:
            message['data']['tagged_user_ids'] = [str(uid) for uid in tagged_user_ids]

        kafka_topic = settings.KAFKA_TOPICS.get('POST_EVENTS', 'default-post-topic')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent post {event_type} event to Kafka: {message}")
    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to send post event to Kafka: {e}")
        # Optionally, you can implement retries or other error handling here
    # Removed producer.close()


@shared_task
def process_kafka_message(message):
    """
    Celery task to process incoming Kafka messages and dispatch them to WebSocket groups.

    Args:
        message (dict): The message received from Kafka.
    """
    logger.debug(f"Processing Kafka message: {message}")

    try:
        group_name = message.get('group')
        content = message.get('content', '')
        if group_name:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'kafka_message',
                    'message': content,
                }
            )
            logger.info(f"Dispatched message to group {group_name}: {content}")
        else:
            logger.warning(f"No group specified in Kafka message: {message}")
    except Exception as e:
        logger.error(f"Error processing Kafka message: {e}")


@worker_shutdown.connect
def shutdown_kafka_producer(**kwargs):
    """
    Signal handler to close the Kafka producer gracefully when Celery worker shuts down.
    """
    producer = KafkaProducerClient()
    producer.close()
