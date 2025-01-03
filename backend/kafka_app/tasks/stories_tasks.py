# backend/kafka_app/tasks/stories_tasks.py

import logging
from celery import shared_task
from kafka.errors import KafkaTimeoutError
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

from backend.core.task_utils import BaseTask
from kafka_app.producer import KafkaProducerClient

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def send_story_event_to_kafka(self, story_id, event_type):
    """
    Celery task to send story events to Kafka.
    """
    try:
        from stories.models import Story
        story = Story.objects.get(id=story_id)
        message = {
            "story_id": str(story.id),
            "user_id": str(story.user_id),
            "content": story.content[:50] + '...' if len(story.content) > 50 else story.content,
            "media_type": story.media_type,
            "event": event_type,
            "created_at": story.created_at.isoformat(),
        }
        producer = KafkaProducerClient()
        kafka_topic = settings.KAFKA_TOPICS.get('STORY_EVENTS', 'story-events')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for story {event_type} with ID: {story.id}")

    except Story.DoesNotExist:
        logger.error(f"Story with ID {story_id} does not exist.")
    except KafkaTimeoutError as e:
        logger.error(f"Kafka timeout error while sending story {event_type}: {e}")
        self.retry(exc=e)
    except Exception as e:
        logger.error(f"Error sending Kafka message for story {event_type}: {e}")
        self.retry(exc=e)
    finally:
        if producer:
            try:
                producer.close()
            except Exception as e:
                logger.error(f"Error while closing Kafka producer: {e}")


@shared_task(bind=True, base=BaseTask, max_retries=5, default_retry_delay=60)
def deactivate_expired_stories(self):
    """
    Celery task to deactivate expired stories and send events to Kafka.
    """
    try:
        logger.info("Started deactivating expired stories...")
        expiration_time = timezone.now() - timedelta(hours=24)

        from stories.models import Story

        expired_stories = Story.objects.filter(is_active=True, created_at__lt=expiration_time)
        total_stories = expired_stories.count()

        if total_stories > 0:
            producer = KafkaProducerClient()

            for story in expired_stories.iterator(chunk_size=500):
                try:
                    story.is_active = False
                    story.save()

                    message = {
                        "story_id": str(story.id),
                        "event": "deactivated",
                        "user_id": str(story.user_id),
                        "created_at": story.created_at.isoformat(),
                    }
                    kafka_topic = settings.KAFKA_TOPICS.get('STORY_EVENTS', 'story-events')
                    producer.send_message(kafka_topic, message)
                    logger.info(f"Sent Kafka message for deactivated story with ID: {story.id}")

                except Exception as e:
                    logger.error(f"Error deactivating story with ID '{story.id}': {e}")
                    continue

            logger.info(f"Successfully deactivated {total_stories} expired stories.")
        else:
            logger.info("No expired stories found to deactivate.")

    except Exception as e:
        logger.error(f"An error occurred while deactivating expired stories: {e}")
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))  # Exponential backoff
