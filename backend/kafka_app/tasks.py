# backend/kafka_app/tasks.py

import logging
from celery import shared_task
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from celery.signals import worker_shutdown
from kafka.errors import KafkaTimeoutError

from .producer import KafkaProducerClient

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def send_post_event_to_kafka(self, post_id, event_type, tagged_user_ids=None):
    """
    Celery task to send post creation, update, deletion, tagging, or untagging events to Kafka.

    Args:
        post_id (int): ID of the post.
        event_type (str): Type of event ('post_created', 'post_updated', 'post_deleted', 'tagged', 'untagged').
        tagged_user_ids (list, optional): List of tagged user IDs for tagging events.
    """
    try:
        from social.models import Post  # Local import to prevent circular dependencies

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
        KafkaProducerClient.send_message(kafka_topic, message)
        logger.info(f"Sent post {event_type} event to Kafka: {message}")

    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to send post event to Kafka: {e}")
        self.retry(exc=e)


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def process_kafka_message(self, message):
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
        self.retry(exc=e)


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def process_notification_event_task(self, notification_id, event_type):
    """
    Celery task to process notification events and send them to Kafka.

    Args:
        notification_id (int): ID of the notification.
        event_type (str): Type of event ('created', 'updated', 'deleted').
    """
    try:
        from notifications.models import Notification  # Local import

        if event_type == 'deleted':
            message = {
                "notification_id": notification_id,
                "action": "deleted"
            }
        else:
            notification = Notification.objects.get(id=notification_id)
            message = {
                "notification_id": notification.id,
                "sender_id": notification.sender_id,
                "sender_username": notification.sender_username,
                "receiver_id": notification.receiver_id,
                "receiver_username": notification.receiver_username,
                "notification_type": notification.notification_type,
                "text": notification.text,
                "created_at": notification.created_at.isoformat(),
                "event": event_type,
            }

        kafka_topic = settings.KAFKA_TOPICS.get('NOTIFICATIONS_EVENTS', 'default-notifications-topic')
        KafkaProducerClient.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for notification {event_type}: {message}")

    except Notification.DoesNotExist:
        logger.error(f"Notification with ID {notification_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def process_notification_event_task_retry(self, notification_id, event_type):
    """
    Celery task to process notification events and send them to Kafka with specific retry for KafkaTimeoutError.

    Args:
        notification_id (int): ID of the notification.
        event_type (str): Type of event ('created', 'updated', 'deleted').
    """
    try:
        from notifications.models import Notification  # Local import

        if event_type == 'deleted':
            message = {
                "notification_id": notification_id,
                "action": "deleted"
            }
        else:
            notification = Notification.objects.get(id=notification_id)
            message = {
                "notification_id": notification.id,
                "sender_id": notification.sender_id,
                "sender_username": notification.sender_username,
                "receiver_id": notification.receiver_id,
                "receiver_username": notification.receiver_username,
                "notification_type": notification.notification_type,
                "text": notification.text,
                "created_at": notification.created_at.isoformat(),
                "event": event_type,
            }

        kafka_topic = 'NOTIFICATIONS_EVENTS'  # Consider using settings for consistency
        KafkaProducerClient.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for notification {event_type}: {message}")

    except Notification.DoesNotExist:
        logger.error(f"Notification with ID {notification_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending notification {event_type}: {e}")
        self.retry(exc=e)
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_reaction_event_to_kafka(self, reaction_id, event_type):
    """
    Celery task to send reaction events to Kafka.

    Args:
        reaction_id (int): ID of the reaction.
        event_type (str): Type of event ('created', 'updated', 'deleted').
    """
    try:
        from reactions.models import Reaction  # Local import

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

        kafka_topic = settings.KAFKA_TOPICS.get('REACTION_EVENTS', 'default-reaction-topic')
        KafkaProducerClient.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for reaction {event_type}: {message}")

    except Reaction.DoesNotExist:
        logger.error(f"Reaction with ID {reaction_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
        self.retry(exc=e)
