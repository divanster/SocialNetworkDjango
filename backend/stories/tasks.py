from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from config import settings
from kafka_app.producer import KafkaProducerClient

logger = logging.getLogger(__name__)

@shared_task
def deactivate_expired_stories():
    try:
        logger.info("Started deactivating expired stories...")
        expiration_time = timezone.now() - timedelta(hours=24)

        # Import Story model here to prevent circular import issues
        from stories.models import Story

        # Fetch all the stories that need to be deactivated
        expired_stories = Story.objects.filter(is_active=True, created_at__lt=expiration_time)
        total_stories = expired_stories.count()

        if total_stories > 0:
            # Instantiate Kafka producer
            producer = KafkaProducerClient()

            # Update in chunks to avoid performance issues
            for story in expired_stories.iterator(chunk_size=500):
                try:
                    story.is_active = False
                    story.save()

                    # Send a Kafka event for each deactivated story
                    kafka_topic = settings.KAFKA_TOPICS.get('STORY_EVENTS', 'default-story-topic')
                    message = {
                        "story_id": str(story.id),
                        "event": "deactivated",
                        "user_id": str(story.user_id),
                        "created_at": str(story.created_at),
                    }
                    producer.send_message(kafka_topic, message)
                    logger.info(f"Sent Kafka message for deactivated story with ID: {story.id}")

                except Exception as e:
                    logger.error(f"Error deactivating story with ID '{story.id}': {e}")
                    continue

            producer.close()  # Close the Kafka producer connection
            logger.info(f"Successfully deactivated {total_stories} expired stories.")
        else:
            logger.info("No expired stories found to deactivate.")

    except Exception as e:
        logger.error(f"An error occurred while deactivating expired stories: {e}")
