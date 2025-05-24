# backend/follows/services.py

import logging
from .models import Follow
from notifications.services import create_notification
from kafka_app.services import KafkaService  # Kafka producer import
from django.conf import settings
import json

logger = logging.getLogger(__name__)

def process_follow_event(data):
    """
    Processes a follow event to trigger notification logic and publish events to Kafka.
    """
    follow_id = data.get('follow_id')
    try:
        follow = Follow.objects.get(id=follow_id)
        logger.info(f"[SERVICE] Processing follow event for Follow ID: {follow_id}")

        # Notify the followed user
        notify_user_about_follow(follow)

        # Publish the follow_created or follow_deleted event to Kafka
        event_type = 'follow_deleted' if follow.is_deleted else 'follow_created'
        publish_follow_event(follow, event_type)

    except Follow.DoesNotExist:
        logger.error(f"[SERVICE] Follow with ID {follow_id} does not exist.")
    except Exception as e:
        logger.error(f"[SERVICE] Error processing follow event: {e}")


def notify_user_about_follow(follow):
    """
    Sends a notification to the followed user.
    """
    try:
        create_notification({
            'sender_id': follow.follower.id,
            'sender_username': follow.follower.username,
            'receiver_id': follow.followed.id,
            'receiver_username': follow.followed.username,
            'notification_type': 'follow',
            'text': f"{follow.follower.username} started following you."
        })
        logger.info(
            f"[NOTIFICATION] Notification created for user {follow.followed.id} about follow by {follow.follower.id}")

    except Exception as e:
        logger.error(
            f"[NOTIFICATION] Failed to notify user {follow.followed.id} about follow by {follow.follower.id}: {e}")


def publish_follow_event(follow, event_type):
    """
    Publishes follow events to Kafka.
    """
    try:
        producer = KafkaService()
        message = {
            "event_type": event_type,
            "data": {
                "follow_id": follow.id,
                "follower_id": follow.follower.id,
                "follower_username": follow.follower.username,
                "followed_id": follow.followed.id,
                "followed_username": follow.followed.username,
                "created_at": follow.created_at.isoformat(),
                "deleted_at": follow.deleted_at.isoformat() if follow.deleted_at else None,
            }
        }

        # Retrieve Kafka topic from settings
        kafka_topic = settings.KAFKA_TOPICS.get('FOLLOW_EVENTS')
        if not kafka_topic:
            logger.error("Kafka topic 'FOLLOW_EVENTS' not defined in settings.")
            return

        # Send message to Kafka
        producer.send_message(kafka_topic, message)
        logger.info(
            f"[KAFKA] Successfully sent '{event_type}' event to topic '{kafka_topic}': {message}")

    except Exception as e:
        logger.error(
            f"[KAFKA] Error sending '{event_type}' event to Kafka for Follow ID {follow.id}: {e}")
