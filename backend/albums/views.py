# backend/albums/views.py

from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from albums.album_models import Album  # Import Album from album_models
from albums.photo_models import Photo  # Import Photo from photo_models
from .serializers import AlbumSerializer, PhotoSerializer
import logging

logger = logging.getLogger(__name__)


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.using('social_db').all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        album = serializer.save(user=self.request.user)
        logger.info(f"Album created with ID {album.id} by user {self.request.user.id}")

    def perform_update(self, serializer):
        album = self.get_object()
        if album.user != self.request.user:
            logger.warning(
                f"Unauthorized update attempt by user {self.request.user.id} on album {album.id}")
            raise permissions.PermissionDenied(
                "You do not have permission to edit this album.")

        updated_album = serializer.save()
        logger.info(
            f"Album with ID {updated_album.id} updated by user {self.request.user.id}")

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            logger.warning(
                f"Unauthorized delete attempt by user {self.request.user.id} on album {instance.id}")
            raise permissions.PermissionDenied(
                "You do not have permission to delete this album.")

        logger.info(
            f"Album with ID {instance.id} deleted by user {self.request.user.id}")
        instance.delete()


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.using('social_db').all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        album = serializer.validated_data['album']
        if album.user != self.request.user:
            logger.warning(
                f"Unauthorized photo creation attempt by user {self.request.user.id} on album {album.id}")
            raise permissions.PermissionDenied(
                "You do not have permission to add photos to this album.")

        photo = serializer.save()
        logger.info(
            f"Photo created with ID {photo.id} in album {album.id} by user {self.request.user.id}")

    def perform_update(self, serializer):
        photo = self.get_object()
        if photo.album.user != self.request.user:
            logger.warning(
                f"Unauthorized update attempt by user {self.request.user.id} on photo {photo.id}")
            raise permissions.PermissionDenied(
                "You do not have permission to edit this photo.")

        updated_photo = serializer.save()
        logger.info(
            f"Photo with ID {updated_photo.id} updated by user {self.request.user.id}")

    def perform_destroy(self, instance):
        if instance.album.user != self.request.user:
            logger.warning(
                f"Unauthorized delete attempt by user {self.request.user.id} on photo {instance.id}")
            raise permissions.PermissionDenied(
                "You do not have permission to delete this photo.")

        logger.info(
            f"Photo with ID {instance.id} deleted by user {self.request.user.id}")
        instance.delete()
