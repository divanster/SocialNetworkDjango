from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Message
from .serializers import MessageSerializer
from kafka_app.producer import KafkaProducerClient
import logging

logger = logging.getLogger(__name__)
producer = KafkaProducerClient()


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(receiver_id=user.id) | Message.objects.filter(
            sender_id=user.id)

    def perform_create(self, serializer):
        instance = serializer.save(sender=self.request.user)
        message = {
            "event": "created",
            "message_id": instance.id,
            "sender_id": instance.sender_id,
            "receiver_id": instance.receiver_id,
            "content": instance.content,
            "timestamp": str(instance.timestamp)
        }
        try:
            producer.send_message('MESSENGER_EVENTS', message)
            logger.info(f"Sent Kafka message for new message: {message}")
        except Exception as e:
            logger.error(f"Error sending Kafka message: {e}")

    def perform_update(self, serializer):
        instance = serializer.save()
        message = {
            "event": "updated",
            "message_id": instance.id,
            "sender_id": instance.sender_id,
            "receiver_id": instance.receiver_id,
            "content": instance.content,
            "timestamp": str(instance.timestamp)
        }
        try:
            producer.send_message('MESSENGER_EVENTS', message)
            logger.info(f"Sent Kafka message for updated message: {message}")
        except Exception as e:
            logger.error(f"Error sending Kafka message: {e}")

    def perform_destroy(self, instance):
        message = {
            "event": "deleted",
            "message_id": instance.id,
            "sender_id": instance.sender_id,
            "receiver_id": instance.receiver_id,
        }
        try:
            producer.send_message('MESSENGER_EVENTS', message)
            logger.info(f"Sent Kafka message for deleted message: {message}")
        except Exception as e:
            logger.error(f"Error sending Kafka message: {e}")

        instance.delete()
