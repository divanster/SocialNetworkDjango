import logging
from kafka_app.base_consumer import BaseKafkaConsumer
from django.conf import settings

logger = logging.getLogger(__name__)


class MessengerKafkaConsumer(BaseKafkaConsumer):
    def __init__(self):
        topic = settings.KAFKA_TOPICS.get('MESSENGER_EVENTS', 'default-messenger-topic')
        group_id = settings.KAFKA_CONSUMER_GROUP_ID
        super().__init__(topic, group_id)

    def process_message(self, message):
        logger.info(f"Processing messenger event: {message}")
        # Implement custom business logic for message events here


def main():
    consumer_client = MessengerKafkaConsumer()
    consumer_client.consume_messages()


if __name__ == "__main__":
    main()
