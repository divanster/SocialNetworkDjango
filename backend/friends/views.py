from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework import viewsets, permissions, serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .models import FriendRequest, Friendship
from .serializers import FriendRequestSerializer, FriendshipSerializer
import logging

# Initialize logging
logger = logging.getLogger(__name__)


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
            logger.info(f"Friend request created: {instance}")
        except ValidationError as e:
            # Catch duplicate request or other validation errors from the model
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as ex:
            logger.error(f"Error during friend request creation: {ex}")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.receiver != request.user:
            raise serializers.ValidationError(
                "You do not have permission to accept this request.")

        # Only the receiver can accept a friend request
        if request.data.get("status") == FriendRequest.Status.ACCEPTED:
            # Update the friend request to accepted status
            instance.accept()
            logger.info(f"Friend request accepted: {instance}")
            return Response({"detail": "Friend request accepted, friendship created."})

        return super().update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        logger.info(f"Deleting friend request: {instance}")
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
            raise serializers.ValidationError("You do not have permission to unfriend "
                                              "this user.")

        logger.info(f"Deleting friendship: {instance}")
        # If the user is involved in the friendship, allow deletion (unfriending)
        self.perform_destroy(instance)
        return Response({"detail": "Unfriended successfully."})
