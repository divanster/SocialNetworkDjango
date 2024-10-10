# backend/social/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet

app_name = 'social'

router = DefaultRouter()
router.register(r'', PostViewSet, basename='post')

urlpatterns = [
    path('', include(router.urls)),
]
