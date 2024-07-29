# backend/friends/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FriendRequestViewSet, FriendshipViewSet

router = DefaultRouter()
router.register(r'friend-requests', FriendRequestViewSet)
router.register(r'friendships', FriendshipViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
