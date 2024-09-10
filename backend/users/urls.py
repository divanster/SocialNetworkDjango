from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, UserProfileViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'profile', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),  # Include the router's URLs
    path('users/me/', CustomUserViewSet.as_view({'get': 'me'}), name='users-me'),
    # Custom endpoint for the "me" action
    path('', include('djoser.urls.jwt')),  # Include only the JWT URLs from Djoser
]
