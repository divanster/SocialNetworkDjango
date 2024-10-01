from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Album, Photo
from .serializers import AlbumSerializer, PhotoSerializer
from .tasks import process_new_album


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        album = serializer.save(user=self.request.user)
        process_new_album.delay(album.id)  # Execute the task asynchronously

    def perform_update(self, serializer):
        serializer.save()


class PhotoViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing photos.
    """
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
