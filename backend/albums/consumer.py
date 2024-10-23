import logging
from kafka_app.base_consumer import BaseKafkaConsumer
from albums.models import Album, Photo

logger = logging.getLogger(__name__)


class AlbumKafkaConsumer(BaseKafkaConsumer):
    def __init__(self):
        topic = 'album-events'
        group_id = 'album_group'
        super().__init__(topic, group_id)

    def process_message(self, message):
        try:
            event_type = message.get('event')
            album_id = message.get('album_id')
            if event_type == 'created':
                # Logic when an album is created
                logger.info(f"[KAFKA] Album created with ID: {album_id}")
            elif event_type == 'updated':
                # Logic when an album is updated
                logger.info(f"[KAFKA] Album updated with ID: {album_id}")
            elif event_type == 'deleted':
                # Logic when an album is deleted
                logger.info(f"[KAFKA] Album deleted with ID: {album_id}")
            else:
                logger.warning(f"[KAFKA] Unrecognized album event type: {event_type}")
        except Exception as e:
            logger.error(f"[KAFKA] Error processing album message: {e}")


class PhotoKafkaConsumer(BaseKafkaConsumer):
    def __init__(self):
        topic = 'photo-events'
        group_id = 'photo_group'
        super().__init__(topic, group_id)

    def process_message(self, message):
        try:
            event_type = message.get('event')
            photo_id = message.get('photo_id')
            if event_type == 'created':
                # Logic when a photo is created
                logger.info(f"[KAFKA] Photo created with ID: {photo_id}")
            elif event_type == 'updated':
                # Logic when a photo is updated
                logger.info(f"[KAFKA] Photo updated with ID: {photo_id}")
            elif event_type == 'deleted':
                # Logic when a photo is deleted
                logger.info(f"[KAFKA] Photo deleted with ID: {photo_id}")
            else:
                logger.warning(f"[KAFKA] Unrecognized photo event type: {event_type}")
        except Exception as e:
            logger.error(f"[KAFKA] Error processing photo message: {e}")


def main():
    album_consumer_client = AlbumKafkaConsumer()
    photo_consumer_client = PhotoKafkaConsumer()

    album_consumer_client.consume_messages()
    photo_consumer_client.consume_messages()


if __name__ == "__main__":
    main()
