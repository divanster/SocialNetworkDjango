from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Album, Photo
from .serializers import AlbumSerializer, PhotoSerializer
from .tasks import process_new_album  # Import the Celery task


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        album = serializer.save(user=self.request.user)
        # Trigger the Celery task after the album is created
        process_new_album.delay(album.id)  # Execute the task asynchronously


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        album = Album.objects.get(pk=self.request.data.get('album'))
        serializer.save(album=album)
