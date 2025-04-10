# backend/users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, UserProfileViewSet, CustomUserSignupView, \
    CustomTokenRefreshView, get_online_users, logout_view
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'users'

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='customuser')  # Register the User view set
router.register(r'profiles', UserProfileViewSet, basename='userprofile')  # Register the UserProfile view set

urlpatterns = [
    # Online users
    path('get_online_users/', get_online_users, name='get_online_users'),

    # JWT Token Refresh endpoint (via SimpleJWT)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Custom path for the current user view (me)
    path('me/', CustomUserViewSet.as_view({'get': 'me', 'put': 'me', 'patch': 'me'}), name='customuser-me'),

    # Include router's URLs for the default routes (users and profiles)
    path('', include(router.urls)),

    # Custom signup route (you have the custom signup view)
    path('signup/', CustomUserSignupView.as_view(), name='customuser-signup'),

    # Include Djoser's JWT URLs for authentication (these are default paths)
    path('jwt/', include('djoser.urls.jwt')),

    # Optionally include a custom token refresh endpoint (if needed)
    path('custom-token-refresh/', CustomTokenRefreshView.as_view(), name='custom_token_refresh'),

    path('logout/', logout_view, name='logout'),
]
