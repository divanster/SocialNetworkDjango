# backend/friends/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FriendRequestViewSet, FriendshipViewSet
from users.views import UserProfileViewSet

app_name = 'friends'

router = DefaultRouter()
router.register(r'friend-requests', FriendRequestViewSet, basename='friend-request')
router.register(r'friendships', FriendshipViewSet, basename='friendship')
router.register(r'user-profiles', UserProfileViewSet, basename='user-profile')

urlpatterns = [
    path('', include(router.urls)),
]
