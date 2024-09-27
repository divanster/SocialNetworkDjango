# users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, UserProfileViewSet, CustomUserSignupView

# Initialize the router
router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='customuser')
router.register(r'profile', UserProfileViewSet, basename='userprofile')

app_name = 'users'  # Set the namespace

urlpatterns = [
    path('', include(router.urls)),  # Include router's URLs

    # Custom route for retrieving UserProfile by UUID
    path('profile/<uuid:id>/', UserProfileViewSet.as_view({'get': 'retrieve'}),
         name='userprofile-detail'),  # UUID-based profile detail

    # Custom path for the current user view (me)
    path('me/', CustomUserViewSet.as_view({'get': 'me', 'put': 'me', 'patch': 'me'}), name='customuser-me'),

    # Include the signup path
    path('signup/', CustomUserSignupView.as_view(), name='customuser-signup'),

    # Include Djoser's JWT URLs for authentication
    path('jwt/', include('djoser.urls.jwt')),  # Moved to a specific subpath to avoid conflicts
]
