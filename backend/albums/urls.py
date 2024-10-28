# backend/albums/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlbumViewSet, PhotoViewSet

app_name = 'albums'  # Adding an app name for URL namespacing, which is useful in templates or reverse lookups

# Create the DefaultRouter for automatically generated routes
router = DefaultRouter()
router.register(r'albums', AlbumViewSet, basename='album')  # Register AlbumViewSet with a basename of 'album'
router.register(r'photos', PhotoViewSet, basename='photo')  # Register PhotoViewSet with a basename of 'photo'

# Define urlpatterns for the albums app
urlpatterns = [
    path('', include(router.urls)),  # Include all of the routes managed by DefaultRouter
]
