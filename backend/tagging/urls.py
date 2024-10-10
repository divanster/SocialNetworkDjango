# backend/tagging/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaggedItemViewSet

app_name = 'tagging'

router = DefaultRouter()
router.register(r'', TaggedItemViewSet, basename='user-tag')

urlpatterns = [
    path('', include(router.urls)),
]
