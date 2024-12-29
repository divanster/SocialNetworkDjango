# backend/kafka_app/management/commands/run_kafka_consumer.py

import logging
import signal
import sys

from django.core.management.base import BaseCommand
from django.conf import settings

from kafka_app.consumer import KafkaConsumerApp

# Configure logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ('Starts the Kafka consumer to listen to specified topics and forward '
            'messages to Channels groups.')

    def handle(self, *args, **options):
        # Initialize the KafkaConsumerApp with topics and group_id
        topics = list(settings.KAFKA_TOPICS.values())
        group_id = settings.KAFKA_CONSUMER_GROUP_ID

        consumer_app = KafkaConsumerApp(topics, group_id)

        # Define a graceful shutdown handler
        def shutdown_handler(signum, frame):
            logger.info("Shutting down Kafka consumer...")
            consumer_app.close()
            sys.exit(0)

        # Register the shutdown handler for SIGINT and SIGTERM
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        # Start consuming messages
        try:
            consumer_app.consume_messages()
        except Exception as e:
            logger.error(f"Unexpected error in Kafka consumer: {e}", exc_info=True)
            consumer_app.close()
            sys.exit(1)
