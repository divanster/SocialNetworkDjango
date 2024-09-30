# backend/friends/views.py
from rest_framework import viewsets, permissions, serializers
from .models import FriendRequest, Friendship
from .serializers import FriendRequestSerializer, FriendshipSerializer
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from kafka_app.producer import KafkaProducerClient  # Import the Kafka producer client
import logging

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize Kafka Producer Client
producer = KafkaProducerClient()


class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    @extend_schema(
        parameters=[OpenApiParameter("id", type=OpenApiTypes.UUID,
                                     description="UUID of the friend request")],
    )
    def get_queryset(self):
        # Only show friend requests where the user is either the sender or the receiver
        return FriendRequest.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        )

    def perform_create(self, serializer):
        try:
            # Automatically set the sender to the current user
            instance = serializer.save(sender=self.request.user)

            # Send Kafka event for a new friend request
            message = {
                "event": "created",
                "friend_request_id": instance.id,
                "sender_id": instance.sender.id,
                "receiver_id": instance.receiver.id,
                "status": instance.status,
                "created_at": str(instance.created_at),
            }
            producer.send_message('FRIEND_EVENTS', message)
            logger.info(f"Sent Kafka message for new friend request: {message}")

        except ValidationError as e:
            # Catch duplicate request or other validation errors from the model
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            logger.error(f"Error sending Kafka message: {ex}")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.receiver != request.user:
            raise serializers.ValidationError("You do not have permission to accept "
                                              "this request.")

        # Only the receiver can accept a friend request
        if request.data.get("status") == "accepted":
            # Update the friend request to accepted status
            instance.status = "accepted"
            instance.save()

            # Automatically create a friendship
            friendship = Friendship.objects.create(
                user1=min(instance.sender, instance.receiver, key=lambda u: u.id),
                user2=max(instance.sender, instance.receiver, key=lambda u: u.id)
            )

            # Send Kafka event for the accepted friend request and created friendship
            try:
                message = {
                    "event": "accepted",
                    "friend_request_id": instance.id,
                    "friendship_id": friendship.id,
                    "sender_id": instance.sender.id,
                    "receiver_id": instance.receiver.id,
                    "created_at": str(instance.created_at),
                }
                producer.send_message('FRIEND_EVENTS', message)
                logger.info(
                    f"Sent Kafka message for accepted friend request: {message}")
            except Exception as ex:
                logger.error(f"Error sending Kafka message: {ex}")

            return Response({"detail": "Friend request accepted, friendship created."})

        return super().update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        # Send Kafka event for the deleted friend request
        try:
            message = {
                "event": "deleted",
                "friend_request_id": instance.id,
                "sender_id": instance.sender.id,
                "receiver_id": instance.receiver.id,
            }
            producer.send_message('FRIEND_EVENTS', message)
            logger.info(f"Sent Kafka message for deleted friend request: {message}")
        except Exception as ex:
            logger.error(f"Error sending Kafka message: {ex}")

        instance.delete()


class FriendshipViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    @extend_schema(
        parameters=[OpenApiParameter("id", type=OpenApiTypes.UUID,
                                     description="UUID of the friendship")],
    )
    def get_queryset(self):
        # Only show friendships where the current user is either user1 or user2
        return Friendship.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user)
        )

    def destroy(self, request, *args, **kwargs):
        # Override the destroy method to allow "unfriending"
        instance = self.get_object()

        # Ensure that only the users involved in the friendship can unfriend each other
        if instance.user1 != request.user and instance.user2 != request.user:
            raise serializers.ValidationError("You do not have permission "
                                              "to unfriend this user.")

        # Send Kafka event for the deleted friendship
        try:
            message = {
                "event": "deleted",
                "friendship_id": instance.id,
                "user1_id": instance.user1.id,
                "user2_id": instance.user2.id,
            }
            producer.send_message('FRIEND_EVENTS', message)
            logger.info(f"Sent Kafka message for deleted friendship: {message}")
        except Exception as ex:
            logger.error(f"Error sending Kafka message: {ex}")

        # If the user is involved in the friendship, allow deletion (unfriending)
        self.perform_destroy(instance)
        return Response({"detail": "Unfriended successfully."})
