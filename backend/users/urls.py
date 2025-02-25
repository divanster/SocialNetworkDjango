# backend/users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, UserProfileViewSet, CustomUserSignupView, CustomTokenRefreshView, get_online_users
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'users'

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='customuser')  # Use specific prefix
router.register(r'profiles', UserProfileViewSet, basename='userprofile')  # Use specific prefix

urlpatterns = [
    # Online usersa
    path('get_online_users/', get_online_users, name='get_online_users'),

    # JWT Token Refresh endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Custom path for the current user view (me)
    path('me/', CustomUserViewSet.as_view({'get': 'me', 'put': 'me', 'patch': 'me'}), name='customuser-me'),

    # Include router's URLs
    path('', include(router.urls)),

    # Include the signup path
    path('signup/', CustomUserSignupView.as_view(), name='customuser-signup'),

    # Include Djoser's JWT URLs for authentication
    path('jwt/', include('djoser.urls.jwt')),

    # Include custom token refresh endpoint if needed
    path('custom-token-refresh/', CustomTokenRefreshView.as_view(), name='custom_token_refresh'),
]
