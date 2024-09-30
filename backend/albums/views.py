# albums/views.py
from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Album, Photo
from .serializers import AlbumSerializer, PhotoSerializer
from kafka_app.producer import KafkaProducerClient  # Import Kafka Producer
from .tasks import process_new_album  # Import the Celery task


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        album = serializer.save(user=self.request.user)
        process_new_album.delay(album.id)  # Execute the task asynchronously

        # Produce Kafka message directly from the view
        producer = KafkaProducerClient()
        message = {
            "event": "created",
            "album_id": album.id,
            "title": album.title,
            "user_id": self.request.user.id,
            "created_at": str(album.created_at),
        }
        producer.send_message('ALBUM_EVENTS', message)

    def perform_update(self, serializer):
        album = serializer.save()
        producer = KafkaProducerClient()
        message = {
            "event": "updated",
            "album_id": album.id,
            "title": album.title,
            "user_id": self.request.user.id,
            "updated_at": str(album.updated_at),
        }
        producer.send_message('ALBUM_EVENTS', message)
