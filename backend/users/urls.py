# backend/users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, UserProfileViewSet, CustomUserSignupView, CustomTokenRefreshView  # Rename the custom refresh view
from rest_framework_simplejwt.views import TokenRefreshView  # Use the default JWT TokenRefreshView

app_name = 'users'  # Set the namespace

router = DefaultRouter()
router.register(r'', CustomUserViewSet, basename='customuser')
router.register(r'profile', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    # JWT Token Refresh endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', include(router.urls)),  # Include router's URLs

    # Custom route for retrieving UserProfile by UUID
    path('profile/<uuid:id>/', UserProfileViewSet.as_view({'get': 'retrieve'}), name='userprofile-detail'),

    # # Custom path for the current user view (me)
    # path('me/', CustomUserViewSet.as_view({'get': 'me', 'put': 'me', 'patch': 'me'}), name='customuser-me'),

    # Include the signup path
    path('signup/', CustomUserSignupView.as_view(), name='customuser-signup'),

    # Include Djoser's JWT URLs for authentication
    path('jwt/', include('djoser.urls.jwt')),  # Moved to a specific subpath to avoid conflicts

    # Include custom token refresh endpoint if needed
    path('custom-token-refresh/', CustomTokenRefreshView.as_view(), name='custom_token_refresh'),
]
