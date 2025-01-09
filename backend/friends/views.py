from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .models import FriendRequest, Friendship, Block
from .serializers import FriendRequestSerializer, FriendshipSerializer, BlockSerializer
from rest_framework.exceptions import PermissionDenied, ValidationError
import logging

# Initialize logging
logger = logging.getLogger(__name__)


class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        """
        Restrict the queryset to friend requests where the user is either the sender or receiver
        and not soft-deleted.
        """
        user = self.request.user
        return FriendRequest.objects.filter(
            Q(sender=user) | Q(receiver=user),
            is_deleted=False  # Exclude soft-deleted records
        )

    def perform_create(self, serializer):
        """
        Automatically set the sender to the authenticated user.
        """
        try:
            instance = serializer.save()
            logger.info(f"Friend request created: {instance}")
        except serializers.ValidationError as e:
            logger.error(f"Validation error during friend request creation: {e}")
            raise e
        except Exception as ex:
            logger.error(f"Error during friend request creation: {ex}")
            raise serializers.ValidationError({'detail': 'An unexpected error occurred.'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def accept(self, request, id=None):
        """
        Custom action to accept a friend request.
        """
        friend_request = self.get_object()

        if friend_request.receiver != request.user:
            logger.warning(
                f"User {request.user.id} attempted to accept a friend request not addressed to them."
            )
            return Response(
                {"detail": "You do not have permission to accept this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        if friend_request.status != FriendRequest.Status.PENDING:
            logger.warning(
                f"User {request.user.id} attempted to accept a non-pending friend request."
            )
            return Response(
                {"detail": "This friend request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                friend_request.accept()
                logger.info(f"Friend request accepted: {friend_request}")

            return Response(
                {"detail": "Friend request accepted, friendship created."},
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            logger.error(f"Validation error while accepting friend request: {e}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as ex:
            logger.error(f"Error while accepting friend request: {ex}")
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reject(self, request, id=None):
        """
        Custom action to reject a friend request.
        """
        friend_request = self.get_object()

        if friend_request.receiver != request.user:
            logger.warning(
                f"User {request.user.id} attempted to reject a friend request not addressed to them."
            )
            return Response(
                {"detail": "You do not have permission to reject this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        if friend_request.status != FriendRequest.Status.PENDING:
            logger.warning(
                f"User {request.user.id} attempted to reject a non-pending friend request."
            )
            return Response(
                {"detail": "This friend request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                friend_request.reject()
                logger.info(f"Friend request rejected: {friend_request}")

            return Response(
                {"detail": "Friend request rejected."},
                status=status.HTTP_200_OK
            )
        except Exception as ex:
            logger.error(f"Error while rejecting friend request: {ex}")
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_destroy(self, instance):
        """
        Allow both sender and receiver to soft-delete a friend request.
        """
        user = self.request.user
        if instance.sender != user and instance.receiver != user:
            logger.warning(
                f"User {user.id} attempted to delete a friend request they are not involved in."
            )
            raise PermissionDenied("You do not have permission to delete this friend request.")

        instance.delete()  # Soft delete
        logger.info(f"Friend request soft-deleted: {instance}")


class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        """
        Restrict the queryset to friendships where the user is either user1 or user2
        and not soft-deleted.
        """
        user = self.request.user
        return Friendship.objects.filter(
            Q(user1=user) | Q(user2=user),
            is_deleted=False  # Exclude soft-deleted records
        )

    def destroy(self, request, *args, **kwargs):
        """
        Allow users to unfriend by soft-deleting the friendship.
        """
        instance = self.get_object()

        if instance.user1 != request.user and instance.user2 != request.user:
            logger.warning(
                f"User {request.user.id} attempted to unfriend without being part of the friendship."
            )
            raise PermissionDenied("You do not have permission to unfriend this user.")

        try:
            with transaction.atomic():
                instance.delete()  # Soft delete
                logger.info(f"Friendship soft-deleted: {instance}")

            return Response(
                {"detail": "Unfriended successfully."},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as ex:
            logger.error(f"Error while deleting friendship: {ex}")
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BlockViewSet(viewsets.ModelViewSet):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        """
        Restrict the queryset to blocks initiated by the authenticated user
        and not soft-deleted.
        """
        user = self.request.user
        return Block.objects.filter(
            blocker=user,
            is_deleted=False  # Exclude soft-deleted records
        )

    def perform_destroy(self, instance):
        """
        Allow users to unblock by soft-deleting the block.
        """
        user = self.request.user
        if instance.blocker != user:
            logger.warning(
                f"User {user.id} attempted to delete a block they did not initiate."
            )
            raise PermissionDenied("You do not have permission to unblock this user.")

        instance.delete()  # Soft delete
        logger.info(f"Block soft-deleted: {instance}")
