# backend/albums/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlbumViewSet, PhotoViewSet

app_name = 'albums'  # Adding an app name for namespacing

# Create the DefaultRouter for automatically generated routes
router = DefaultRouter()
router.register(r'albums', AlbumViewSet, basename='album')
router.register(r'photos', PhotoViewSet, basename='photo')

urlpatterns = [
    path('', include(router.urls)),
]
