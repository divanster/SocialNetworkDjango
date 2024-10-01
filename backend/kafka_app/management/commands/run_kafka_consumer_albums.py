import logging
from django.core.management.base import BaseCommand
from kafka_app.consumer import KafkaConsumerClient
from albums.handlers import handle_album_events

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Runs the Kafka consumer for ALBUM_EVENTS'

    def handle(self, *args, **options):
        consumer = KafkaConsumerClient('ALBUM_EVENTS')

        self.stdout.write(self.style.SUCCESS('Started Kafka consumer for ALBUM_EVENTS'))

        try:
            for message in consumer.consume_messages():
                try:
                    handle_album_events(message)
                except Exception as e:
                    logger.error(f"Error handling album event: {e}")
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Stopping Kafka consumer for ALBUM_EVENTS'))
            consumer.close()
            self.stdout.write(self.style.SUCCESS('Kafka consumer stopped gracefully.'))
        except Exception as e:
            logger.error(f"Unexpected error in Kafka consumer: {e}")
            consumer.close()
