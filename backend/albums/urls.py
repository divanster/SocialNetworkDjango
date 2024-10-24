# backend/albums/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlbumViewSet, PhotoViewSet

app_name = 'albums'  # Adding an app name for namespacing

# Create the DefaultRouter for automatically generated routes
router = DefaultRouter()
router.register(r'albums', AlbumViewSet, basename='album')  # Register AlbumViewSet
router.register(r'photos', PhotoViewSet, basename='photo')  # Register PhotoViewSet

# Include the automatically generated routes
urlpatterns = [
    path('', include(router.urls)),  # Include all of the routes managed by DefaultRouter
]
