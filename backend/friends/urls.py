from rest_framework.routers import DefaultRouter
from .views import FriendRequestViewSet, FriendshipViewSet

router = DefaultRouter()

# Add the basename explicitly
router.register(r'friend-requests', FriendRequestViewSet, basename='friend-request')
router.register(r'friendships', FriendshipViewSet, basename='friendship')

urlpatterns = router.urls
