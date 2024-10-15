# backend/comments/test_views.py
from rest_framework import viewsets
from .models import Comment
from .serializers import CommentSerializer
from kafka_app.producer import KafkaProducerClient


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        instance = serializer.save(
            user=self.request.user)  # Ensure the user is set correctly
        producer = KafkaProducerClient()
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
        instance = serializer.save()
        producer = KafkaProducerClient()
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
        producer = KafkaProducerClient()
        message = {
            "comment_id": instance.id,
            "action": "deleted"
        }
        producer.send_message('COMMENT_EVENTS', message)
        instance.delete()
