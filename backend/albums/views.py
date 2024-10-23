from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Album, Photo
from .serializers import AlbumSerializer, PhotoSerializer
from kafka_app.producer import KafkaProducerClient
import logging

logger = logging.getLogger(__name__)
producer = KafkaProducerClient()  # Centralized producer instance

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.using('social_db').all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        album = serializer.save(user=self.request.user)
        message = {
            "event": "created",
            "album_id": album.id,
            "title": album.title,
            "description": album.description,
            "user_id": album.user.id,
        }
        try:
            producer.send_message('ALBUM_EVENTS', message)
            logger.info(f"Sent Kafka message for album created: {message}")
        except Exception as e:
            logger.error(f"Failed to send album event to Kafka: {e}")

    def perform_update(self, serializer):
        album = serializer.save()
        message = {
            "event": "updated",
            "album_id": album.id,
            "title": album.title,
            "description": album.description,
            "user_id": album.user.id,
        }
        try:
            producer.send_message('ALBUM_EVENTS', message)
            logger.info(f"Sent Kafka message for album updated: {message}")
        except Exception as e:
            logger.error(f"Failed to send album event to Kafka: {e}")

    def perform_destroy(self, instance):
        message = {
            "event": "deleted",
            "album_id": instance.id,
            "user_id": instance.user.id,
        }
        try:
            producer.send_message('ALBUM_EVENTS', message)
            logger.info(f"Sent Kafka message for album deleted: {message}")
        except Exception as e:
            logger.error(f"Failed to send album event to Kafka: {e}")

        instance.delete()


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.using('social_db').all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        photo = serializer.save()
        message = {
            "event": "created",
            "photo_id": photo.id,
            "album_id": photo.album.id,
            "description": photo.description,
        }
        try:
            producer.send_message('PHOTO_EVENTS', message)
            logger.info(f"Sent Kafka message for photo created: {message}")
        except Exception as e:
            logger.error(f"Failed to send photo event to Kafka: {e}")

    def perform_update(self, serializer):
        photo = serializer.save()
        message = {
            "event": "updated",
            "photo_id": photo.id,
            "album_id": photo.album.id,
            "description": photo.description,
        }
        try:
            producer.send_message('PHOTO_EVENTS', message)
            logger.info(f"Sent Kafka message for photo updated: {message}")
        except Exception as e:
            logger.error(f"Failed to send photo event to Kafka: {e}")

    def perform_destroy(self, instance):
        message = {
            "event": "deleted",
            "photo_id": instance.id,
            "album_id": instance.album.id,
        }
        try:
            producer.send_message('PHOTO_EVENTS', message)
            logger.info(f"Sent Kafka message for photo deleted: {message}")
        except Exception as e:
            logger.error(f"Failed to send photo event to Kafka: {e}")

        instance.delete()
