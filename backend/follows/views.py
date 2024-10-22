# backend/follows/views.py
from rest_framework import viewsets, permissions
from .models import Follow
from .serializers import FollowSerializer
from kafka_app.producer import KafkaProducerClient
import logging

logger = logging.getLogger(__name__)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(follower=self.request.user)

        # Send Kafka event for a new follow
        producer = KafkaProducerClient()
        message = {
            "follow_id": instance.id,
            "follower_id": instance.follower.id,
            "follower_username": instance.follower.username,
            "followed_id": instance.followed.id,
            "followed_username": instance.followed.username,
            "created_at": str(instance.created_at),
        }
        try:
            producer.send_message('FOLLOW_EVENTS', message)
            logger.info(f"Sent Kafka message for new follow: {message}")
        except Exception as e:
            logger.error(f"Error sending Kafka message: {e}")

    def perform_destroy(self, instance):
        # Send Kafka event for a deleted follow
        producer = KafkaProducerClient()
        message = {
            "follow_id": instance.id,
            "follower_id": instance.follower.id,
            "followed_id": instance.followed.id,
            "action": "deleted"
        }
        try:
            producer.send_message('FOLLOW_EVENTS', message)
            logger.info(f"Sent Kafka message for deleted follow: {message}")
        except Exception as e:
            logger.error(f"Error sending Kafka message: {e}")

        instance.delete()
