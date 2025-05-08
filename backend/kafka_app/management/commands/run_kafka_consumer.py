import asyncio
import logging
import sys
from django.core.management.base import BaseCommand
from config import settings
from kafka_app.consumer import KafkaConsumerApp

logger = logging.getLogger(__name__)

# Ensure that any thread running async code gets an event loop
def set_event_loop():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

class Command(BaseCommand):
    help = (
        "Starts the Kafka consumer (using aiokafka) to listen on your configured topics "
        "and forward messages to Django Channels groups."
    )

    def handle(self, *args, **options):
        topics = list(settings.KAFKA_TOPICS.values())
        group_id = settings.KAFKA_CONSUMER_GROUP_ID

        consumer_app = KafkaConsumerApp(topics, group_id)

        # Ensure event loop is set before starting Kafka consumer
        set_event_loop()

        try:
            asyncio.get_event_loop().run_until_complete(consumer_app._consume_loop())
        except KeyboardInterrupt:
            logger.info("Kafka consumer interrupted by user.")
        except Exception as e:
            logger.error(f"Unexpected error in Kafka consumer: {e}", exc_info=True)
        finally:
            logger.info("Kafka consumer shutdown complete.")
            sys.exit(0)
