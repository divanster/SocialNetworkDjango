# backend/social/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, RatingViewSet, TagViewSet, PostImageViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'ratings', RatingViewSet)
router.register(r'tags', TagViewSet)
router.register(r'post-images', PostImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
