import logging
import sys

from django.core.management.base import BaseCommand
from django.conf import settings

from kafka_app.consumer import KafkaConsumerApp

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Starts the Kafka consumer (using aiokafka) to listen on your configured topics "
        "and forward messages to Django Channels groups."
    )

    def handle(self, *args, **options):
        topics = list(settings.KAFKA_TOPICS.values())
        group_id = settings.KAFKA_CONSUMER_GROUP_ID

        consumer_app = KafkaConsumerApp(topics, group_id)

        try:
            consumer_app.start()
        except KeyboardInterrupt:
            logger.info("Kafka consumer interrupted by user.")
        except Exception as e:
            logger.error(f"Unexpected error in Kafka consumer: {e}", exc_info=True)
        finally:
            logger.info("Kafka consumer shutdown complete.")
            sys.exit(0)
