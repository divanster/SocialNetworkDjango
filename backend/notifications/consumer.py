# backend/notifications/consumer.py

import logging
from kafka_app.base_consumer import BaseKafkaConsumer
from django.conf import settings

logger = logging.getLogger(__name__)


class NotificationKafkaConsumer(BaseKafkaConsumer):
    def __init__(self):
        # Initialize with topic and group_id
        topic = settings.KAFKA_TOPICS.get('NOTIFICATIONS_EVENTS',
                                          'default-notifications-topic')
        group_id = settings.KAFKA_CONSUMER_GROUP_ID
        super().__init__(topic, group_id)

    def process_message(self, message):
        # Add your custom processing logic for notifications here
        try:
            logger.info(f"Processing notification event: {message}")
            # Implement the business logic here (e.g., update database, send notification)
        except Exception as e:
            logger.error(f"[KAFKA] Error processing notification message: {e}")


def main():
    consumer_client = NotificationKafkaConsumer()
    consumer_client.consume_messages()


if __name__ == "__main__":
    main()
