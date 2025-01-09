# backend/kafka_app/management/commands/run_kafka_consumer.py

import logging
import signal
import sys
import asyncio

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

        loop = asyncio.get_event_loop()

        # Define a graceful shutdown handler
        def shutdown_handler():
            logger.info("Shutting down Kafka consumer...")
            for task in asyncio.all_tasks(loop):
                task.cancel()

        # Register the shutdown handler for SIGINT and SIGTERM
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, shutdown_handler)

        try:
            loop.run_until_complete(consumer_app.start())
        except asyncio.CancelledError:
            logger.info("Kafka consumer has been cancelled.")
        except Exception as e:
            logger.error(f"Unexpected error in Kafka consumer: {e}", exc_info=True)
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
            logger.info("Kafka consumer shutdown complete.")
            sys.exit(0)
