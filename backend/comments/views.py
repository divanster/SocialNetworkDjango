from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Comment
from .serializers import CommentSerializer
from kafka_app.producer import KafkaProducerClient


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        # Send Kafka event
        producer = KafkaProducerClient()
        message = {
            "comment_id": instance.id,
            "content": instance.content,
            "user_id": instance.user_id,
            "post_id": instance.post_id,
            "created_at": str(instance.created_at),
        }
        producer.send_message('COMMENT_EVENTS', message)

    def perform_destroy(self, instance):
        # Send Kafka event
        producer = KafkaProducerClient()
        message = {
            "comment_id": instance.id,
            "action": "deleted"
        }
        producer.send_message('COMMENT_EVENTS', message)
        instance.delete()
