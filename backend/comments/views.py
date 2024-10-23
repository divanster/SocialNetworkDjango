# backend/comments/views.py
from rest_framework import viewsets
from .models import Comment
from .serializers import CommentSerializer
from kafka_app.producer import KafkaProducerClient
import logging

logger = logging.getLogger(__name__)
producer = KafkaProducerClient()

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
        message = {
            "event": "created",
            "comment_id": instance.id,
            "content": instance.content,
            "user_id": instance.user_id,
            "post_id": instance.post_id,
            "created_at": str(instance.created_at),
        }
        try:
            producer.send_message('COMMENT_EVENTS', message)
            logger.info(f"Sent Kafka message for comment created: {message}")
        except Exception as e:
            logger.error(f"Failed to send comment event to Kafka: {e}")

    def perform_update(self, serializer):
        """
        Overridden perform_update method to update comment and send update event to Kafka.
        """
        instance = serializer.save()
        message = {
            "event": "updated",
            "comment_id": instance.id,
            "content": instance.content,
            "user_id": instance.user_id,
            "post_id": instance.post_id,
            "updated_at": str(instance.updated_at),
        }
        try:
            producer.send_message('COMMENT_EVENTS', message)
            logger.info(f"Sent Kafka message for comment updated: {message}")
        except Exception as e:
            logger.error(f"Failed to send comment event to Kafka: {e}")

    def perform_destroy(self, instance):
        """
        Overridden perform_destroy method to delete comment and send delete event to Kafka.
        """
        message = {
            "event": "deleted",
            "comment_id": instance.id,
            "post_id": instance.post_id,
            "user_id": instance.user_id,
        }
        try:
            producer.send_message('COMMENT_EVENTS', message)
            logger.info(f"Sent Kafka message for comment deleted: {message}")
        except Exception as e:
            logger.error(f"Failed to send comment event to Kafka: {e}")

        instance.delete()
