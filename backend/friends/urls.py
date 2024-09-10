from rest_framework.routers import DefaultRouter
from .views import FriendRequestViewSet, FriendshipViewSet
from users.views import UserProfileViewSet

router = DefaultRouter()

# Add the basename explicitly
router.register(r'friend-requests', FriendRequestViewSet, basename='friend-request')
router.register(r'friendships', FriendshipViewSet, basename='friendship')
router.register(r'user-profiles', UserProfileViewSet, basename='user-profile')

urlpatterns = router.urls
