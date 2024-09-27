from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, UserProfileViewSet

# Initialize the router
router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='customuser')
router.register(r'profile', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('', include(router.urls)),  # Include router's URLs

    # Custom route for retrieving UserProfile by UUID
    path('profile/<uuid:id>/', UserProfileViewSet.as_view({'get': 'retrieve'}),
         name='profile-detail'),  # UUID-based profile detail

    # Custom path for the current user view (me)
    path('users/me/', CustomUserViewSet.as_view({'get': 'me', 'put': 'me', 'patch': 'me'}), name='customuser-me'),

    # Include Djoser's JWT URLs for authentication
    path('', include('djoser.urls.jwt')),
]
