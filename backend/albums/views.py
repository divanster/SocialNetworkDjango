from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Album, Photo
from .serializers import AlbumSerializer, PhotoSerializer
import logging

logger = logging.getLogger(__name__)


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.using('social_db').all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        # Validate that the user has the permission to create an album
        if not self.request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Save the album with the user who is creating it
        album = serializer.save(user=self.request.user)

        logger.info(f"Album created with ID {album.id} by user {self.request.user.id}")

    def perform_update(self, serializer):
        # Make sure the user is the owner of the album before updating
        album = self.get_object()
        if album.user != self.request.user:
            logger.warning(f"Unauthorized update attempt by user {self.request.user.id} on album {album.id}")
            raise permissions.PermissionDenied("You do not have permission to edit this album.")

        # Save updated data
        updated_album = serializer.save()

        logger.info(f"Album with ID {updated_album.id} updated by user {self.request.user.id}")

    def perform_destroy(self, instance):
        # Make sure the user is the owner of the album before deleting
        if instance.user != self.request.user:
            logger.warning(f"Unauthorized delete attempt by user {self.request.user.id} on album {instance.id}")
            raise permissions.PermissionDenied("You do not have permission to delete this album.")

        # Perform deletion
        logger.info(f"Album with ID {instance.id} deleted by user {self.request.user.id}")
        instance.delete()


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.using('social_db').all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        # Check if the user has permissions to add photos to an album
        album = serializer.validated_data['album']
        if album.user != self.request.user:
            logger.warning(f"Unauthorized photo creation attempt by user {self.request.user.id} on album {album.id}")
            raise permissions.PermissionDenied("You do not have permission to add photos to this album.")

        # Save the photo to the specified album
        photo = serializer.save()
        logger.info(f"Photo created with ID {photo.id} in album {album.id} by user {self.request.user.id}")

    def perform_update(self, serializer):
        # Ensure user owns the photo they are updating
        photo = self.get_object()
        if photo.album.user != self.request.user:
            logger.warning(f"Unauthorized update attempt by user {self.request.user.id} on photo {photo.id}")
            raise permissions.PermissionDenied("You do not have permission to edit this photo.")

        # Save updated photo data
        updated_photo = serializer.save()
        logger.info(f"Photo with ID {updated_photo.id} updated by user {self.request.user.id}")

    def perform_destroy(self, instance):
        # Ensure user owns the photo they are deleting
        if instance.album.user != self.request.user:
            logger.warning(f"Unauthorized delete attempt by user {self.request.user.id} on photo {instance.id}")
            raise permissions.PermissionDenied("You do not have permission to delete this photo.")

        # Perform deletion
        logger.info(f"Photo with ID {instance.id} deleted by user {self.request.user.id}")
        instance.delete()
