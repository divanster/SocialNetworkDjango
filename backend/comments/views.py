# backend/comments/views.py

from rest_framework import viewsets
from .models import Comment
from .serializers import CommentSerializer
from core.utils import get_kafka_producer  # Updated import to use core utility


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Comment CRUD operations. Uses Kafka to produce comment events.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        """
        Overridden perform_create method to save comment and send event to Kafka.
        """
        instance = serializer.save(user=self.request.user)  # Ensure the user is set correctly
        producer = get_kafka_producer()  # Use core utility for KafkaProducerClient
        message = {
            "comment_id": instance.id,
            "content": instance.content,
            "user_id": instance.user_id,
            "post_id": instance.post_id,
            "created_at": str(instance.created_at),
            "event": "created"
        }
        producer.send_message('COMMENT_EVENTS', message)

    def perform_update(self, serializer):
        """
        Overridden perform_update method to update comment and send update event to Kafka.
        """
        instance = serializer.save()
        producer = get_kafka_producer()  # Use core utility for KafkaProducerClient
        message = {
            "comment_id": instance.id,
            "content": instance.content,
            "user_id": instance.user_id,
            "post_id": instance.post_id,
            "updated_at": str(instance.updated_at),
            "event": "updated"
        }
        producer.send_message('COMMENT_EVENTS', message)

    def perform_destroy(self, instance):
        """
        Overridden perform_destroy method to delete comment and send delete event to Kafka.
        """
        producer = get_kafka_producer()  # Use core utility for KafkaProducerClient
        message = {
            "comment_id": instance.id,
            "action": "deleted"
        }
        producer.send_message('COMMENT_EVENTS', message)
        instance.delete()
