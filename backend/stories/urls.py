# backend/stories/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StoryViewSet

app_name = 'stories'

router = DefaultRouter()
router.register(r'', StoryViewSet, basename='story')

urlpatterns = [
    path('', include(router.urls)),
]
